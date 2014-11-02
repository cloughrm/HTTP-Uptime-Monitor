import os
import json
import time
import tornadio
import tornado.web
import tornadio.router
import tornadio.server
from feedformatter import Feed

FIStatusSockets = []
banks = json.loads(open('banks.json').read())
rss_items = []


class FIStatusHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('fi_status.html', banks=banks.keys())

    def post(self):

        # Make sure its a valid request
        if not self.get_argument('key'):
            return
        if self.get_argument('key') != '':
            return

        # Create our response object
        res = {
            'name': self.get_argument('name'),
            'status': self.get_argument('status')
        }

        # Add status to RSS items
        rss_items.insert(0, {
            'title': res['name'],
            'description': res['status'],
            'pubDate': time.localtime()
        })
        if len(rss_items) > 100:
            rss_items.pop()

        # Get previous states
        previous_status = banks[res['name']]['previous_status']
        alarm_status = banks[res['name']]['alarm_status']

        # If the current status does not match the previous status, then we have inconclusive results, skip it
        if previous_status != res['status']:
            banks[res['name']]['previous_status'] = res['status']
            return

        # Send data to dashboard
        if res['status'] == 'RED' and alarm_status == 'OFF':
            banks[res['name']]['alarm_status'] = 'ON'
            res['alarm'] = 'ON'
            for client in FIStatusSockets:
                try:
                    client.send(json.dumps(res))
                except:
                    FIStatusSockets.remove(client)

        elif res['status'] == 'RED' and alarm_status == 'ON':
            res['alarm'] = 'OFF'
            for client in FIStatusSockets:
                try:
                    client.send(json.dumps(res))
                except:
                    FIStatusSockets.remove(client)

        else:
            banks[res['name']]['alarm_status'] = 'OFF'
            res['alarm'] = 'OFF'
            for client in FIStatusSockets:
                try:
                    client.send(json.dumps(res))
                except:
                    FIStatusSockets.remove(client)


class FIStatusSocketConnection(tornadio.SocketConnection):
    def on_open(self, *args, **kwargs):
        FIStatusSockets.append(self)
        for bank, meta in banks.iteritems():
            res = {
                'name': bank,
                'status': meta['previous_status'],
                'alarm': meta['alarm_status']
            }
            self.send(json.dumps(res))

    def on_message(self, message):
        pass

    def on_close(self):
        FIStatusSockets.remove(self)


class RSSHandler(tornado.web.RequestHandler):
    def get(self):
        # Create the feed
        feed = Feed()

        # Set the feed/channel level properties
        feed.feed["title"] = "pkt.li"
        feed.feed["author"] = "pkt.li"
        feed.feed["link"] = "http://pkt.li/banks/rss"

        # Create items and add to the feed
        for item in rss_items:
            feed.items.append(item)

        # Print the feed to stdout in various formats
        self.content_type = 'application/atom+xml'
        self.write(feed.format_atom_string())

if __name__ == '__main__':
    settings = {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    }
    FIStatusRouter = tornadio.get_router(FIStatusSocketConnection, {
        'enabled_protocols': ['websocket', 'xhr-multipart', 'xhr-polling']
    }, resource='fistatus')
    app = tornado.web.Application([
        (r'favicon.ico', tornado.web.StaticFileHandler),
        (r'/fistatus', FIStatusHandler),
        FIStatusRouter.route(),
        (r'/rss', RSSHandler),
    ], socket_io_port=8000, debug=True, **settings)
    tornadio.server.SocketServer(app)
