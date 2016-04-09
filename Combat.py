from tkinter import *
from Action import *
import random, socket, sqlite3, sys, threading

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
        self.hasMoved = False
        self.hasActed = False

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
                self.enemy = Character(row[0], row[1], row[2], row[3], row[4], row[5])
                Enemies.append(self.enemy)

class ClientConnect():
    def __init__(self):
        def tCon():
            t = threading.Thread(target = connect)
            t.setDaemon(True)
            t.start()
            
        def connect():
            host = e.get()
            print(host)
            s.connect((host, 4594))
            try:
                message = "Network Test."
                s.send(message.encode())
                print("Success!")
            except(socket.error, msg):
                print("Failed to create socket. Error Code: " + str(msg[0]) + " Message " + msg[1])
                sys.exit()
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('', 4594)
            s.bind(server_address)
        except(socket.error, msg):
            print("Failed to create socket. Error Code: " + str(msg[0]) + " Message " + msg[1])
            sys.exit()

        e = Entry(root)
        e.pack()
        e.focus_set()
        b = Button(root, text="Go!", width=10, command=tCon)
        b.pack()
        root.mainloop()

class GUI():
    def __init__(self):
        def addCharacter(character):
            Combatants.append(character)

        def addEnemy(enemy):
            Combatants.append(enemy)

        def showCombatants():
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
            mb.menu.add_command(label=en.name, command=lambda x=i: addEnemy(Enemies[x]))
            i = i + 1
        mb.pack()
        B = Button(root, text ="Go!", command = showCombatants)
        B.pack()
        root.mainloop()

class BattleScreen():
    def __init__(self):
        self.prompt = StringVar()
        
        def TakeTurn():
            if(Combatants[0].hasMoved == True and Combatants[0].hasActed == True):
                delay = 100
            elif(Combatants[0].hasMoved == False and Combatants[0].hasActed == False):
                delay = 60
            else:
                delay = 80
            Combatants[0].CT -= delay
            Combatants[0].hasMoved = False
            BS.getTurn(self.prompt)
            MoveB.config(state="normal")
            AttackB.config(state="normal")

        def Move():
            Combatants[0].hasMoved = True
            MoveB.config(state="disabled")

        def Attack():
            Combatants[0].hasActed = True
            AttackB.config(state="disabled")
            SelectionMenu()

        def SelectionMenu():
            i = 0
            self.attframe = Frame(txt_frm)
            self.attframe.grid(row=2, column=0, columnspan=2)
            for c in Combatants:
                a = Button(self.attframe, text=c.name, command = lambda x=c: setTarget(x)).grid(row=0, column=i)
                i += 1

        def setTarget(c):
            damage = Action.Attack(Combatants[0].acc, c.eva, Combatants[0].attack, c.defense)
            if(damage == -1):
                msg = "%s missed %s!" %(Combatants[0].name, c.name)
                log(msg)
            else:
                msg = "%s hit %s for %d points of damage!" %(Combatants[0].name, c.name, damage)
                log(msg)
                c.HP -= damage
                if(c.HP <= 0):
                    msg = "%s was defeated!" %(c.name)
                    log(msg)
            self.attframe.destroy()

        def log(msg):
            self.txt.insert('end', msg + '\n')

    # create a Frame for the Text and Scrollbar
        txt_frm = Frame(root, width=600, height=600)
        txt_frm.pack(fill="both", expand=True)
        txt_frm.grid_propagate(False)
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

        buttonframe = Frame(txt_frm)
        buttonframe.grid(row=2, column=0, columnspan=2)
        MoveB = Button(buttonframe, text ="Move", command = Move)
        MoveB.grid(row=0, column=0)
        AttackB = Button(buttonframe, text ="Attack", command = Attack)
        AttackB.grid(row=0, column=1)
        B = Button(buttonframe, text ="Take Turn", command = TakeTurn)
        B.grid(row=0, column=2)

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
    #Old Selector GUI. Temporarily disabled for First-Playable.
    #GUI = GUI()
    cli = ClientConnect()

if __name__ == "__main__":
    main()
