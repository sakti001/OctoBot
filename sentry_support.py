import raven
import os
import inspect

import settings

if settings.USE_SENTRY:
    sentry_client = raven.Client(settings.SENTRY_URL,
                                 refs=[{
                                     "commit": raven.fetch_git_sha(os.getcwd()),
                                     "repository": settings.SENTRY_REPO
                                 }],
                                 environment=settings.SENTRY_ENV)


def catch_exc(user_context={}, tags_context={}, extra_context={}):
    if settings.USE_SENTRY:
        sentry_client.user_context(user_context)
        sentry_client.extra_context(extra_context)
        tags_context["Exception Source"] = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
        tags_context["Environment"] = settings.SENTRY_ENV
        sentry_client.tags_context(tags_context)
        return sentry_client.captureException()

