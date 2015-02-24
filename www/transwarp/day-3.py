#save the database's name and type
class Field(object):
	def __init__(self, name, column_type):
		self.name = name
		self.column_type = column_type
	def __str__(self):
		return '<%s:%s>' %(self.__class__.__name__, self.name)

class StringField(Field):
	def __init__(self, name):
		super(StringField, self).__init__(name, 'varchar(100)')
		print "string........................"

class IntergerField(Field):
	
	def __init__(self, name):
		super(IntergerField, self).__init__(name, 'bigint')


class ModelMetaclass(type):
	def __new__(cls, name, bases, attrs):
		print cls
		print name
		print bases
		print attrs
		if name == 'Model':
			return type.__new__(cls, name, bases, attrs)
		mappings = dict()

		print "this is metaclass............"
		for k, v in attrs.iteritems():
			if isinstance(v, Field):
				print v
				print('Found mapping: %s ======> %s' % (k, v))
				mappings[k] = v
		for k in mappings.iterkeys():
			attrs.pop(k)
		attrs['__table__'] = name
		attrs['__mappings__'] = mappings
		print attrs
		return type.__new__(cls, name, bases, attrs)

class Model(dict):


	__metaclass__ = ModelMetaclass


	def __init__(self, **kw):
		super(Model, self).__init__(**kw)
		print kw
		print "this is Model  init ........"

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '%s'" % key)
	def __setattr__(self, key, value):
		self[key] = value

	def save(self):
		print "thsi is save"
		fields = []
		params = []
		args = []

		for k, v in self.__mappings__.iteritems():
			fields.append(v.name)
			params.append('?')
			args.append(getattr(self, k, None))
		print params

		sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
		print('SQL: %s' % sql)
		print ('ARGS: %s' % str(args))
	

class User(Model):
	
	
	id = IntergerField('id')

	name = StringField('username')
	email = StringField('email')
	password = StringField('password')
	
print"1111111111111111111111111111111111"
u = User(id = 12345, name = 'Michael', email = 'test@orm.org', password = 'my-pwd')
print "O ........................................"
u.save
print "WWW ........................................"
