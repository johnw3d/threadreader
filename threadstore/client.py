#  client.py  - threadreader's client interface to the threadstore
#
#   ThreadReader constructs a tree of collections to store feed info & items, in the form:
#
#       threadreader.<user>.feeds.<type>.feedname
#
#   the collection object for a feed stores metadata about the feed, the items
#   are posts within the feed's collection
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'john'

import logging

from threadclient.client import ThreadStore, ItemNotFound
from threadclient.tornado_client import AsyncThreadStore

log = logging.getLogger('threadstore.client')

class ThreadStoreClient(object):
    "threadreader's threadstore client"

    _instance = None  # singleton instance

    def __init__(self, host='', port=8888, client_settings={}, request_settings={}):
        self.host = host
        self.port = port
        self.client_settings = client_settings
        self.request_settings = request_settings
        self.blocking_threadstore = None
        """@type : threadclient.tornado_client.ThreadStore"""
        self.threadstore = None
        """@type : threadclient.tornado_client.AsyncThreadStore"""

    @classmethod
    def open(cls, host='', port=8888, client_settings={}, request_settings={}):
        "instantiate threadstoreclient singleton"
        # establishes both blocking and async connections
        ThreadStoreClient._instance = tsc = cls(host, port, client_settings, request_settings)
        tsc.blocking_threadstore = ThreadStore(host, port)
        tsc.threadstore = AsyncThreadStore(host,
                                           port,
                                           client_settings, request_settings)
        return tsc

    @classmethod
    def instance(cls):
        """return ThreadStoreClient singleton
           :rtype : ThreadStoreClient"""
        return ThreadStoreClient._instance

    def close(self):
        "close threadstore connection"
        pass

    def init_reader_threadstore(self):
        "clear threadstore threadreader collections, recreate & set up indexes, etc."
        ts = self.blocking_threadstore
        # delete all posts in the threadreader collection subspace
        ts.delete_posts('threadreader')
        # delete all subspace collectiobs of threadreader
        collections = ts.collection_directory('threadreader', structured=False).get('_collections')
        if collections:
            for c in collections:
                if c != 'threadory':
                    ts.delete_collection(c)

    def build_test_db(self):
        "build test feeds"
        test_feeds = [
            dict(
                feed_url="http://feeds.kottke.org/main",
                collection='threadreader.feeds.blog.kottke',
                feed_tag="blog.kottke",
                tags=[],
            ),
            dict(
                feed_url="http://daringfireball.net/feeds/main",
                collection='threadreader.feeds.blog.daringfireball',
                feed_tag="blog.daringfireball",
                tags=[],
            )
        ]
        # load test feeds
        from feeds.readers import RSSReader
        for tf in test_feeds:
            RSSReader(**tf).update()

