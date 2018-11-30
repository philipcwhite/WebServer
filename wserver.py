import asyncio
import ssl
import uuid
import datetime

class vars:
    def __init__(self, controller):
        self.controller = controller

class web_request:
    def __init__(self, arguments, cookie, ext, method, path):
        self.arguments = arguments
        self.cookie = cookie
        self.ext = ext
        self.method = method
        self.path = path
        
    def get_headers(request):
        # Process Request Headers
        # Store parts of request as variables
        web_request.arguments = ""
        web_request.cookie = ""
        web_request.ext =""
        web_request.path = ""
        web_request.method = ""
        
        request_list = []
        request_list = request.split("\n")
        web_request.method = request_list[0].split(" ")[0]
        web_request.path = request_list[0].split(" ")[1]
        if '.' in web_request.path:
            web_request.ext = web_request.path.split('.')[1]
        else:
            web_request.ext = 'html'
        web_request.arguments = request_list[-1]
        for i in request_list:
            if "Cookie:" in i: web_request.cookie = i.replace("Cookie: ","")

        print("METHOD:" + web_request.method)
        print("PATH:" + web_request.path)
        print("EXT:" + web_request.ext)
        print("COOKIE:" + web_request.cookie)
        print("ARGUMENTS:" + web_request.arguments)
        print("")

    def get_cookie():
        pass

class web_response:
    def __init__(self, length, cookie):
        self.length = length
        self.cookie = cookie

    def set_cookie():
        if web_request.cookie == "":
            session_id = "session_id=" + str(uuid.uuid1())
            cookie = "Set-Cookie: " + session_id + "\r\n"
            return cookie

    def set_headers():
        content_type = {'css':'text/css',
                        'html': 'text/html',
                        'ico': 'image/x-icon',
                        'jpg': 'image/jpg',
                        'png': 'image/png'}

        http_status =  "HTTP/1.1 200 OK\r\n"
        con_type = 'Content-Type: ' + content_type[web_request.ext] + " \r\n"
        server_date = "Date: " + str(datetime.datetime.now()) + "\r\n"
        server_name = "Server: Custom\r\n"
        con_length = "Content-Length: " + web_response.length + " \r\n"
        cookie = web_response.set_cookie()
        if cookie is None: cookie = ''
        accept_range = ''
        if 'image' in content_type[web_request.ext]: 
            accept_range = 'Accept-Ranges: bytes\r\n'
            head = http_status + con_type + accept_range + '\r\n'
            return head.encode()
        else:
            head = http_status + con_type + server_date + server_name + con_length + cookie + "\r\n\r\n"
            return head.encode()    

    def static(url):
        url=url[1:]
        if not 'static' in url: url = 'static/' + url
        f = open(url, "rb")
        obj = f.read()
        web_response.length=str(len(obj))
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

        if "/favicon.ico" in web_request.path:
            self.transport.write(web_response.static(web_request.path))
        if "/static/" in web_request.path:
            self.transport.write(web_response.static(web_request.path))

        for i in dir(vars.controller):
            if not "__" in i:
                if web_request.path == "/" and i=="index":
                    func = getattr(vars.controller,i)
                    proc=func(web_request.arguments)
                    cont=proc
                    web_response.content_type = 'text/html'
                    web_response.length=str(len(cont))
                    head = web_response.set_headers()
                    resp_msg = head + cont.encode()
                    self.transport.write(resp_msg)
                if i == web_request.path.replace("/",""):
                    func = getattr(vars.controller,i)
                    proc=func(web_request.arguments)
                    cont=proc
                    web_response.content_type = 'text/html'
                    web_response.length=str(len(cont))
                    head = web_response.set_headers()
                    resp_msg = head + cont.encode()
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
        server = await loop.create_server(lambda: web_handle(), server_ip, server_port, ssl=ssl_context)
        async with server: await server.serve_forever()
        

class app:
    def start(controller):
        vars.controller=controller
        try:
            asyncio.run(web_server.connection_loop())
        except:
            pass