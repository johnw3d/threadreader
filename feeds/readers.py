#  readers.py - feed readers - generate threadreader item posts from RSS feeds
#
# TODO: factor this out into a separate feeds module for other apps to use
# TODO: need an async Tornado version for prod
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import xmltodict
import urllib.request, urllib.error, urllib.parse
import re
import dateutil.parser

from bs4 import BeautifulSoup

from threadstore.client import ThreadStoreClient, ItemNotFound, ThreadStore

class BaseReader(object):
    "base feed reader"
    pass

class RSSReader(BaseReader):
    "reader for RSS feeds"

    def __init__(self, feed_url='', collection='', feed_tag='', tags=[], user='@johnw'):  #TODO: insist on user
        self.feed_url = feed_url
        self.collection = collection
        self.feed_tag = feed_tag
        self.tags = tags or []
        self.user = user

    def _create_feed(self, posts, title='', subtitle='', updated=None):
        # connect to threadstore
        ts = ThreadStoreClient.instance().blocking_threadstore  # TODO: make async
        title = ThreadStore.tag_escape(title)
        if not self.collection:
            # construct feed collection name
            self.collection = 'threadreader.feeds.%s.%s' % (self.user, title)
        # construct feed tag, for now just escaped title if not supplied
        if not self.feed_tag:
            self.feed_tag = 'feed:' + title
        self.tags.append(self.feed_tag)
        # build or update feed collection
        try:
            col_id = ts.get_collection(self.collection)['_id']
        except ItemNotFound:
            col_id = ts.create_collection(self.collection, user=self.user)['_id']
        ts.update_collection(dict(_id=col_id,
                                  title=title,
                                  subtitle=subtitle,
                                  feed_tag=self.feed_tag,
                                  updated=dateutil.parser.parse(updated) if updated else None,
                                  ))
        # TODO: get & cache favicon.ico
        # add feed entry posts
        for post in posts:
            ts.create_post(col_id, user='@johnw', body=post, tags=self.tags)

    def update(self):
        "polls feed for an update"
        # TODO: get & cache favicon.ico
        # get & parse feed
        feed = self._get_feed_xml()
        if feed:
            if 'feed' in feed:
                # Atom format feed
                feed = feed['feed']
                # construct feed entry posts & add feed
                posts = [{
                        "type": "atom.feed.html",
                        "title": e['title'],
                        "published": dateutil.parser.parse(e['published']),
                        "author": dict(e['author']),
                        "body": self._clean_html(e['content']['#text']),
                    } for e in feed['entry']]
                self._create_feed(posts, feed['title'], feed['subtitle'], feed['updated'])
            elif 'rss' in feed:
                # RSS format feed
                feed = feed['rss']['channel']
                # construct feed entry posts & add feed
                posts = [{
                        "type": "rss.feed.html",
                        "title": e['title'],
                        "published": dateutil.parser.parse(e['pubDate']),
                        "author": e.get('dc:creator'),
                        "body": self._clean_html(e.get('content:encoded', e.get('description'))),
                    } for e in feed['item']]
                self._create_feed(posts, feed['title'], feed['description'], feed.get('lastBuildDate'))
        return self

    feed_type_pat = re.compile(r'^(application/rss\+xml|application/rdf\+xml|application/atom\+xml|application/xml|text/xml).*')

    def _get_feed_xml(self, recursing=False):
        "locate an RSS feed at given URL, via <link alternate> header if needed in a normal html web page"
        # get & parse response from initially-given feed URL
        try:
            response = urllib.request.urlopen(self.feed_url)
        except urllib.error.HTTPError as e:
            return None
        ct = response.getheader("Content-Type", '')
        doc = response.read()
        if not recursing and ct.startswith('text/html'):
            # got HTML, maybe home page, check for link alternates of right type in head
            soup = BeautifulSoup(doc)
            feed_link = soup.find('link', rel="alternate", type=self.feed_type_pat)
            if feed_link:
                # found possible feed alternate
                alt_href = feed_link.get('href')
                if alt_href:
                    # update feed url & try again (but allow only one indirection)
                    self.feed_url = urllib.parse.urljoin(self.feed_url, alt_href)
                    return self._get_feed_xml(recursing=True)
        elif self.feed_type_pat.match(ct) and doc:
            # we have putative feed xml, parse it
            return xmltodict.parse(doc)

    def _clean_html(self, html):
        "cleans scripts & other bad stuff from feed item body HTML"
        return html.replace('<script>', '<!--script>').replace('<script ', '<!--script ').replace('</script>', '</script-->')

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


    # # RSS
    #
    # <?xml version="1.0" encoding="UTF-8"?>
    # <?xml-stylesheet type="text/xsl" media="screen" href="/~d/styles/rss2full.xsl"?>
    # <?xml-stylesheet type="text/css" media="screen" href="http://feeds.arstechnica.com/~d/styles/itemcontent.css"?>
    # <rss xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:slash="http://purl.org/rss/1.0/modules/slash/" xmlns:feedburner="http://rssnamespace.org/feedburner/ext/1.0" version="2.0">
    #   <channel>
    #     <title>Ars Technica</title>
    #     <link>http://arstechnica.com</link>
    #     <description>The Art of Technology</description>
    #     <lastBuildDate>Sat, 23 Aug 2014 20:04:43 +0000</lastBuildDate>
    #     <language>en-US</language>
    #     <sy:updatePeriod>hourly</sy:updatePeriod>
    #     <sy:updateFrequency>1</sy:updateFrequency>
    #     <generator>http://wordpress.org/?v=3.9.2</generator>
    #     <atom10:link xmlns:atom10="http://www.w3.org/2005/Atom" rel="self" type="application/rss+xml" href="http://feeds.arstechnica.com/arstechnica/index"/>
    #     <feedburner:info uri="arstechnica/index"/>
    #     <atom10:link xmlns:atom10="http://www.w3.org/2005/Atom" rel="hub" href="http://pubsubhubbub.appspot.com/"/>
    #     <item>
    #       <title>CarPlay introductions quietly slip back into 2015</title>
    #       <link>http://feeds.arstechnica.com/~r/arstechnica/index/~3/rEgK8RENCzY/</link>
    #       <comments>http://arstechnica.com/cars/2014/08/carplay-introductions-quietly-slip-back-into-2015/#comments</comments>
    #       <pubDate>Sat, 23 Aug 2014 19:30:14 +0000</pubDate>
    #       <dc:creator><![CDATA[Jonathan M. Gitlin]]></dc:creator>
    #       <category><![CDATA[Cars Technica]]></category>
    #       <category><![CDATA[Infinite Loop]]></category>
    #       <guid isPermaLink="false">http://arstechnica.com/?p=524263</guid>
    #       <description><![CDATA[Car makers push back in-car iOS until next year]]></description>
    #       <content:encoded><![CDATA[<div id="rss-wrap">
    # <div>
    #       <img src="http://cdn.arstechnica.net/wp-content/uploads/2014/08/CarPlay3-640x256.jpg">
    # </div>
    #  <p>CarPlay, Apple’s in-car iOS integration product, has shown up in flashy demos at various trade shows this year, but it will take a while before we see it on the roads, according to Lucas Mearian at <em><a href="http://www.computerworld.com/s/article/9250581/Carmakers_put_Apple_s_CarPlay_in_the_slow_lane">Computerworld</a></em>. Mercedes-Benz, Volvo, and Honda are all believed to be pushing back plans to include CarPlay in some of their new models until 2015.</p>
    # <p>Apple’s influence on the automotive industry may have been unintentional at first, but the arrival of the iPod created an <a href="http://arstechnica.com/cars/2014/06/the-past-present-and-future-of-in-car-infotainment/">infotainment paradigm shift</a>. iPod owners wanted their MP3 players to connect to their cars. Less than a decade later and even the cheapest rental car now comes with a plethora of USB ports and wireless options for piping one’s tunes through the car’s speakers. CarPlay is an evolution of this approach, moving the display from the mobile device to the car’s center stack, as well as integrating Siri into the infotainment system.</p>
    # <p>An Apple-created solution, (potentially) free of the kludginess that often comes with third-party systems may help sell cars to the 42 percent of American smartphone users who have iOS, but equally might do little to attract their Android-using counterparts, who outnumber them 5 to 4 domestically and by quite a considerable margin worldwide.</p>
    # </div><p><a href="http://arstechnica.com/cars/2014/08/carplay-introductions-quietly-slip-back-into-2015/#p3">Read 1 remaining paragraphs</a> | <a href="http://arstechnica.com/cars/2014/08/carplay-introductions-quietly-slip-back-into-2015/?comments=1">Comments</a></p><div class="feedflare">
    # <a href="http://feeds.arstechnica.com/~ff/arstechnica/index?a=rEgK8RENCzY:YQcmha30iwQ:V_sGLiPBpWU"><img src="http://feeds.feedburner.com/~ff/arstechnica/index?i=rEgK8RENCzY:YQcmha30iwQ:V_sGLiPBpWU" border="0"></img></a> <a href="http://feeds.arstechnica.com/~ff/arstechnica/index?a=rEgK8RENCzY:YQcmha30iwQ:F7zBnMyn0Lo"><img src="http://feeds.feedburner.com/~ff/arstechnica/index?i=rEgK8RENCzY:YQcmha30iwQ:F7zBnMyn0Lo" border="0"></img></a> <a href="http://feeds.arstechnica.com/~ff/arstechnica/index?a=rEgK8RENCzY:YQcmha30iwQ:qj6IDK7rITs"><img src="http://feeds.feedburner.com/~ff/arstechnica/index?d=qj6IDK7rITs" border="0"></img></a> <a href="http://feeds.arstechnica.com/~ff/arstechnica/index?a=rEgK8RENCzY:YQcmha30iwQ:yIl2AUoC8zA"><img src="http://feeds.feedburner.com/~ff/arstechnica/index?d=yIl2AUoC8zA" border="0"></img></a>
    # </div><img src="http://feeds.feedburner.com/~r/arstechnica/index/~4/rEgK8RENCzY" height="1" width="1"/>]]></content:encoded>
    #       <wfw:commentRss>http://arstechnica.com/cars/2014/08/carplay-introductions-quietly-slip-back-into-2015/feed/</wfw:commentRss>
    #       <slash:comments>0</slash:comments>
    #       <feedburner:origLink>http://arstechnica.com/cars/2014/08/carplay-introductions-quietly-slip-back-into-2015/</feedburner:origLink>
    #     </item>
    #
