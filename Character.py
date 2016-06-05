class PlayerItem(object):
    def __init__(self, name, num):
        self.name = name
        self.quantity = num

class Character(object):
    def __init__(self, name, HP, MP, attack, defense, acc, eva):
        self.name = name
        self.HP = HP
        self.MaxHP = HP
        self.MP = MP
        self.attack = attack
        self.defense = defense
        self.acc = acc
        self.eva = eva
        self.CT = 0
        self.hasMoved = False
        self.hasActed = False
        self.hasUsedItem = False
        self.hasItems = False
        self.abilitiesUsed = 0
        self.id = None
        self.inventory = []

    def getName(self):
        return self.name

    def addItem(self, name, num):
        item = PlayerItem(name, num)
        self.inventory.append(item)

    def checkItems(self):
        self.hasItems = False
        for item in self.inventory:
            if item.quantity > 0:
                self.hasItems = True
