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
        # TODO: get & cache favicon.ico
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
  #   <content type="html" xml:base="http://daringfireball.net/linked/" xml:lang="en"><![CDATA[]]>>


  # mime types for alternate links:
  #  RSS - application/rss+xml
  #  Atom - application/atom+xml

    # jbw-mp.bin$ curl -XHEAD -v http://daringfireball.net/feeds/main
    # * Adding handle: conn: 0x7f9831804000
    # * Adding handle: send: 0
    # * Adding handle: recv: 0
    # * Curl_addHandleToPipeline: length: 1
    # * - Conn 0 (0x7f9831804000) send_pipe: 1, recv_pipe: 0
    # * About to connect() to daringfireball.net port 80 (#0)
    # *   Trying 199.192.241.217...
    # * Connected to daringfireball.net (199.192.241.217) port 80 (#0)
    # > HEAD /feeds/main HTTP/1.1
    # > User-Agent: curl/7.30.0
    # > Host: daringfireball.net
    # > Accept: */*
    # >
    # < HTTP/1.1 200 OK
    # < Date: Sat, 23 Aug 2014 16:28:26 GMT
    # * Server Apache is not blacklisted
    # < Server: Apache
    # < Content-Location: serve.php
    # < Vary: negotiate,Accept-Encoding
    # < TCN: choice
    # < Served-By: Joyent
    # < Last-Modified: Sat, 23 Aug 2014 16:28:03 GMT
    # < ETag: "7b1a0d0d99485c7d680ceb3fd8634e74"
    # < Connection: close
    # < Content-Type: text/xml;charset=UTF-8
    # <
    # * Closing connection 0


    # jbw-mp.bin$ curl -XGET -v http://daringfireball.net/ | more
    # * Adding handle: conn: 0x7fe3f0804000
    # * Adding handle: send: 0
    # * Adding handle: recv: 0
    # * Curl_addHandleToPipeline: length: 1
    # * - Conn 0 (0x7fe3f0804000) send_pipe: 1, recv_pipe: 0
    #   % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
    #                                  Dload  Upload   Total   Spent    Left  Speed
    #   0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0* About to connect() to daringfireball.net port 80 (#0)
    # *   Trying 199.192.241.217...
    # * Connected to daringfireball.net (199.192.241.217) port 80 (#0)
    # > GET / HTTP/1.1
    # > User-Agent: curl/7.30.0
    # > Host: daringfireball.net
    # > Accept: */*
    # >
    # < HTTP/1.1 200 OK
    # < Date: Sat, 23 Aug 2014 16:32:26 GMT
    # * Server Apache is not blacklisted
    # < Server: Apache
    # < Served-By: Joyent
    # < Vary: Accept-Encoding
    # < Connection: close
    # < Transfer-Encoding: chunked
    # < Content-Type: text/html; charset=UTF-8
    # <
    # { [data not shown]
    # <!DOCTYPE html>
    # <html lang="en">
    # <head>
    #         <meta charset="UTF-8" />
    #         <title>Daring Fireball</title>
    #
    #         <meta name="viewport" content="width=600, initial-scale=0.5, minimum-scale=0.45" />     <link rel="apple-touch-icon-precomposed" href="/graphics/apple-touch-icon.png" />
    #         <link rel="shortcut icon" href="/graphics/favicon.ico?v=005" />
    #         <link rel="stylesheet" type="text/css" media="screen"  href="/css/fireball_screen.css?v1.52" />
    #         <link rel="stylesheet" type="text/css" media="screen"  href="/css/ie_sucks.php" />
    #         <link rel="stylesheet" type="text/css" media="print"   href="/css/fireball_print.css?v01" />
    #         <link rel="alternate" type="application/atom+xml" href="/feeds/main" />
    #         <script src="/js/js-global/FancyZoom.js" type="text/javascript"></script>
    #         <script src="/js/js-global/FancyZoomHTML.js" type="text/javascript"></script>
    # </head>
