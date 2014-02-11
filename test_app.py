from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

def simple_app(environ, start_response):
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/plain'),
               ('Cache-Control', "max-age=5, public")]

    print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
    start_response(status, headers)

    return '<html>Hello World</html>'

httpd = make_server('', 9000, simple_app)
print "Serving on port 9000..."
httpd.serve_forever()
