#  readers.py - feed readers - generate threadreader item posts from RSS feeds
#
# TODO: factor this out into a separate feeds module for other apps to use
# TODO: need an async Tornado version
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

from app import threadstore_client

class BaseReader(object):
    "base feed reader"
    pass

class RSSReader(BaseReader):
    "reader for RSS feeds"

    def __init__(self, feed_url='', collection='', feed_tag='', tags=[]):
        self.feed_url = feed_tag
        self.collection = collection
        self.feed_tag = feed_tag
        self.tags = tags

    def update(self):
        "polls feed for an update"
        import xmltodict
        from urllib import request
        # get & parse feed
        response = request.urlopen(self.feed_url)
        feed = response.read()
        feed = xmltodict.parse(feed)['feed']
        # connect to threadstore
        ts = threadstore_client.blocking_threadstore  # TODO: make async
        # build or update feed collection
        if ts.get_collection()
        collection = feed['title']
        title = feed['subtitle']
        try:
            ts.create_collection(collection, body=dict(title=title), user='@johnw')
        except:
            pass
        # add feed entries
        for e in feed['entry']:
            post = {
                "type": "rss.feed.html",
                "title": e['title'],
                "published": e['published'],
                "body": dict(e['content']),
                "$add_tags": e['title'].split(' '),
            }
            ts.create_post(collection, user='@johnw', body=post)
