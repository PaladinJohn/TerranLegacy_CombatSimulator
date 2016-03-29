from tkinter import *
import sqlite3, random

Characters = []
Enemies = []
Combatants = []
root = Tk()

class Character():
    def __init__(self, name, HP, attack, defense, acc, eva):
        self.name = name
        self.HP = HP
        self.attack = attack
        self.defense = defense
        self.acc = acc
        self.eva = eva
        self.CT = 0

    def getName():
        return self.name

class Enemy():
    def __init__(self, name, HP, attack, defense, acc, eva):
        self.name = name
        self.HP = HP
        self.attack = attack
        self.defense = defense
        self.acc = acc
        self.eva = eva
        self.CT = 0

class BattleConstructor():
    def __init__(self):
        self.conn = sqlite3.connect('stats.db')

    def Populate(self):
        with self.conn:    
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM Characters")
            rows = cur.fetchall()
            for row in rows:
                self.character = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                Characters.append(self.character)
            cur.execute("SELECT * FROM Enemy")
            rows = cur.fetchall()
            for row in rows:
                self.enemy = Enemy(row[0], row[1], row[2], row[3], row[4], row[5])
                Enemies.append(self.enemy)

class GUI():
    def __init__(self):
        def addCharacter(character):
            Combatants.append(character)

        def addEnemy(enemy):
            Combatants.append(enemy)

        def showCombatants():
            for c in Combatants:
                print(c.name)
            mb.destroy()
            B.destroy()
            BattleScreen()

        i = 0
        mb = Menubutton(root, text="Combatants", relief=RAISED)
        mb.grid()
        mb.menu = Menu(mb, tearoff = 0)
        mb["menu"] = mb.menu
        for char in Characters:
            mb.menu.add_command(label=char.name, command=lambda x=i: addCharacter(Characters[x]))
            i = i + 1
        i = 0
        for en in Enemies:
            mb.menu.add_command(label=Enemies[i].name, command=lambda x=i: addEnemy(Enemies[x]))
            i = i + 1
        mb.pack()
        B = Button(root, text ="Go!", command = showCombatants)
        B.pack()
        root.mainloop()

class BattleScreen():
    def __init__(self):
        self.prompt = StringVar()
        
        def TakeTurn():
            Combatants[0].CT -= 80
            msg = "%s took their turn!" %Combatants[0].name
            log(msg)
            BS.getTurn(self.prompt)

        def log(msg):
            # Write on GUI
            self.txt.insert('end', msg + '\n')

    # create a Frame for the Text and Scrollbar
        txt_frm = Frame(root, width=600, height=600)
        txt_frm.pack(fill="both", expand=True)
        # ensure a consistent GUI size
        txt_frm.grid_propagate(False)
        # implement stretchability
        txt_frm.grid_rowconfigure(0, weight=1)
        txt_frm.grid_columnconfigure(0, weight=1)

    # create a Text widget
        self.txt = Text(txt_frm, borderwidth=3, relief="sunken")
        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # create a Scrollbar and associate it with txt
        scrollb = Scrollbar(txt_frm, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set

        L = Label(root, textvariable = self.prompt)
        L.pack()
        self.prompt.set('Loading...')
        BS = BattleScene(self.prompt)

        B = Button(root, text ="Take Turn", command = TakeTurn)
        B.pack()

class BattleScene():
    def __init__(self, prompt):
        self.Initiative()
        self.getTurn(prompt)

    def Initiative(self):
        for c in Combatants:
            c.CT = random.randint(0, 100)

    def getTurn(self, prompt):
        Combatants.sort(key = lambda Combatant: Combatant.CT, reverse = True)
        while Combatants[0].CT < 100:
            self.ClockTick()
        prompt.set(Combatants[0].name + '\'s Turn!')

    def ClockTick(self):
        for c in Combatants:
            c.CT += 5

class main():
    constructor = BattleConstructor()
    constructor.Populate()
    GUI = GUI()

if __name__ == "__main__":
    main()
