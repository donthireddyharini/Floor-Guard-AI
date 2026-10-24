import sqlite3

conn = sqlite3.connect('data/database.sqlite')
c = conn.cursor()
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for name, sql in c.fetchall():
    print('TABLE:', name)
    print(sql)
    print('-' * 50)
