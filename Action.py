import random

class Action():
    def Attack(acc, eva, atk, dfn):
        toHitRoll = random.randint(1, 100)
        if(toHitRoll == 1):
            baseDamage = random.randint(atk, (2 * atk))
            actualDamage = max(1, (baseDamage - dfn)) + baseDamage
            return actualDamage
        elif(toHitRoll >= (acc - eva) or toHitRoll == 100):
            return -1
        else:
            #Damage Calculation
            baseDamage = random.randint(atk, (2 * atk))
            actualDamage = max(1, (baseDamage - dfn))
            return actualDamage
