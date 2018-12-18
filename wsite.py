from wserver import app

class controller(object):
    def index(self):
        response = '''<html>
        <body>Hello World!</body>
        </html>'''
        return response

    def login(self, username=None, password=None):
        if username is None:
            response = '''<html>
            <body>
            <form action="/login" method="POST">
            Username <input type="text" name="username" /><br />
            Password <input type="password" name="password" /><br />
            <input type="submit" value="Submit" />
            </form>
            </body>
            </html>'''
            return response
        else:
            if username == 'admin' and password == 'test':
                self.login(username)
                resp='<html><body>' + username + ' logged in</body></html>'
                return resp

    def logout(self):
        self.logout(self.user())
        return 'logged out'

    def home(self):
        response = '''<html>
        <body><h1>Home</h1>''' + self.session_id + '<br />' + self.user() + '''</body>
        </html>'''
        return response

    def redirect(self):
        self.redirect('/')

app.start(controller)
