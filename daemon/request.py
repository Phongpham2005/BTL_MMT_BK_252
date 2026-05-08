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
        # 1. Tách Headers và Body (Dùng biến 'request' truyền vào)
        parts = request.split('\r\n\r\n', 1)
        header_section = parts[0]
        
        # Gán body: Luôn là chuỗi (thậm chí là rỗng) để App json.loads không bị crash
        self.body = parts[1] if len(parts) > 1 else ""
        
        # Gán lại cho các biến tạm của Thắng nếu cần
        self._raw_headers = header_section
        self._raw_body = self.body

        # 2. Phân tích Request Line
        self.method, self.path, self.version = self.extract_request_line(self._raw_headers)
        
        # 4. Xử lý Routing (QUAN TRỌNG: method phải uppercase)
        if routes:
            self.routes = routes
            # Nên dùng .upper() để chắc chắn khớp với key trong AsynapRous
            self.hook = routes.get((self.method.upper(), self.path))

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

    def get_auth_credentials(self):
        """Giải mã header Authorization từ Base64 sang văn bản thô."""
        auth_header = self.headers.get('authorization', '')
        if auth_header.startswith('Basic '):
            import base64
            encoded = auth_header.split(' ')[1]
            decoded = base64.b64decode(encoded).decode('utf-8')
            if ':' in decoded:
                return decoded.split(':', 1) # Trả về [user, password]
        return None, None