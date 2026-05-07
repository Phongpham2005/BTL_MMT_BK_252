#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.request
~~~~~~~~~~~~~~~~~

This module provides a Request object to manage and persist 
request settings (cookies, auth, proxies).
"""
from .dictionary import CaseInsensitiveDict

class Request():
    """The fully mutable "class" `Request <Request>` object,
    containing the exact bytes that will be sent to the server.

    Instances are generated from a "class" `Request <Request>` object, and
    should not be instantiated manually; doing so may produce undesirable
    effects.

    Usage::

      >>> import deamon.request
      >>> req = request.Request()
      ## Incoming message obtain aka. incoming_msg
      >>> r = req.prepare(incoming_msg)
      >>> r
      <Request>
    """
    __attrs__ = [
        "method",
        "url",
        "headers",
        "body",
        "_raw_headers",
        "_raw_body",
        "reason",
        "cookies",
        "body",
        "routes",
        "hook",
    ]

    def __init__(self):
        #: HTTP verb to send to the server.
        self.method = None
        #: HTTP URL to send the request to.
        self.url = None
        #: dictionary of HTTP headers.
        self.headers = None
        #: HTTP path
        self.path = None        
        # The cookies set used to create Cookie header
        self.cookies = None
        #: request body to send to the server.
        self.body = None
        # The raw header
        self._raw_headers = None
        #: The raw body
        self._raw_body = None
        #: Routes
        self.routes = {}
        #: Hook point for routed mapped-path
        self.hook = None

    def extract_request_line(self, request):
        try:
            lines = request.splitlines()
            first_line = lines[0]
            method, path, version = first_line.split()

            if path == '/':
                path = '/index.html'
        except Exception:
            return None, None

        return method, path, version
             
    def prepare_headers(self, request):
        """Prepares the given HTTP headers."""
        lines = request.split('\r\n')
        headers = {}
        for line in lines[1:]:
            if ': ' in line:
                key, val = line.split(': ', 1)
                headers[key.lower()] = val
        return headers

    def fetch_headers_body(self, request):
        """Prepares the given HTTP headers."""
        # Split request into header section and body section
        parts = request.split("\r\n\r\n", 1)  # split once at blank line

        _headers = parts[0]
        _body = parts[1] if len(parts) > 1 else ""
        return _headers, _body

    def prepare(self, request, routes=None):
        """Prepares the entire request with the given parameters."""
        # 1. Tách thô Header và Body từ request (dữ liệu thô)
        # Sử dụng hàm fetch_headers_body bạn đã viết bên dưới
        self._raw_headers, self._raw_body = self.fetch_headers_body(request)

        # 2. Phân tích Request Line (Method, Path, Version)
        print("[Request] prepare request missg {}".format(request))
        self.method, self.path, self.version = self.extract_request_line(self._raw_headers)
        print("[Request] {} path {} version {}".format(self.method, self.path, self.version))

        # 3. Phân tích và gán giá trị cho self.headers (FIX LỖI NoneType TẠI ĐÂY)
        # Gọi hàm prepare_headers để biến chuỗi thô thành CaseInsensitiveDict hoặc dict
        from .dictionary import CaseInsensitiveDict
        self.headers = CaseInsensitiveDict(self.prepare_headers(self._raw_headers))

        # 4. Xử lý Routing cho WebApp (AsynapRous)
        if routes and routes != {}:
            self.routes = routes
            print("[Request] Routing METHOD {} path {}".format(self.method, self.path))
            self.hook = routes.get((self.method, self.path))
            # print("[Request] Hook has request {}".format(request))

        # 5. Bây giờ self.headers đã tồn tại, bạn có thể lấy Cookie an toàn
        cookies_raw = self.headers.get('cookie', '')
        if cookies_raw:
            # Gọi hàm parse để biến chuỗi thành dict
            self.cookies = self.prepare_cookies(cookies_raw)
            print("[Request] Cookies detected: {}".format(self.cookies))

        return

    def prepare_body(self, data, files, json=None):
        self.prepare_content_length(self.body)
        self.body = body
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return


    def prepare_content_length(self, body):
        self.headers["Content-Length"] = "0"
        #
        # TODO prepare the request authentication
        #
	# self.auth = ...
        return


    def prepare_auth(self, auth, url=""):
        #
        # TODO prepare the request authentication
        #
        """
        Giải mã header Authorization (Basic Auth)
        """
        auth_header = self.headers.get('authorization', '')
        if auth_header.startswith('Basic '):
            import base64
            # Lấy phần mã hóa sau chữ 'Basic '
            encoded_credentials = auth_header.split(' ')[1]
            # Giải mã sang chuỗi 'user:pass'
            decoded_bytes = base64.b64decode(encoded_credentials)
            decoded_str = decoded_bytes.decode('utf-8')
            
            # Tách user và pass
            if ':' in decoded_str:
                username, password = decoded_str.split(':', 1)
                return username, password
        return None, None

    def prepare_cookies(self, cookies_raw):
        """
        Parses the raw Cookie header string into a dictionary.
        Ví dụ: "id=1; name=thang" -> {'id': '1', 'name': 'thang'}
        """
        cookies_dict = {}
        if cookies_raw:
            # Tách các cặp cookie bằng dấu chấm phẩy
            pairs = cookies_raw.split('; ')
            for pair in pairs:
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    cookies_dict[key] = val
        return cookies_dict
