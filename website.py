from web.server import app
from web.templates import render

class controller(object):
    def index(self):
        user = self.get_auth()
        response = render('index.html', username=user)
        return response

    def login(self, username=None, password=None):
        if username is None: return render('login.html')
        elif username == 'admin' and password == 'test':
                self.login(username)
                self.redirect('/')
        else: return render('error.html')

    def logout(self):
        self.logout(self.get_user())
        self.redirect('/login')

app.start(controller)
