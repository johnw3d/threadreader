import logging
import datetime

import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen

from threadstore.client import ThreadStoreClient
from feeds.readers import RSSReader

log = logging.getLogger('handlers.home')

class BaseHandler(tornado.web.RequestHandler):
    "base threadreader request handler"

    def _get_tags_dir(self):
        "get an up-to-date structured tag directory for all threadreader collections"
        return ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory(collection='threadreader.feeds',
                                                                                     counts=True,
                                                                                     filter={"$not":{"$regex": r'tagging|taggedBy'}})
    def _get_feeds_dir(self):
        "get an up-to-date structured feed directory for all threadreader collections"
        return ThreadStoreClient.instance().blocking_threadstore.posts_collection_directory(collection='threadreader.feeds',
                                                                                     counts=True)


class TemplateUtils(object):
    "a namespace for threadreader template utilities (some may factor out at some point)"

    def directory_tree(self, dir, new_feed=None):
        "render given directory as nested <ul><li> HTML"
        def _render_level(subdir, path='', indent='  '):
            if subdir:
                folder_icon = "fa-plus-square-o" if path == '' else "fa-plus-square-o"
                hidden = 'style="display: none;"' if path != '' else ''
                ul = indent + '<ul>\n'
                if isinstance(subdir, dict):
                    for k in sorted(subdir.keys(), key=str.lower):
                        if k:
                            v = subdir[k]
                            count = v.pop('_count')  # TODO: handle case when no counts pulled, will have empty leafs and leaf lists
                            item = '<span tag="%s">%s</span> <span class="item-count">%s</span></span>' % (path + k, k, count)
                            if v:
                                ul += indent + '  <li %s><span class="folder-item"><i class="tree-folder fa %s"></i>%s</span>\n' % (hidden, folder_icon, item)
                                ul += _render_level(v, path + k + ('.' if k[-1] != ':' else ''), indent + '    ')
                            else:
                                ul += indent + '  <li %s>%s\n' % (hidden, item)
                            ul += indent + '  </li>\n'
                elif isinstance(subdir, list):
                    for v in sorted(subdir, key=str.lower):
                        ul += indent + '  <li %s><span tag="%s">%s</span>\n' % (hidden, path + v, v)
                        ul += indent + '  </li>\n'
                return ul + indent + '</ul>\n'
            else:
                return ''

        ul = _render_level(dir)
        new_feed_attr = ('new_feed="%s"' % new_feed) if new_feed else ''
        return '<div class="tree" %s>\n%s</div>' %  (new_feed_attr, ul)

    def format_date(self, date):
        "reformats datestamp"
        return date

    def elapsedSinceDateTime(self, date_time):
        "gens display form of elapsed time since date until now"
        now = datetime.datetime.now(datetime.timezone.utc)
        dt = now - date_time
        if dt.days:
            return ('%d days' % dt.days) if dt.days > 1 else '1 day'
        else:
            minutes = dt.seconds / 60
            if minutes < 60:
                return ('%d minutes' % minutes) if minutes > 1 else '1 minute'
            else:
                hours = minutes / 60
                return ('%d hours' % hours) if hours > 1 else '< 1 hour'

    def item_html(self, item):
        "extract RSS item HTML"
        return item['body']

utils = TemplateUtils()

class HomeHandler(BaseHandler):

    def get(self):
        # supply structured tag directory for threadreader subspace posts
        tag_dir = self._get_tags_dir()
        self.render('index.html', dir=tag_dir, new_feed=None, utils=utils)

class ThreadListHandler(BaseHandler):

    def get(self, tag):
        thread = ThreadStoreClient.instance().blocking_threadstore.thread(tag, 'threadreader', sort=[{"published": -1}])
        if thread:
            self.render('threadlist.html', thread=thread['items'], utils=utils)


class AddFeedHandler(BaseHandler):

    def get(self):
        self.render('addfeed.html', utils=utils)

    def post(self):
        "add new feed, repull & return updated tag directory"
        url = self.get_body_argument('url')
        if not url.startswith('http://'):
            url = 'http://' + url
        tags = self.get_body_argument('tags')
        tags = list(map(str.strip, tags.split(',')))
        # load feed
        feed = RSSReader(feed_url=url, tags=tags, user='@johnw').update()
        # pull & return updated tag directory
        tag_dir = self._get_tags_dir()
        self.render('directory_tree.html', dir=tag_dir, new_feed='feed' + feed.feed_tag, utils=utils)


class ItemTagHandler(BaseHandler):

    def post(self, item):
        "add tqgs to given item"
        tags = self.get_body_argument('tags')
        tags = list(map(str.strip, tags.split(',')))
        ThreadStoreClient.instance().blocking_threadstore.update_tags(item, user='@johnw', add_tags=tags)
        # pull & return updated tag directory
        tag_dir = self._get_tags_dir()
        self.render('directory_tree.html', dir=tag_dir, new_feed=None, utils=utils)
