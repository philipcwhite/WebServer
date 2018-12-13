from wserver import app, web_handle

class controller(object):
    def index(self, args):
        resp = """<html>
        <body>
        <h2>Index</h2>
        Session ID:<br />""" + self.session_id + """</body>
        </html>"""
        return resp
    def home(self, args):
        resp = """<html>
        <body>
        <h2>Home</h2>
        </body>
        </html>"""
        return resp

app.start(controller)
