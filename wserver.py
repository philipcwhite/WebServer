import asyncio
import ssl
import uuid
import datetime


class app_vars:
    server_ip = '0.0.0.0'
    server_port = 9999
    ssl_enabled = False
    cert_path = './'
    cert_name = 'localhost.crt'
    cert_key = 'localhost.pem'

class session:
    session_list = []
    def __init__(self, session_id, session_user, session_expire):
        self.session_id = session_id
        self.session_user = session_user
        self.session_expire = session_expire

class web_handle(asyncio.Protocol):
    session_id = None
    get_cookie = None
    set_cookie = None
    controller = None
    arguments = None
    extention = None
    length = None
    method = None
    path = None
    content_dict = {'css': 'text/css',
                    'gif': 'image/gif',
                    'htm': 'text/html',
                    'html': 'text/html',
                    'jpeg': 'image/jpeg',
                    'jpg': 'image/jpg',
                    'js': 'text/javascript',
                    'ico': 'image/x-icon',
                    'png': 'image/png',
                    'text': 'text/plain',
                    'txt': 'text/plain'}

    def cookie(self, key = None, value = None, expires = None):
        # Set session cookie
        if self.get_cookie is None:
        #if not 'session_id' in self.get_cookie:
            self.session_id = str(uuid.uuid1())
            expire = str(3600)
            if not self.set_cookie is None:
                self.set_cookie += 'Set-Cookie: session_id=' + self.session_id + '; max-age=' + expire + '; path=/ \r\n'
            else:
                self.set_cookie = 'Set-Cookie: session_id=' + self.session_id + '; max-age=' + expire + '; path=/ \r\n'
        # Set other cookies

    def login(self, username):
        user=session(self.session_id, username, datetime.datetime.now())
        session.session_list.append(user)

    def logout(self, username):
        for i, o in enumerate(session.session_list):
            if o.session_user == username:
                del session.session_list[i]
                break
        self.set_cookie = 'Set-Cookie: session_id=' + self.session_id + '; max-age=0; path=/ \r\n'

    def user(self):
        user = None
        for i in session.session_list:
            if i.session_id == self.session_id:
                user = i.session_user
        if not user is None:
            return user
        else:
            return 'Not Authorized'

    def get_headers(self, request):
        request_list = []
        request_list = request.split("\n")
        self.method = request_list[0].split(" ")[0]
        self.path = request_list[0].split(" ")[1]
        if '.' in self.path:
            self.extention = self.path.split('.')[1]
        else:
            self.extention = 'html'
        self.arguments = request_list[-1]
        for i in request_list:
            if 'Cookie:' in i: 
                self.get_cookie = i.replace("Cookie: ","")
                session_id = self.get_cookie.split(';')[0].replace('session_id=','')
                if not session_id == '':
                    self.session_id = session_id
        print('METHOD:' + self.method)
        print('PATH:' + self.path)
        print('EXT:' + self.extention)
        print('ARGUMENTS:' + self.arguments)
        if not self.get_cookie is None:
            print('COOKIE:' + self.get_cookie)
            print('SESSION_ID:' + self.session_id)

        print('')

    def set_headers(self):
        http_status =  'HTTP/1.1 200 OK\r\n'
        content_type = 'Content-Type: ' + self.content_dict[self.extention] + ' \r\n'
        server_date = 'Date: ' + str(datetime.datetime.now()) + '\r\n'
        server_name = 'Server: Custom\r\n'
        content_length = 'Content-Length: ' + self.length + '\r\n'
        accept_range = ''

        if 'image' in self.content_dict[self.extention]: 
            accept_range = 'Accept-Ranges: bytes\r\n'
            head = http_status + content_type + accept_range + '\r\n'
            return head.encode()
        else:
            self.cookie()
            cookie_text = ''
            if not self.set_cookie is None: cookie_text = self.set_cookie
            head = http_status + content_type + server_date + server_name + content_length + cookie_text + '\r\n'
            return head.encode()  
  
    def call_controller(self):        
        args = []
        parsed_url = self.path.split('?')
        path1 = parsed_url[0]
        path_func = path1.split('/')[1]
        if path_func is '':path_func='index'
        for i in dir(self.controller):
            if not "__" in i:
                if i == path_func:
                    for x in path1.split('/'):
                        if not x is '': 
                            args.append(x)
                    if args:
                        del args[0]
                    if '?' in self.path:
                        args1 = parsed_url[1].split('&')
                        for x in args1:
                            args.append(x.split('=')[1])
                    self.arguments = args
                    func = getattr(self.controller, i)
                    proc = None
                    if args:
                        proc = func(self, *args)
                    else:
                        proc = func(self)
                    self.length=str(len(proc))
                    head = self.set_headers()
                    resp_msg = head + proc.encode()
                    return resp_msg

    def call_static(self):
        if '/favicon.ico' in self.path or '/static/' in self.path:
            url=self.path[1:]
            if 'favicon.ico' in url: url = 'static/favicon.ico'
            f = open(url, "rb")
            obj = f.read()
            self.length=str(len(obj))
            head = self.set_headers()
            resp = head + obj
            return resp

    def connection_made(self, transport):
        #peername = transport.get_extra_info('peername')
        self.transport = transport

    def data_received(self, data):
        
        message = data.decode('utf-8', 'ignore')
        # Parse headers, route request, return data
        self.get_headers(message)

        # Check to see if loop should end
        #loop = asyncio.get_running_loop()
        #loop.call_soon_threadsafe(loop.stop)

        reply = None
        reply = self.call_static()
        #reply = self.call_controller()
        if reply is None: reply = self.call_controller()
        self.transport.write(reply)               
        self.transport.close()
        
class web_server():
    async def connection_loop():
        loop = asyncio.get_running_loop()
        if app_vars.ssl_enabled == True:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.options |= ssl.PROTOCOL_TLSv1_2
            ssl_context.load_cert_chain(certfile = app_vars.cert_path + app_vars.cert_name, keyfile = app_vars.cert_path + app_vars.cert_key)
            server = await loop.create_server(lambda: web_handle(), app_vars.server_ip, app_vars.server_port, ssl=ssl_context)
        else:
            server = await loop.create_server(lambda: web_handle(), app_vars.server_ip, app_vars.server_port)
        async with server: await server.serve_forever()
        
class app:
    def start(controller):
        web_handle.controller = controller
        app_vars.ssl_enabled = False
        try:
            asyncio.run(web_server.connection_loop())
        except:
            pass
