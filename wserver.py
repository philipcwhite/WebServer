import asyncio
import ssl
import uuid
import datetime
import time

class web_vars:
    def __init__(self, arguments, cookie, extention, length, method, path, session_id):
        self.arguments = arguments
        self.cookie = cookie
        self.extention = extention
        self.length = length
        self.method = method
        self.path = path
        self.session_id = session_id
        
class app_vars:
    def __init__(self, controller, ssl_enabled):
        self.controller = controller
        self.ssl_enabled = ssl_enabled

class web_request:
    def get_headers(request):
        # Process Request Headers
        # Store parts of request as variables
        web_vars.arguments = ""
        web_vars.cookie = ""
        web_vars.extention =""
        web_vars.path = ""
        web_vars.method = ""
        web_vars.session_id = ''
        
        request_list = []
        request_list = request.split("\n")
        web_vars.method = request_list[0].split(" ")[0]
        web_vars.path = request_list[0].split(" ")[1]
        if '.' in web_vars.path:
            web_vars.extention = web_vars.path.split('.')[1]
        else:
            web_vars.extention = 'html'
        web_vars.arguments = request_list[-1]
        for i in request_list:
            if "Cookie:" in i: 
                web_vars.cookie = i.replace("Cookie: ","")
                web_vars.session_id = web_vars.cookie.split(';')[0].replace('session_id=','')

        print("METHOD:" + web_vars.method)
        print("PATH:" + web_vars.path)
        print("EXT:" + web_vars.extention)
        print("COOKIE:" + web_vars.cookie)
        print("ARGUMENTS:" + web_vars.arguments)
        print("SESSION_ID:" + web_vars.session_id)
        print("")

    def get_cookie():
        pass

class web_response:
    def set_cookie():
        if web_vars.cookie == "":
            web_vars.session_id = str(uuid.uuid1())
            lease = 3600  # In seconds
            end = time.localtime(time.time() + lease)
            expire = time.strftime('%a, %d-%b-%Y %T GMT', end)
            cookie = 'Set-Cookie: session_id=' + web_vars.session_id + ';expires=' + expire + '\r\n'
            return cookie

    def set_headers():
        content = {'css':'text/css',
                        'html': 'text/html',
                        'ico': 'image/x-icon',
                        'jpg': 'image/jpg',
                        'png': 'image/png'}

        http_status =  "HTTP/1.1 200 OK\r\n"
        content_type = 'Content-Type: ' + content[web_vars.extention] + " \r\n"
        server_date = "Date: " + str(datetime.datetime.now()) + "\r\n"
        server_name = "Server: Custom\r\n"
        content_length = "Content-Length: " + web_vars.length + " \r\n"
        cookie = web_response.set_cookie()
        if cookie is None: cookie = ''
        accept_range = ''
        if 'image' in content[web_vars.extention]: 
            accept_range = 'Accept-Ranges: bytes\r\n'
            head = http_status + content_type + accept_range + '\r\n'
            return head.encode()
        else:
            head = http_status + content_type + server_date + server_name + content_length + cookie + "\r\n\r\n"
            return head.encode()    

    def static(url):
        url=url[1:]
        if not 'static' in url: url = 'static/' + url
        f = open(url, "rb")
        obj = f.read()
        web_vars.length=str(len(obj))
        head = web_response.set_headers()
        resp = head + obj
        return resp

class web_handle(asyncio.Protocol):
    def connection_made(self, transport):
        #peername = transport.get_extra_info('peername')
        self.transport = transport

    def data_received(self, data):
        message = data.decode('utf-8', 'ignore')
        # Parse headers, route request, return data
        web_request.get_headers(message)

        # Check to see if loop should end
        #loop = asyncio.get_running_loop()
        #loop.call_soon_threadsafe(loop.stop)

        if "/favicon.ico" in web_vars.path:
            self.transport.write(web_response.static(web_vars.path))
        if "/static/" in web_vars.path:
            self.transport.write(web_response.static(web_vars.path))

        for i in dir(app_vars.controller):
            if not "__" in i:
                if web_vars.path == "/" and i=="index":
                    func = getattr(app_vars.controller,i)
                    proc=func(web_vars.arguments)
                    web_vars.length=str(len(proc))
                    head = web_response.set_headers()
                    resp_msg = head + proc.encode()
                    self.transport.write(resp_msg)
                if i == web_vars.path.replace("/",""):
                    func = getattr(app_vars.controller,i)
                    proc=func(web_vars.arguments)
                    web_vars.length=str(len(proc))
                    head = web_response.set_headers()
                    resp_msg = head + proc.encode()
                    self.transport.write(resp_msg)
        self.transport.close()
        
class web_server():
    async def connection_loop():
        cert_path = "C:\\Users\\philwhite\\Documents\\Python\\webserver\\test\\"
        cert_name = "localhost.crt"
        cert_key = "localhost.pem"
        server_ip = "0.0.0.0"
        server_port = 9999
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.options |= ssl.PROTOCOL_TLSv1_2
        #ssl_context.options |= ssl.PROTOCOL_SSLv23
        #ssl_context.set_ciphers('DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:ECDHE-ECDSA-AES128-GCM-SHA256')
        ssl_context.load_cert_chain(certfile = cert_path + cert_name, keyfile = cert_path + cert_key)
        loop = asyncio.get_running_loop()
        if app_vars.ssl_enabled == True:
            server = await loop.create_server(lambda: web_handle(), server_ip, server_port, ssl=ssl_context)
        else:
            server = await loop.create_server(lambda: web_handle(), server_ip, server_port)
        async with server: await server.serve_forever()
        
class app:
    def start(controller):
        app_vars.controller = controller
        app_vars.ssl_enabled = True
        try:
            asyncio.run(web_server.connection_loop())
        except:
            pass