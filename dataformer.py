import sqlite3
db=sqlite3.connect("d:\\temp\\talk.sqlite")
cur=db.cursor()
cur.execute("Select ZTEXT from ZMESSAGE where CHAT=3 ORDER BY ZTIMESTAMP ASC")
db.close()