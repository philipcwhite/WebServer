from wserver import app, web_vars

class controller(object):
    def index(args):
        resp = """<html>
        <body>
        <h2>Index</h2>
        Session ID:<br />""" + web_vars.session_id + """</body>
        </html>"""
        return resp
    def home(args):
        resp = """<html>
        <body>
        <h2>Home</h2>
        </body>
        </html>"""
        return resp

app.start(controller)
