import logging
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen

from threadstore.client import ThreadStoreClient
from feeds.readers import RSSReader

log = logging.getLogger('handlers.home')

class BaseHandler(tornado.web.RequestHandler):
    "base threadreader request handler"

    pass

class TemplateUtils(object):
    "a namespace for threadreader template utilities (some may factor out at some point)"

    def directory_tree(self, dir):
        "render given directory as nested <ul><li> HTML"
        def _render_level(subdir, path='', indent='  '):
            if subdir:
                ul = indent + '<ul>\n'
                if isinstance(subdir, dict):
                    for k, v in subdir.items():
                        ul += indent + '  <li><span><i class="tree-folder fa fa-minus-square-o"></i><span tag="%s">%s</span></span>\n' %  (path + k, k)
                        ul += _render_level(v, path + k + '.', indent + '    ')
                        ul += indent + '  </li>\n'
                elif isinstance(subdir, list):
                    for v in subdir:
                        ul += indent + '  <li><span tag="%s">%s</span>\n' % (path + v, v)
                        ul += indent + '  </li>\n'
                return ul + indent + '</ul>\n'
            else:
                return ''

        ul = _render_level(dir)
        return '<div class="tree">\n' + ul + '</div>'

    def format_date(self, date):
        "reformats datestamp"
        return date

    def item_html(self, item):
        "extract RSS item HTML"
        return item['body']

utils = TemplateUtils()

class HomeHandler(BaseHandler):

    def get(self):
        # supply structured tag directory for threadreader subspace posts
        tag_dir = ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory('threadreader', filter=r'\.')
        self.render('index.html', dir=tag_dir, utils=utils)


class ThreadListHandler(BaseHandler):

    def get(self, tag):
        thread = ThreadStoreClient.instance().blocking_threadstore.thread(tag, 'threadreader', sort=[{"published": -1}])
        if thread:
            self.render('threadlist.html', thread=thread['items'], utils=utils)


class AddFeedHandler(BaseHandler):

    def get(self):
        self.render('addfeed.html', utils=utils)

    def post(self):
        # add new feed, repull & return updated tag directory
        url = self.get_body_argument('url')
        if not url.startswith('http://'):
            url = 'http://' + url
        tags = self.get_body_argument('tags')
        tags = list(map(str.strip, tags.split(',')))
        # load feed
        RSSReader(feed_url=url, tags=tags, user='@johnw').update()
        # pull & return updated tag directory
        tag_dir = ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory('threadreader', filter=r'\.')
        self.render('directory_tree.html', dir=tag_dir, utils=utils)



