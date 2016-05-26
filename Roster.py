from Character import *
import Pyro4, socket, sqlite3

class Roster(object):
    def __init__(self):
        self.contents = []
        self.Characters = []
        self.Enemies = []
        self.conn = sqlite3.connect('stats.db')
        self.Populate()

    def Populate(self):
        with self.conn:    
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM Characters")
            rows = cur.fetchall()
            for row in rows:
                self.character = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                daemon.register(self.character)
                self.Characters.append(self.character)
            cur.execute("SELECT * FROM Enemy")
            rows = cur.fetchall()
            for row in rows:
                self.enemy = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                daemon.register(self.enemy)
                self.Enemies.append(self.enemy)

    def get(self, i):
        return self.contents[i]

    def retList(self):
        return self.contents

    def add(self, i, isChar):
        if isChar == True:
            self.contents.append(self.Characters[i])
        else:
            self.contents.append(self.Enemies[i])

    def getNumChars(self):
        return len(self.Characters)

    def getCharName(self, i):
        return self.Characters[i].name

    def getNumEn(self):
        return len(self.Enemies)

    def getEnName(self, i):
        return self.Enemies[i].name

    def testConnection(self):
        return 4

daemon = Pyro4.Daemon()
#daemon.serveSimple({Roster(): "Combatants"}, host=socket.gethostname(), port=4594, ns=True)
