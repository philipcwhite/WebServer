from wserver import app, web_request
#from wserver import web_request

class controller(object):
    def index(args):
        resp = """<html>
        <body>
        <h2>Index</h2>
        Cookie:<br />""" + web_request.cookie + """</body>
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
