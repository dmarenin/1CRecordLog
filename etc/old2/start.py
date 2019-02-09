from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from common import external_record_log
import sys
from common import common

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    parser = common.createParser()
    namespace = parser.parse_args(sys.argv[1:])
    erl = external_record_log.ExternalRecordLog()
    server = ThreadedHTTPServer((namespace.ip, int(namespace.port)), external_record_log.ExternalRecordLog_Handler)
    print('Starting External Record Log '+str(namespace.ip)+':'+str(namespace.port)+' (use <Ctrl-C> to stop)')
    server.serve_forever()

