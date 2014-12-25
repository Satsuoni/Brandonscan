import sqlite3
import datetime
print(
    datetime.datetime.fromtimestamp(
        int("1284101485")
    ).strftime('%Y-%m-%d %H:%M:%S')
)
db=sqlite3.connect("d:\\temp\\talk.sqlite")
cur=db.cursor()
cur.execute("Select ZTEXT from ZMESSAGE where CHAT=3 ORDER BY ZTIMESTAMP ASC")
db.close()