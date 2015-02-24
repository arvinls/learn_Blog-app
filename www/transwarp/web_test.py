import types, os, re, cgi, sys, time, datetime, functools, mimetypes, threading, logging, urllib, traceback

try:
	from cStringIO import cStringIO
except ImportError:
	from StringIO import StringIO

_RESPONSE_STATUSES = {
	100: 'Continue',
	101: 'Switching Protocals',
	102: 'Processing',

	#Successful
	200: 'OK',
	201: 'Created',
	202: 'Accepted',
	203: 'Non-Authoritative Information',
	204: 'No Content',
	205: 'Reset Content',
	206: 'Partial Content',
	207: 'Multi Status',
	226: 'IM Used',

	#Redirection
	300: 'Multiple Choices',
	301: 'Moved Permanently',
	302: 'Found',
	303: 'See Other',
	304: 'Not Modified',
	305: 'Use Proxy',
	307: 'Temporary Redirect',

	#Client Error
	400: 'Bad Request',
	401: 'Unauthorized',
	402: 'Payment Required',
	403: 'Forbidden',
	404: 'Not Found',
	405: 'Method Not Allowed',
	406: 'Not Acceptable',
	407: 'Proxy Authentication Required',
	408: 'Request Timeout',
	409: 'Conflict',
	410: 'Gone',
	411: 'Length Required',
	412: 'Precondition Failed',
	413: 'Request Entity Too Large',
	414: 'Request URI Too Long',
	415: 'Unsupported Media Type',
	416: 'Requested Range Not Satisfiable',
	417: 'Exception Failed',
	418: "I'm a teapot",
	422: 'Unprocessable Entity',
	423: 'Locked',
	424: 'Failed Dependency',
	426: 'Upgrade Required',

	#Server Error
	500: 'Internal Server Error',
	501: 'Not Implemented',
	502: 'Bad Gateway',
	503: 'Service Unavailable',
	504: 'Gateway Timeout',
	505: 'HTTP Version Not Supported',
	507: 'Insufficient Storage',
	510: 'Not Extended',
}

_RE_RESPONSE_STATUS = re.compile(r'^\d\d\d(\ [\w\ ]+)?$')
class HttpError(Exception):
	'''
	HttpError that defines http error code.

	>>> e = HttpError(404)
	>>> e.status
	'404 Not Found'
	'''
	def __init__(self, code):
		'''
		Init an HttpError with response code.
		'''
		super(HttpError, self).__init__()
		self.status = '%d %s' % (code, _RESPONSE_STATUSES[code])

	def header(self, name, value):
		if not hasattr(self, '_headers'):
			self._headers = [_HEADER_X_POWERED_BY]
		self._headers.append((name, value))
	@property
	def headers(self):
		if hasattr(self, '_headers'):
			return self._headers
		return []

	def __str__(self):
		return self.status
	__repr__ = __str__


class RedirectError(HttpError):
	'''
	RedirectError that defines http redirect code.

	>>> e = RedirectError(302, 'http://www.apple.com/')
	>>> e.status
	'302 Found'
	>>> e.location 
	'http://www.apple.com/'
	'''
	def __init__(self, code, location):
		'''
		Init an HttpError with response code.
		'''
		super(RedirectError, self).__init__(code)
		self.location = location

	def __str__(self):
		return '%s, %s' % (self.status, self.location)

	__repr__ = __str__

def redirect(location):
	'''
	Do permanent redirect.

	>>> raise redirect('http://www.itranswarp.com/')
	Traceback (most recent call last):
		...
	RedirectError: 301 Moved Permanently, http://www.itranswarp.com/
	'''
	return RedirectError(301, location)

if __name__ == '__main__':
	sys.path.append('.')
	import doctest
	doctest.testmod()