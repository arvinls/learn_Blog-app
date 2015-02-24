
class Field(object):
	_count = 0
	def __init__(self, **kw):
		self.name = kw.get('name', None)
		self.primary_key = kw.get('primary_key', None)
		self.ddl = kw.get('ddl', '')

	@property
	





class User(Model):
	id = StringField(primary_key = True, ddl = 'varchar(50)')
	name = StringField(ddl = 'varchar(50)')