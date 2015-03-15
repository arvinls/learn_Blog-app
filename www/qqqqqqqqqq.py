import urls


for name in dir(urls):
	fn = getattr(urls, name)
	print name
	print '-------------------------'
	if callable(fn) and hasattr(fn, '__web_route__') and hasattr(fn, '__web_method__'):
		print '===========',
		print name


