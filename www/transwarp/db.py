#Written by Arvin
#transwarp.db

__author__ = "Arvin"

'''
Database operation module.

This module is imitate the  http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/0013976160374750f95bd09087744569be5aae6160c8351000

'''
import time, uuid, functools, threading, logging

#Dick object
class Dict(dict):
	def __init__(self, names=(), values = (), **kw):
		super(Dict, self).__init__(*kw)
		for k, v in zip(names, values):
			self[k] = v
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)
	def __setattr__(self, key, value):
		self[key] = value
	

def next_id(t = None):
	if t is None:
		t = time.time()
	return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


class _LasyConnection(object):
	def __init__(self):
		self.connection = None


	def cursor(self):
		if self.connection is None:
			connection = engine.connect()  # in the future, the ENGINE will be design

			logging.info('open connection <%s>...' % hex(id(connection)))
			self.connection = connection

		return self.connection.cursor()

	def commit(self):
		self.connection.commit()  #used: self.commit()

	def rollback(self):
		self.connection.rollback()  #used: self.rollback()

	def cleanup(self):  #used: self.cleanup()   this will break the connection
		if self.connection:
			connection = self.connection
			self.connection = None
			logging.info('close connection <%s>...' % hex(id(connection)))
			print connection
			connection.close()


class _DbCtx(threading.local):
	'''
	Threading local object that holds connection info.
	'''
	def __init__(self):
		self.connection = None
		self.transactions = 0

	def is_init(self):   #when it is True, meaning the self.connection is init
		if self.connection is None:
			return False
		else:
			return True

	def init(self): # if Flase this method will be used

		self.connection = _LasyConnection()
		self.transactions = 0


	def cursor(self):
			'''return cursor '''
			return self.connection.cursor()

	def cleanup(self):
		self.connection.cleanup()
		self.connection = None

#thread=local db context
_db_ctx = _DbCtx()

#global engine object:
engine = None

class _Engine(object):
	'''
	used:
		t = _Engine(connect)
		t.connect  == connect
		but is you donnot use t.connect the  value of connect
		will not be assigned to t.connect

		but I donnot know what is the arm......... 
	'''
	def __init__(self, connect):
		self._connect = connect

	def connect(self):
	
		return self._connect()


def create_engine(user, password, database, host = '127.0.0.1', port = 3306,  **kw):
	'''
		if kw[use_unicode] is exit, then:
			params[use_unicode] = kw[use_unicode]
		else
			params[use_unicode] = defaults[use_unicode]
	'''
	import mysql.connector
	global engine
	if engine is not None:
		raise DBError('Engine is already initialized.')
	params = dict(user = user, password = password, database = database, host = host, port = port)
	defaults = dict(use_unicode = True, charset = 'utf8', collation = 'utf8_general_ci', autocommit = False)
	for k, v in defaults.iteritems():
		params[k] = kw.pop(k, v)

	params.update(kw)
	params['buffered']  =True
	engine = _Engine(lambda: mysql.connector.connect(**params))
	
	#test the connection....
	logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

class _ConnectionCtx(object):
	'''
	_ConnectionCtx object that can open and close connection context.
	_ConnectionCtx object can be nested and only the most 
	outer connection has effect.

	with connection():
		pass
		with connection():
			pass
	'''
	def __enter__(self):
		global _db_ctx
		self.should_cleanup = False 
		'''
		if _db_ctx is init , then the should_cleanup is Flase ?????
		'''
		if not _db_ctx.is_init():
			_db_ctx.init()
			'''
		def init(self):
		logging.info('open lazy connection...')
   			self.connection = _LasyConnection()
		self.transactions = 0

			'''
			self.should_cleanup = True

		return self

	def __exit__(self, exctype, excvalue, traceback):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup()

def connection():
	return _ConnectionCtx()

def with_connection(func):
	'''
	Decorator for reuse conncetion.

	@with_connection
	def foo(*args, **kw):
		f1()
	'''
	@functools.wraps(func)
	def _wrapper(*args, **kw):
		with connection():
			return func(*args, **kw)
	return _wrapper

	'''
	when use this:
	@with_connection
	def func(*args, **kw):
		pass


	'''
	#when use this function which means:
	#with_connection(func)(*args, **kw)====> _wrapper(*args, **kw)


class _TransactionCtx(object):
	'''
	_TransactionCtx object can handle transactions.
	with _TransactionCtx:
		pass
	'''
	def __enter__(self):
		global _db_ctx
		self.should_close_conn = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_close_conn = True
		_db.ctx.transactions = _db_ctx.transactions + 1
		logging.info('begin transaction ...' if _db_ctx.transaction == 1 else 'join current transaction...')
		return self

	def __exit__(self, exctype, excvalue, traceback):
		global _db_ctx
		_db_ctx.tansactions = _db_ctx.tansactions - 1
		try:
			if _db_ctx.transactions == 0:
				if exctype is None:
					self.commit()
				else:
					self.rollback()
		finally:
			if self.should_close_conn:
				_db_ctx.cleanup()

	def commit(self):
		global _db_ctx
		logging.info('commit transactions......')
		try:
			_db_ctx.connection.commit()
			logging.info('commit ok')
		except:
			logging.warning('commit failed. try rollback.....')
			_db_ctx.connection.rollback()
			logging.warning('rollback ok')
			raise

	def rollback(self):
		global _db_ctx
		logging.warning('rollback transaction ......')
		_db_ctx.connection.rollback()
		logging.info('rollback ok.')


def transaction():
	return _TransactionCtx()

def _profiling(start, sql = ''):
	t = time.time() - start
	if t > 0.1:
		logging.warning('[PROFILING] [DB] %s : %s' % (t, sql))
	else:
		logging.info('[PROFILING] [DB] %s: %s' % (t, sql))


def with_transaction(func):
	@functools.wraps(func)
	def _wrapper(*args, **kw):
		_start = time.time()
		with _TransactionCtx():
			return func(*args, **kw)
		_profiling(_start)
	return _wrapper


def _select(sql, first, *args):
	'execute select SQL and return unique result of list results'
	global _db_ctx
	cursor = None
	sql = sql.replace('?', '%s') # '''I donnot know what does this mean????'''
	logging.info('SQL: %s, ARGS: %s' % (sql, args))
	try:
		cursor = _db_ctx.connection.cursor()
		cursor.execute(sql, args)
		if cursor.description:
			names = [x[0] for x in cursor.description]
		if first:
			value = cursor.fetchone()
			if not value:
				return None
			return Dict(names, value)
		return [Dict(names, x) for x in cursor.fetchall()]
	finally:
		if cursor:
			cursor.close()

@with_connection
def select_one(sql, *args):
	#'''
	#Execute select SQL and expected one result. 
	#If no result found, return None.
	#If multiple results found, the first one returned.

#	>>> u1 = dict(id=100, name='Alice', email='alice@test.org', passwd='ABC-12345', last_modified=time.time())
#	>>> u2 = dict(id=101, name='Sarah', email='sarah@test.org', passwd='ABC-12345', last_modified=time.time())
#	>>> insert('user', **u1)
#	1
#	>>> insert('user', **u2)
#	1
#	>>> u = select_one('select * from user where id=?', 100)
#	>>> u.name
#	u'Alice'
#	>>> select_one('select * from user where email=?', 'abc@email.com')
#	>>> u2 = select_one('select * from user where passwd=? order by email', 'ABC-12345')
#	>>> u2.name
#	u'Alice'
#	'''
	return _select(sql, True, *args)

@with_connection
def select_int(sql, *args):

	d = _select(sql, True, *args)
	if len(d) != 1:
		raise MultiColumnsError('Except only one colum.')
	return d.value()[0]
@with_connection
def select(sql, *args):
	return _select(sql, False, *args)

@with_connection
def _update(sql, *args):
	global _db_ctx
	cursor = None
	sql = sql.replace('?', '%s')
	logging.info('SQL: %s, ARGS: %s' % (sql, args))
	try:
		cursor = _db_ctx.connection.cursor()
		cursor.execute(sql, args)
		r = cursor.rowcount
		if _db_ctx.transactions == 0:
			logging.info('auto commit')
			_db_ctx.connection.commit()
		return r

	finally:
		if cursor:
			cursor.close()

def insert(table, **kw):
	cols, args = zip(*kw.iteritems())
	sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]), ','.join(['?' for i in range(len(cols))]))
	return _update(sql, *args)

def update(sql, *args):

	return _update(sql, *args)

if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG)
	create_engine('root', '****your code***', 'test')
	update('drop table if exists user')
	update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')
	import doctest
	doctest.testmod()


