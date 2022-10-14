import os
import sys
import logging

from wsgiref.simple_server import make_server, WSGIRequestHandler

import ankisyncd
import ankisyncd.config
from ankisyncd.sync_app import SyncApp
from ankisyncd.thread import shutdown

logger = logging.getLogger("ankisyncd")

if __package__ is None and not hasattr(sys, "frozen"):
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


class RequestHandler(WSGIRequestHandler):
    logger = logging.getLogger("ankisyncd.http")

    def log_error(self, format, *args):
        self.logger.error("%s %s", self.address_string(), format % args)

    def log_message(self, format, *args):
        self.logger.info("%s %s", self.address_string(), format % args)


def main():
    logging.basicConfig(
        level=logging.INFO, format="[%(asctime)s]:%(levelname)s:%(name)s:%(message)s"
    )
    logger.info(
        "ankisyncd {} ({})".format(ankisyncd._get_version(), ankisyncd._homepage)
    )

    if len(sys.argv) > 1:
        # backwards compat
        config = ankisyncd.config.load(sys.argv[1])
    else:
        config = ankisyncd.config.load()

    ankiserver = SyncApp(config)
    httpd = make_server(
        config["host"], int(config["port"]), ankiserver, handler_class=RequestHandler
    )

    try:
        logger.info("Serving HTTP on {} port {}...".format(*httpd.server_address))
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        shutdown()


if __name__ == "__main__":
    main()
