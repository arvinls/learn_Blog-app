from transwarp import db
db.create_engine(user = 'root', password = 'password', database = 'test', host = '127.0.0.1', port = 3306)
user = db.select('select * from user')
n = db.update('insert into user(id, name) values(?, ?)', 4, 'Jack')