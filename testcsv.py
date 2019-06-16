# coding : utf-8
import sqlite3


conn = sqlite3.connect('./main.sqlite')
c = conn.cursor()
# print "Opened database successfully";

# c.execute("INSERT INTO Judicial (ID,COURT,CASE_TYPE,CASE_YEAR,CASE_CODE,CASE_DATE,CASE_INFO,CASE_FILE) \
# VALUES (1, 'court', 'case_type', 'year', 'code', 'date', 'result', 'ink' )")

c.execute('''CREATE TABLE Judicial
       ([ID] INTEGER PRIMARY KEY NULL,
       COURT           TEXT    NOT NULL,
       CASE_TYPE       TEXT    NOT NULL,
       CASE_YEAR       TEXT    NOT NULL,
       CASE_CODE       TEXT    NOT NULL,
       CASE_DATE       TEXT    NOT NULL,
       CASE_INFO       TEXT    NOT NULL,
       CASE_FILE       TEXT    NOT NULL);''')

conn.commit()
conn.close()