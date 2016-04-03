# -*- coding: utf-8 -*-
"""Web-based CLI for rpi2caster"""

import os.path
import tornado.web
import tornado.ioloop
# This demo requires tornado_xstatic and XStatic-term.js
import tornado_xstatic

import terminado
STATIC_DIR = os.path.join(os.path.dirname(terminado.__file__), "_static")


class TerminalPageHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("/var/www/rpi2caster/termpage.html",
                           static=self.static_url,
                           xstatic=self.application.settings['xstatic_url'],
                           ws_url_path="/websocket")

if __name__ == '__main__':
    term_manager = terminado.SingleTermManager(shell_command=['rpi2caster'])
    handlers = [
                (r"/websocket", terminado.TermSocket,
                 {'term_manager': term_manager}),
                (r"/", TerminalPageHandler),
                (r"/xstatic/(.*)", tornado_xstatic.XStaticFileHandler,
                 {'allowed_modules': ['termjs']})
               ]
    xstatic_url = tornado_xstatic.url_maker('/xstatic/')
    app = tornado.web.Application(handlers, static_path=STATIC_DIR,
                                  xstatic_url=xstatic_url)
    # Serve at http://localhost:8765/ N.B. Leaving out 'localhost' here will
    # work, but it will listen on the public network interface as well.
    # Given what terminado does, that would be rather a security hole.
    app.listen(8000)
    try:
        tornado.ioloop.IOLoop.instance().start()
    finally:
        term_manager.shutdown()
