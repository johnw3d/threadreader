import logging
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.gen

from threadstore.client import ThreadStoreClient

log = logging.getLogger('handlers.home')

class BaseHandler(tornado.web.RequestHandler):
    "base threadreader request handler"

    pass

class TemplateUtils(object):

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

utils = TemplateUtils()

class HomeHandler(BaseHandler):

    def get(self):
        tag_dir = ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory('threadreader', filter=r'\.')
        self.render('index.html', foo=str(tag_dir), dir=tag_dir, utils=utils)


class ThreadListHandler(BaseHandler):

    def get(self, tag):
        thread = ThreadStoreClient.instance().blocking_threadstore.thread(tag, 'threadreader', sort=[{"published": -1}])
        if thread:
            self.render('threadlist.html', thread=thread['items'], utils=utils)
