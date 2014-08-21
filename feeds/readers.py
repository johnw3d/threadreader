#  readers.py - feed readers - generate threadreader item posts from RSS feeds
#
# TODO: factor this out into a separate feeds module for other apps to use
# TODO: need an async Tornado version
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

from threadstore.client import ThreadStoreClient, ItemNotFound

class BaseReader(object):
    "base feed reader"
    pass

class RSSReader(BaseReader):
    "reader for RSS feeds"

    def __init__(self, feed_url='', collection='', feed_tag='', tags=[]):
        self.feed_url = feed_url
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
        ts = ThreadStoreClient.instance().blocking_threadstore  # TODO: make async
        # build or update feed collection
        try:
            col_id = ts.get_collection(self.collection)['_id']
        except ItemNotFound:
            col_id = ts.create_collection(self.collection, user='@johnw')['_id']
        ts.update_collection(dict(_id=col_id,
                                  title=feed['title'],
                                  subtitle=feed['subtitle'],
                                  updated=feed['updated'],
                                  ))
        # add feed entries
        for e in feed['entry']:
            post = {
                "type": "atom.feed.html",
                "title": e['title'],
                "published": e['published'],
                "author": dict(e['author']),
                "body": dict(e['content']),
            }
            ts.create_post(col_id, user='@johnw', body=post, tags=self.tags + ['feed.%s' % self.feed_tag])


  # <title>Daring Fireball</title>
  # <subtitle>By John Gruber</subtitle>
  # <link rel="alternate" type="text/html" href="http://daringfireball.net/"/>
  # <link rel="self" type="application/atom+xml" href="http://daringfireball.net/feeds/main"/>
  # <id>http://daringfireball.net/feeds/main</id>
  # <updated>2014-08-17T22:35:04Z</updated>
  # <rights>Copyright © 2014, John Gruber</rights>

  # <entry>
  #   <title>‘Humans Need Not Apply’</title>
  #   <link rel="alternate" type="text/html" href="http://kottke.org/14/08/humans-need-not-apply"/>
  #   <link rel="shorturl" type="text/html" href="http://df4.us/n1x"/>
  #   <link rel="related" type="text/html" href="http://daringfireball.net/linked/2014/08/16/humans-need-not-apply"/>
  #   <id>tag:daringfireball.net,2014:/linked//6.29877</id>
  #   <published>2014-08-16T19:51:40Z</published>
  #   <updated>2014-08-17T22:35:04Z</updated>
  #   <author>
  #     <name>John Gruber</name>
  #     <uri>http://daringfireball.net/</uri>
  #   </author>
  #   <content type="html" xml:base="http://daringfireball.net/linked/" xml:lang="en"><![CDATA[
