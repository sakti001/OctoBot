#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains the Dispatcher class."""

import logging
import weakref
from functools import wraps
from threading import Thread, Lock, Event, current_thread, BoundedSemaphore
from time import sleep
from uuid import uuid4
from collections import defaultdict

from queue import Queue, Empty

from future.builtins import range

from telegram import TelegramError
from telegram.ext.handler import Handler
from telegram.utils.promise import Promise

logging.getLogger(__name__).addHandler(logging.NullHandler())
DEFAULT_GROUP = 0


def run_async(func):
    """Function decorator that will run the function in a new thread.

    Will run :attr:`telegram.ext.Dispatcher.run_async`.

    Using this decorator is only possible when only a single Dispatcher exist in the system.

    Note: Use this decorator to run handlers asynchronously.

    """
    @wraps(func)
    def async_func(*args, **kwargs):
        return Dispatcher.get_instance().run_async(func, *args, **kwargs)

    return async_func


class DispatcherHandlerStop(Exception):
    """Raise this in handler to prevent execution any other handler (even in different group)."""
    pass


class UnlockedDispatcher(object):
    """This class dispatches all kinds of updates to its registered handlers.

    Attributes:
        bot (:class:`telegram.Bot`): The bot object that should be passed to the handlers.
        update_queue (:obj:`Queue`): The synchronized queue that will contain the updates.
        job_queue (:class:`telegram.ext.JobQueue`): Optional. The :class:`telegram.ext.JobQueue`
            instance to pass onto handler callbacks.
        workers (:obj:`int`): Number of maximum concurrent worker threads for the ``@run_async``
            decorator.

    Args:
        bot (:class:`telegram.Bot`): The bot object that should be passed to the handlers.
        update_queue (:obj:`Queue`): The synchronized queue that will contain the updates.
        job_queue (:class:`telegram.ext.JobQueue`, optional): The :class:`telegram.ext.JobQueue`
                instance to pass onto handler callbacks.
        workers (:obj:`int`, optional): Number of maximum concurrent worker threads for the
            ``@run_async`` decorator. defaults to 4.

    """

    __singleton_lock = Lock()
    __singleton_semaphore = BoundedSemaphore()
    __singleton = None
    logger = logging.getLogger(__name__)

    def __init__(self, bot, update_queue, workers=4, exception_event=None, job_queue=None):
        self.bot = bot
        self.update_queue = update_queue
        self.job_queue = job_queue
        self.workers = workers

        self.user_data = defaultdict(dict)
        """:obj:`dict`: A dictionary handlers can use to store data for the user."""
        self.chat_data = defaultdict(dict)
        """:obj:`dict`: A dictionary handlers can use to store data for the chat."""
        self.handlers = {}
        """Dict[:obj:`int`, List[:class:`telegram.ext.Handler`]]: Holds the handlers per group."""
        self.groups = []
        """List[:obj:`int`]: A list with all groups."""
        self.error_handlers = []
        """List[:obj:`callable`]: A list of errorHandlers."""

        self.running = False
        """:obj:`bool`: Indicates if this dispatcher is running."""
        self.__stop_event = Event()
        self.__exception_event = exception_event or Event()
        self.__async_queue = Queue()
        self.__async_threads = set()

        # For backward compatibility, we allow a "singleton" mode for the dispatcher. When there's
        # only one instance of Dispatcher, it will be possible to use the `run_async` decorator.
        with self.__singleton_lock:
            if self.__singleton_semaphore.acquire(blocking=0):
                self._set_singleton(self)
            else:
                self._set_singleton(None)

    def _init_async_threads(self, base_name, workers):
        base_name = '{}_'.format(base_name) if base_name else ''

        for i in range(workers):
            thread = Thread(target=self._pooled, name='{}{}'.format(base_name, i))
            self.__async_threads.add(thread)
            thread.start()

    @classmethod
    def _set_singleton(cls, val):
        cls.logger.debug('Setting singleton dispatcher as %s', val)
        cls.__singleton = weakref.ref(val) if val else None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of this class.

        Returns:
            :class:`telegram.ext.Dispatcher`

        Raises:
            RuntimeError

        """
        if cls.__singleton is not None:
            return cls.__singleton()
        else:
            return
            raise RuntimeError('{} not initialized or multiple instances exist'.format(
                cls.__name__))

    def _pooled(self):
        thr_name = current_thread().getName()
        while 1:
            promise = self.__async_queue.get()

            # If unpacking fails, the thread pool is being closed from Updater._join_async_threads
            if not isinstance(promise, Promise):
                self.logger.debug("Closing run_async thread %s/%d", thr_name,
                                  len(self.__async_threads))
                break

            promise.run()
            if isinstance(promise.exception, DispatcherHandlerStop):
                self.logger.warning(
                    'DispatcherHandlerStop is not supported with async functions; func: %s',
                    promise.pooled_function.__name__)

    def run_async(self, func, *args, **kwargs):
        """Queue a function (with given args/kwargs) to be run asynchronously.

        Args:
            func (:obj:`callable`): The function to run in the thread.
            *args (:obj:`tuple`, optional): Arguments to `func`.
            **kwargs (:obj:`dict`, optional): Keyword arguments to `func`.

        Returns:
            Promise

        """
        # TODO: handle exception in async threads
        #       set a threading.Event to notify caller thread
        promise = Promise(func, args, kwargs)
        self.__async_queue.put(promise)
        return promise

    def start(self):
        """Thread target of thread 'dispatcher'.

        Runs in background and processes the update queue.

        """
        if self.running:
            self.logger.warning('already running')
            return

        if self.__exception_event.is_set():
            msg = 'reusing dispatcher after exception event is forbidden'
            self.logger.error(msg)
            raise TelegramError(msg)

        self._init_async_threads(uuid4(), self.workers)
        self.running = True
        self.logger.debug('Dispatcher started')

        while 1:
            try:
                # Pop update from update queue.
                update = self.update_queue.get(True, 1)
            except Empty:
                if self.__stop_event.is_set():
                    self.logger.debug('orderly stopping')
                    break
                elif self.__exception_event.is_set():
                    self.logger.critical('stopping due to exception in another thread')
                    os.kill(os.getpid(),9)
                    break
                continue

            self.logger.debug('Processing Update: %s' % update)
            self.process_update(update)

        self.running = False
        self.logger.debug('Dispatcher thread stopped')

    def stop(self):
        """Stops the thread."""
        if self.running:
            self.__stop_event.set()
            while self.running:
                sleep(0.1)
            self.__stop_event.clear()

        # async threads must be join()ed only after the dispatcher thread was joined,
        # otherwise we can still have new async threads dispatched
        threads = list(self.__async_threads)
        total = len(threads)

        # Stop all threads in the thread pool by put()ting one non-tuple per thread
        for i in range(total):
            self.__async_queue.put(None)

        for i, thr in enumerate(threads):
            self.logger.debug('Waiting for async thread {0}/{1} to end'.format(i + 1, total))
            thr.join()
            self.__async_threads.remove(thr)
            self.logger.debug('async thread {0}/{1} has ended'.format(i + 1, total))

    @property
    def has_running_threads(self):
        return self.running or bool(self.__async_threads)

    def process_update(self, update):
        """Processes a single update.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | :class:`telegram.TelegramError`):
                The update to process.

        """
        # An error happened while polling
        if isinstance(update, TelegramError):
            try:
                self.dispatch_error(None, update)
            except Exception:
                self.logger.exception('An uncaught error was raised while handling the error')
            return

        for group in self.groups:
            try:
                for handler in (x for x in self.handlers[group] if x.check_update(update)):
                    handler.handle_update(update, self)
                    break

            # Stop processing with any other handler.
            except DispatcherHandlerStop:
                self.logger.debug('Stopping further handlers due to DispatcherHandlerStop')
                break

            # Dispatch any error.
            except TelegramError as te:
                self.logger.warning('A TelegramError was raised while processing the Update')

                try:
                    self.dispatch_error(update, te)
                except DispatcherHandlerStop:
                    self.logger.debug('Error handler stopped further handlers')
                    break
                except Exception:
                    self.logger.exception('An uncaught error was raised while handling the error')

            # Errors should not stop the thread.
            except Exception:
                self.logger.exception('An uncaught error was raised while processing the update')

    def add_handler(self, handler, group=DEFAULT_GROUP):
        """Register a handler.

        TL;DR: Order and priority counts. 0 or 1 handlers per group will be used.

        A handler must be an instance of a subclass of :class:`telegram.ext.Handler`. All handlers
        are organized in groups with a numeric value. The default group is 0. All groups will be
        evaluated for handling an update, but only 0 or 1 handler per group will be used. If
        :class:`telegram.DispatcherHandlerStop` is raised from one of the handlers, no further
        handlers (regardless of the group) will be called.

        The priority/order of handlers is determined as follows:

          * Priority of the group (lower group number == higher priority)
          * The first handler in a group which should handle an update (see
            :attr:`telegram.ext.Handler.check_update`) will be used. Other handlers from the
            group will not be used. The order in which handlers were added to the group defines the
            priority.

        Args:
            handler (:class:`telegram.ext.Handler`): A Handler instance.
            group (:obj:`int`, optional): The group identifier. Default is 0.

        """

        if not isinstance(handler, Handler):
            raise TypeError('handler is not an instance of {0}'.format(Handler.__name__))
        if not isinstance(group, int):
            raise TypeError('group is not int')

        if group not in self.handlers:
            self.handlers[group] = list()
            self.groups.append(group)
            self.groups = sorted(self.groups)

        self.handlers[group].append(handler)

    def remove_handler(self, handler, group=DEFAULT_GROUP):
        """Remove a handler from the specified group.

        Args:
            handler (:class:`telegram.ext.Handler`): A Handler instance.
            group (:obj:`object`, optional): The group identifier. Default is 0.

        """
        if handler in self.handlers[group]:
            self.handlers[group].remove(handler)
            if not self.handlers[group]:
                del self.handlers[group]
                self.groups.remove(group)

    def add_error_handler(self, callback):
        """Registers an error handler in the Dispatcher.

        Args:
            callback (:obj:`callable`): A function that takes ``Bot, Update, TelegramError`` as
                arguments.

        """
        self.error_handlers.append(callback)

    def remove_error_handler(self, callback):
        """Removes an error handler.

        Args:
            callback (:obj:`callable`): The error handler to remove.

        """
        if callback in self.error_handlers:
            self.error_handlers.remove(callback)

    def dispatch_error(self, update, error):
        """Dispatches an error.

        Args:
            update (:obj:`str` | :class:`telegram.Update` | None): The update that caused the error
            error (:class:`telegram.TelegramError`): The Telegram error that was raised.

        """
        for callback in self.error_handlers:
            callback(self.bot, update, error)

#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains the class Updater, which tries to make creating Telegram bots intuitive."""

import logging
import os
import ssl
import warnings
from threading import Thread, Lock, current_thread, Event
from time import sleep
import subprocess
from signal import signal, SIGINT, SIGTERM, SIGABRT
from queue import Queue

from telegram import Bot, TelegramError
from telegram.ext import JobQueue
from telegram.error import Unauthorized, InvalidToken, RetryAfter
from telegram.utils.request import Request
from telegram.utils.webhookhandler import (WebhookServer, WebhookHandler)

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Updater(object):
    """
    This class, which employs the :class:`telegram.ext.Dispatcher`, provides a frontend to
    :class:`telegram.Bot` to the programmer, so they can focus on coding the bot. Its purpose is to
    receive the updates from Telegram and to deliver them to said dispatcher. It also runs in a
    separate thread, so the user can interact with the bot, for example on the command line. The
    dispatcher supports handlers for different kinds of data: Updates from Telegram, basic text
    commands and even arbitrary types. The updater can be started as a polling service or, for
    production, use a webhook to receive updates. This is achieved using the WebhookServer and
    WebhookHandler classes.


    Attributes:
        bot (:class:`telegram.Bot`): The bot used with this Updater.
        user_sig_handler (:obj:`signal`): signals the updater will respond to.
        update_queue (:obj:`Queue`): Queue for the updates.
        job_queue (:class:`telegram.ext.JobQueue`): Jobqueue for the updater.
        dispatcher (:class:`telegram.ext.Dispatcher`): Dispatcher that handles the updates and
            dispatches them to the handlers.
        running (:obj:`bool`): Indicates if the updater is running.

    Args:
        token (:obj:`str`, optional): The bot's token given by the @BotFather.
        base_url (:obj:`str`, optional): Base_url for the bot.
        workers (:obj:`int`, optional): Amount of threads in the thread pool for functions
            decorated with ``@run_async``.
        bot (:class:`telegram.Bot`, optional): A pre-initialized bot instance. If a pre-initialized
            bot is used, it is the user's responsibility to create it using a `Request`
            instance with a large enough connection pool.
        user_sig_handler (:obj:`function`, optional): Takes ``signum, frame`` as positional
            arguments. This will be called when a signal is received, defaults are (SIGINT,
            SIGTERM, SIGABRT) setable with :attr:`idle`.
        request_kwargs (:obj:`dict`, optional): Keyword args to control the creation of a request
            object (ignored if `bot` argument is used).

    Note:
        You must supply either a :attr:`bot` or a :attr:`token` argument.

    Raises:
        ValueError: If both :attr:`token` and :attr:`bot` are passed or none of them.

    """

    _request = None

    def __init__(self,
                 token=None,
                 base_url=None,
                 workers=4,
                 bot=None,
                 user_sig_handler=None,
                 request_kwargs=None):

        if (token is None) and (bot is None):
            raise ValueError('`token` or `bot` must be passed')
        if (token is not None) and (bot is not None):
            raise ValueError('`token` and `bot` are mutually exclusive')

        self.logger = logging.getLogger(__name__)

        con_pool_size = workers + 4

        if bot is not None:
            self.bot = bot
            if bot.request.con_pool_size < con_pool_size:
                self.logger.warning(
                    'Connection pool of Request object is smaller than optimal value (%s)',
                    con_pool_size)
        else:
            # we need a connection pool the size of:
            # * for each of the workers
            # * 1 for Dispatcher
            # * 1 for polling Updater (even if webhook is used, we can spare a connection)
            # * 1 for JobQueue
            # * 1 for main thread
            if request_kwargs is None:
                request_kwargs = {}
            if 'con_pool_size' not in request_kwargs:
                request_kwargs['con_pool_size'] = con_pool_size
            self._request = Request(**request_kwargs)
            self.bot = Bot(token, base_url, request=self._request)
        self.user_sig_handler = user_sig_handler
        self.update_queue = Queue()
        self.job_queue = JobQueue(self.bot)
        self.__exception_event = Event()
        self.dispatcher = UnlockedDispatcher(
            self.bot,
            self.update_queue,
            job_queue=self.job_queue,
            workers=workers,
            exception_event=self.__exception_event)
        self.last_update_id = 0
        self.running = False
        self.is_idle = False
        self.httpd = None
        self.__lock = Lock()
        self.__threads = []

    def _init_thread(self, target, name, *args, **kwargs):
        thr = Thread(target=self._thread_wrapper, name=name, args=(target,) + args, kwargs=kwargs)
        thr.start()
        self.__threads.append(thr)

    def _thread_wrapper(self, target, *args, **kwargs):
        thr_name = current_thread().name
        self.logger.debug('{0} - started'.format(thr_name))
        try:
            target(*args, **kwargs)
        except Exception:
            self.__exception_event.set()
            self.logger.exception('unhandled exception')
            raise
        self.logger.debug('{0} - ended'.format(thr_name))

    def start_polling(self,
                      poll_interval=0.0,
                      timeout=10,
                      network_delay=None,
                      clean=False,
                      bootstrap_retries=0,
                      read_latency=2.,
                      allowed_updates=None):
        """Starts polling updates from Telegram.

        Args:
            poll_interval (:obj:`float`, optional): Time to wait between polling updates from
                Telegram in seconds. Default is 0.0.
            timeout (:obj:`float`, optional): Passed to :attr:`telegram.Bot.get_updates`.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting to poll. Default is False.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely
                *   0 - no retries (default)
                * > 0 - retry up to X times

            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.get_updates`.
            read_latency (:obj:`float` | :obj:`int`, optional): Grace time in seconds for receiving
                the reply from server. Will be added to the `timeout` value and used as the read
                timeout from server (Default: 2).
            network_delay: Deprecated. Will be honoured as :attr:`read_latency` for a while but
                will be removed in the future.

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """

        if network_delay is not None:
            warnings.warn('network_delay is deprecated, use read_latency instead')
            read_latency = network_delay

        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher")
                self._init_thread(self._start_polling, "updater", poll_interval, timeout,
                                  read_latency, bootstrap_retries, clean, allowed_updates)

                # Return the update queue so the main thread can insert updates
                return self.update_queue

    def start_webhook(self,
                      listen='127.0.0.1',
                      port=80,
                      url_path='',
                      cert=None,
                      key=None,
                      clean=False,
                      bootstrap_retries=0,
                      webhook_url=None,
                      allowed_updates=None):
        """
        Starts a small http server to listen for updates via webhook. If cert
        and key are not provided, the webhook will be started directly on
        http://listen:port/url_path, so SSL can be handled by another
        application. Else, the webhook will be started on
        https://listen:port/url_path

        Args:
            listen (:obj:`str`, optional): IP-Address to listen on. Default ``127.0.0.1``.
            port (:obj:`int`, optional): Port the bot should be listening on. Default ``80``.
            url_path (:obj:`str`, optional): Path inside url.
            cert (:obj:`str`, optional): Path to the SSL certificate file.
            key (:obj:`str`, optional): Path to the SSL key file.
            clean (:obj:`bool`, optional): Whether to clean any pending updates on Telegram servers
                before actually starting the webhook. Default is ``False``.
            bootstrap_retries (:obj:`int`, optional): Whether the bootstrapping phase of the
                `Updater` will retry on failures on the Telegram server.

                * < 0 - retry indefinitely
                *   0 - no retries (default)
                * > 0 - retry up to X times

            webhook_url (:obj:`str`, optional): Explicitly specify the webhook url. Useful behind
                NAT, reverse proxy, etc. Default is derived from `listen`, `port` & `url_path`.
            allowed_updates (List[:obj:`str`], optional): Passed to
                :attr:`telegram.Bot.set_webhook`.

        Returns:
            :obj:`Queue`: The update queue that can be filled from the main thread.

        """

        with self.__lock:
            if not self.running:
                self.running = True

                # Create & start threads
                self.job_queue.start()
                self._init_thread(self.dispatcher.start, "dispatcher"),
                self._init_thread(self._start_webhook, "updater", listen, port, url_path, cert,
                                  key, bootstrap_retries, clean, webhook_url, allowed_updates)

                # Return the update queue so the main thread can insert updates
                return self.update_queue

    def _start_polling(self, poll_interval, timeout, read_latency, bootstrap_retries, clean,
                       allowed_updates):
        # """
        # Thread target of thread 'updater'. Runs in background, pulls
        # updates from Telegram and inserts them in the update queue of the
        # Dispatcher.
        # """

        cur_interval = poll_interval
        self.logger.debug('Updater thread started')

        self._bootstrap(bootstrap_retries, clean=clean, webhook_url='', allowed_updates=None)

        while self.running:
            try:
                updates = self.bot.get_updates(
                    self.last_update_id,
                    timeout=timeout,
                    read_latency=read_latency,
                    allowed_updates=allowed_updates)
            except RetryAfter as e:
                self.logger.info(str(e))
                cur_interval = 0.5 + e.retry_after
            except TelegramError as te:
                self.logger.error("Error while getting Updates: {0}".format(te))

                # Put the error into the update queue and let the Dispatcher
                # broadcast it
                self.update_queue.put(te)

                cur_interval = self._increase_poll_interval(cur_interval)
            else:
                if not self.running:
                    if len(updates) > 0:
                        self.logger.debug('Updates ignored and will be pulled '
                                          'again on restart.')
                    break

                if updates:
                    for update in updates:
                        self.update_queue.put(update)
                    self.last_update_id = updates[-1].update_id + 1

                cur_interval = poll_interval

            sleep(cur_interval)

    @staticmethod
    def _increase_poll_interval(current_interval):
        # increase waiting times on subsequent errors up to 30secs
        if current_interval == 0:
            current_interval = 1
        elif current_interval < 30:
            current_interval += current_interval / 2
        elif current_interval > 30:
            current_interval = 30
        return current_interval

    def _start_webhook(self, listen, port, url_path, cert, key, bootstrap_retries, clean,
                       webhook_url, allowed_updates):
        self.logger.debug('Updater thread started')
        use_ssl = cert is not None and key is not None
        if not url_path.startswith('/'):
            url_path = '/{0}'.format(url_path)

        # Create and start server
        self.httpd = WebhookServer((listen, port), WebhookHandler, self.update_queue, url_path,
                                   self.bot)

        if use_ssl:
            self._check_ssl_cert(cert, key)

            # DO NOT CHANGE: Only set webhook if SSL is handled by library
            if not webhook_url:
                webhook_url = self._gen_webhook_url(listen, port, url_path)

            self._bootstrap(
                max_retries=bootstrap_retries,
                clean=clean,
                webhook_url=webhook_url,
                cert=open(cert, 'rb'),
                allowed_updates=allowed_updates)
        elif clean:
            self.logger.warning("cleaning updates is not supported if "
                                "SSL-termination happens elsewhere; skipping")

        self.httpd.serve_forever(poll_interval=1)

    def _check_ssl_cert(self, cert, key):
        # Check SSL-Certificate with openssl, if possible
        try:
            exit_code = subprocess.call(
                ["openssl", "x509", "-text", "-noout", "-in", cert],
                stdout=open(os.devnull, 'wb'),
                stderr=subprocess.STDOUT)
        except OSError:
            exit_code = 0
        if exit_code is 0:
            try:
                self.httpd.socket = ssl.wrap_socket(
                    self.httpd.socket, certfile=cert, keyfile=key, server_side=True)
            except ssl.SSLError as error:
                self.logger.exception('Failed to init SSL socket')
                raise TelegramError(str(error))
        else:
            raise TelegramError('SSL Certificate invalid')

    @staticmethod
    def _gen_webhook_url(listen, port, url_path):
        return 'https://{listen}:{port}{path}'.format(listen=listen, port=port, path=url_path)

    def _bootstrap(self, max_retries, clean, webhook_url, allowed_updates, cert=None):
        retries = 0
        while 1:

            try:
                if clean:
                    # Disable webhook for cleaning
                    self.bot.delete_webhook()
                    self._clean_updates()
                    sleep(1)

                self.bot.set_webhook(
                    url=webhook_url, certificate=cert, allowed_updates=allowed_updates)
            except (Unauthorized, InvalidToken):
                raise
            except TelegramError:
                msg = 'error in bootstrap phase; try={0} max_retries={1}'.format(retries,
                                                                                 max_retries)
                if max_retries < 0 or retries < max_retries:
                    self.logger.warning(msg)
                    retries += 1
                else:
                    self.logger.exception(msg)
                    raise
            else:
                break
            sleep(1)

    def _clean_updates(self):
        self.logger.debug('Cleaning updates from Telegram server')
        updates = self.bot.get_updates()
        while updates:
            updates = self.bot.get_updates(updates[-1].update_id + 1)

    def stop(self):
        """Stops the polling/webhook thread, the dispatcher and the job queue."""

        self.job_queue.stop()
        with self.__lock:
            if self.running or self.dispatcher.has_running_threads:
                self.logger.debug('Stopping Updater and Dispatcher...')

                self.running = False

                self._stop_httpd()
                self._stop_dispatcher()
                self._join_threads()

                # Stop the Request instance only if it was created by the Updater
                if self._request:
                    self._request.stop()

    def _stop_httpd(self):
        if self.httpd:
            self.logger.debug('Waiting for current webhook connection to be '
                              'closed... Send a Telegram message to the bot to exit '
                              'immediately.')
            self.httpd.shutdown()
            self.httpd = None

    def _stop_dispatcher(self):
        self.logger.debug('Requesting Dispatcher to stop...')
        self.dispatcher.stop()

    def _join_threads(self):
        for thr in self.__threads:
            self.logger.debug('Waiting for {0} thread to end'.format(thr.name))
            thr.join()
            self.logger.debug('{0} thread has ended'.format(thr.name))
        self.__threads = []

    def signal_handler(self, signum, frame):
        self.is_idle = False
        if self.running:
            self.stop()
            if self.user_sig_handler:
                self.user_sig_handler(signum, frame)
        else:
            self.logger.warning('Exiting immediately!')
            import os
            os._exit(1)

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        """Blocks until one of the signals are received and stops the updater.

        Args:
            stop_signals (:obj:`iterable`): Iterable containing signals from the signal module that
                should be subscribed to. Updater.stop() will be called on receiving one of those
                signals. Defaults to (``SIGINT``, ``SIGTERM``, ``SIGABRT``).

        """
        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.is_idle = True

        while self.is_idle:
            sleep(1)
