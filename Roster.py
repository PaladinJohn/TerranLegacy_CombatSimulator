from Character import *
import copy, Pyro4, socket, sqlite3

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
            i = 1
            for row in rows:
                self.character = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                self.character.id = i
                cur.execute("SELECT * FROM PlayerInventory WHERE PlayerID="+str(self.character.id))
                inventory = cur.fetchall()
                for item in inventory:
                    cur.execute("SELECT * FROM Item WHERE ItemID="+str(item[1]))
                    tempItem = cur.fetchall()
                    itemName = tempItem[0][0]
                    self.character.addItem(itemName, item[2])
                daemon.register(self.character)
                self.Characters.append(self.character)
                i = i+1
            cur.execute("SELECT * FROM Enemy")
            rows = cur.fetchall()
            for row in rows:
                self.enemy = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                daemon.register(self.enemy)
                self.Enemies.append(self.enemy)

    def get(self, i):
        return self.contents[i]

    def getLast(self):
        i = len(self.contents)
        return self.contents[i-1]

    def retList(self):
        return self.contents

    def add(self, i, isChar):
        if isChar == True:
            self.contents.append(self.Characters[i])
        else:
            #en = copy.copy(self.Enemies[i])
            #daemon.register(en)
            #self.contents.append(en)
            self.contents.append(self.Enemies[i])

    def getNumChars(self):
        return len(self.Characters)

    def getCharName(self, i):
        return self.Characters[i].name

    def getNumEn(self):
        return len(self.Enemies)

    def getEnName(self, i):
        return self.Enemies[i].name

daemon = Pyro4.Daemon()
