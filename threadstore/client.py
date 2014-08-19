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

from threadclient.tornado_client import AsyncThreadStore, BlockingThreadStore, ThreadStore

from feeds.readers import RSSReader

class ThreadStoreClient(object):
    "threadreader's threadstore client"

    def __init__(self, host='', port=8888, client_settings={}, request_settings={}):
        self.host = host
        self.port = port
        self.client_settings = client_settings
        self.request_settings = request_settings
        self.blocking_threadstore = None
        self.threadstore = None

    def open(self):
        "open threadstore connection"
        # establishes both blocking and async connections
        self.blocking_threadstore = BlockingThreadStore(self.host,
                                        self.port,
                                        self.client_settings, self.request_settings)
        self.threadstore = AsyncThreadStore(self.host,
                                        self.port,
                                        self.client_settings, self.request_settings)

    def close(self):
        "close threadstore connection"
        pass

    def init_reader_threadstore(self):
        "clear threadstore threadreader collections, recreate & set up indexes, etc."
        ts = self.blocking_threadstore
        ts.delete_collection('threadreader')

        for c in ts.
        for c in ts.search_collections(query={'_name_index': 'threadreader'}, projection=['_name', '_id']).get('items',[]):



        for c in self.collections:
            ts.delete_collection(c['name'])
            ts.create_collection(c['name'])


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
        for tf in test_feeds:
            RSSReader(**tf).update()

