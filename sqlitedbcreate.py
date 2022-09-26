import sqlite3

conn = sqlite3.connect('dbd.db')
print("Opened database successfully")

#drop table if it exists
conn.execute('''DROP TABLE IF EXISTS DIS_STEAM_CONN''')
print("Table dropped successfully")


# Create table named DIS_STEAM_CONN with columns discordid and steamid and username
conn.execute('''CREATE TABLE DIS_STEAM_CONN
       (DISCORDID INT PRIMARY KEY     NOT NULL,
       STEAMID           INT    NOT NULL,
       USERNAME          TEXT   NOT NULL);''')
print("Table created successfully")

conn.close()


