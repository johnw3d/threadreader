#  client.py  - threadreader's client interface to the threadstore
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'john'

from threadclient.tornado_client import AsyncThreadStore, BlockingThreadStore

threadstore = None  # the threadstore client singleton

class ThreadStoreClient(object):
    "threadreader's threadstore client"

    @classmethod
    def initialize(cls, host='', port=8888, mode='async', client_settings={}, request_settings={}):
        "establish connection to threadstore, create wrapper singleton"
        client = AsyncThreadStore(host, port, client_settings, request_settings)

    global threadstore
    threadstore = AsyncThreadStore()
