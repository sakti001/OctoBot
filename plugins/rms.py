"""RMS module for @SquidSan request"""
from random import choice

from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

import constants

richards = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ1nHGrYQicbml71xY2a3T82PHRiH6cIw1JfPg6H6bCuayWx3oa",
    "http://i1-news.softpedia-static.com/images/news2/Richard-Stallman-Says-He-Created-GNU-Which-Is-Called-Often-Linux-482416-2.jpg",
    "http://i.imgur.com/5fEuORU.jpg",
    "https://i.ytimg.com/vi/RZ_3MKomQzY/maxresdefault.jpg",
    "http://upload.wikimedia.org/wikipedia/commons/6/69/Richard_Stallman_by_Anders_Brenna_03.jpg",
    "http://orig11.deviantart.net/254c/f/2011/040/5/6/carta_richard_stallman_by_dominushatred-d397czl.jpg",
    "https://2ch.hk/s/arch/2016-10-23/src/1856890/14751562632760.jpg"
    "https://2ch.hk/s/arch/2016-06-04/thumb/1717751/14638466044631s.jpg",
    "https://s-media-cache-ak0.pinimg.com/originals/ff/8c/48/ff8c4804d0a415dcbcb0ce76ccc408f6.jpg",
    "https://images.encyclopediadramatica.rs/thumb/4/43/RMS.jpg/180px-RMS.jpg",
    "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSiTVXkycx2G7ICfwz4oo4Xwfg4LmjmHyTvlmmGe3sT1VhPK-Dn",
    "https://regmedia.co.uk/2012/06/12/richard_stallman.jpg?x=648&y=348&crop=1",
    "http://vgboxart.com/boxes/MOVIE/40808-the-botnet-starring-richard-stallman.jpg",
    "https://hackadaycom.files.wordpress.com/2016/01/stallman.jpg?w=800",
    "https://img.scoop.it/kvnhfnGaWu8e6vPFTBf5KTl72eJkfbmt4t8yenImKBVvK0kTmF0xjctABnaLJIm9",
    "http://24.media.tumblr.com/cd04c5996145586147412d2dbbfb917f/tumblr_mm0dxsRgvd1spxfkfo1_500.jpg",
    "http://www.mypokecard.com/en/Gallery/my/galery/PDNlAzFlsoLb.jpg",
    "https://i.ytimg.com/vi/UdfY25gDjK8/maxresdefault.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/56/Richard_Matthew_Stallman_working_on_his_Lemote_Machine.JPG",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Richard_Stallman_Conversing.jpg/295px-Richard_Stallman_Conversing.jpg",
    "http://www.chip.pl/blobimgs/2013/04/full/03776186fdde93b327c3c81e224056b6.jpeg"
]


def preload(*_):
    return


def richard(*_):
    return choice(richards), constants.PHOTO

COMMANDS = [
    {
        "command":"/rms",
        "function":richard,
        "description":"Sends photo of GNU/God",
        "inline_support": True
    }
]