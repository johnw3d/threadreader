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

def directory_tree(dir):
    "render given directory as nested <ul><li> HTML"
    def _render_level(subdir, indent='  '):
        if subdir:
            ul = indent + '<ul>\n'
            if isinstance(subdir, dict):
                for k, v in subdir.items():
                    ul += indent + '  <li><span><i class="tree-folder fa fa-minus-square-o"></i>%s</span>\n' % k
                    ul += _render_level(v, indent + '    ')
                    ul += indent + '  </li>\n'
            elif isinstance(subdir, list):
                for v in subdir:
                    ul += indent + '  <li><span>%s</span>\n' % v
                    ul += indent + '  </li>\n'
            return ul + indent + '</ul>\n'
        else:
            return ''

    ul = _render_level(dir)
    return '<div class="tree">\n' + ul + '</div>'

class HomeHandler(BaseHandler):

    def get(self):
        tag_dir = ThreadStoreClient.instance().blocking_threadstore.posts_tag_directory('threadreader', filter=r'\.')
        self.render('index.html', foo=str(tag_dir), dir=tag_dir, directory_tree=directory_tree)

