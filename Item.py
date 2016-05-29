from Character import *

class Item():
    def Potion(Character):
        Character.HP += 80
        if Character.HP > Character.MaxHP:
            Character.HP = Character.MaxHP
        msg = Character.name + " recovered 80 HP!"
        return msg
