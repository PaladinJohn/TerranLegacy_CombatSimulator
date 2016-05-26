class Character(object):
    def __init__(self, name, HP, attack, defense, acc, eva):
        self.name = name
        self.HP = HP
        self.attack = attack
        self.defense = defense
        self.acc = acc
        self.eva = eva
        self.CT = 0
        self.hasMoved = False
        self.hasActed = False
