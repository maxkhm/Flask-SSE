from flask import render_template
import flask
import queue


class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


announcer = MessageAnnouncer()
app = flask.Flask(__name__)


def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ping/<data>')
def ping(data):
    msg = format_sse(data=str(data))
    announcer.announce(msg=msg)
    return {}, 200


@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = announcer.listen()
        while True:
            msg = messages.get()
            yield msg

    return flask.Response(stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run("0.0.0.0")
