import os
import datetime
import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from config import *    

class GetStaticHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request_path = urlparse.urlparse(self.path)[2]
        if request_path == '/':
            self.send_response(200)
            self.end_headers()
            # page_server is module global variable
            self.wfile.write(page_server.index())
        else:
            file_path = request_path[1:]
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = ''.join(f.readlines())
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(content)
            else:
                self.send_error(500, 'No Such File: %s' % file_path)

class AppServer(object):
    def run(self):
        print('Server Is Listening on localhost:8080')
        server = HTTPServer((HOSTNAME, PORT), GetStaticHandler)
        server.serve_forever()
    
    def set_working_dir(self, working_dir):
        if os.path.isdir(working_dir):
            self.working_dir = working_dir
        else:
            raise Exception('working_dir is not a directory')
    def index(self):
        if not self.working_dir:
            raise Exception('Please Set working_dir firstly')
        
        def collecter(fl, dirname, itemnames):
            for itemname in itemnames:
                item_path = os.path.join(dirname, itemname)
                if os.path.isfile(item_path) and item_path.endswith(SUFFIX_NAME):
                    fl[os.path.getmtime(item_path)] = item_path
        file_list = {}
        os.path.walk(self.working_dir, collecter, file_list)
        
        li_template = '<li><a href="%(filename)s">%(filename)s</a> - <span>%(mtime)s</span></li>'
        content_header = '<!doctype><html><head><title>BootstrapTestBox</title></head><body><ul>'
        content = ''.join([
            li_template % {'filename': file_list[k], 'mtime': datetime.datetime.fromtimestamp(k).strftime('%Y-%M-%d %H:%M:%S')}
            for k in reversed(file_list.keys())
        ])
        content_footer = '</ul></body></html>'
        return ''.join([content_header, content, content_footer])

page_server = AppServer()
page_server.set_working_dir(WORKING_DIR)

if __name__ == '__main__':
    page_server.run()
