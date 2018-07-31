import sqlite3
class DB():
    def DB(self):
        self.conn = sqlite3.connect('backup.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY AUTOINCREMENT, server text, username text, password text)''')
        self.conn.commit()

    def checkServer(self, server,username,password):
        res = False
        where = (server,username,password,)
        self.c.execute('SELECT * FROM servers WHERE server=? AND username=? AND password=?', where)
        try:
            server = self.c.fetchone()[1]
            res = True
        except:
            print "error"
        return res

        

    def insertServer(self, server, username, password):
        self.c.execute("INSERT INTO servers (server,username,password) VALUES ('"+server+"','"+username+"','"+password+"')")
        self.conn.commit()

    def getServers(self):
        self.c.execute('SELECT * FROM servers')
        return self.c.fetchall()

    def close(self):
        self.conn.close()
        self.c.close()