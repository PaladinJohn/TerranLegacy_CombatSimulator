from Action import *
from kivy.app import App
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.actionbar import ActionBar, ActionButton, ActionPrevious, ActionView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
import random, socket, sqlite3, threading

Characters = []
Enemies = []
Combatants = []
Screens = []
sm = ScreenManager()

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

class ConnectionScreen(Screen):
    def __init__(self, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)

        def on_enter(instance):
            t = threading.Thread(target = connect)
            t.setDaemon(True)
            t.start()

        def connect():
            host = self.textinput.text
            s.connect((host, 4594))
            data = s.recv(2048).decode()
            message = "Network Test."
            s.send(message.encode())
            self.manager.current = 'Selection Screen'
            

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('', 4594)
            #s.bind(server_address)
        except(socket.error, msg):
            print("Failed to create socket. Error Code: " + str(msg[0]) + " Message " + msg[1])
            sys.exit()
        
        self.root = BoxLayout(orientation='vertical')
        self.textinput = TextInput(text='John-PC', multiline=False)
        self.textinput.bind(on_text_validate=on_enter)
        self.root.add_widget(self.textinput)
        self.add_widget(self.root)

class SelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectionScreen, self).__init__(**kwargs)

        self.root = Accordion()
        charItem = AccordionItem(title='Characters')
        self.root.add_widget(charItem)
        enItem = AccordionItem(title='Enemies')
        self.root.add_widget(enItem)
        confirmItem = AccordionItem(title='Done')
        self.root.add_widget(confirmItem)
        self.CharButtons = []
        self.EnemyButtons = []
        for char in Characters:
            btn = ToggleButton(text=char.name)
            charItem.add_widget(btn)
            self.CharButtons.append(btn)
        for en in Enemies:
            btn = ToggleButton(text=en.name)
            enItem.add_widget(btn)
            self.EnemyButtons.append(btn)
        B = Button(text='Go!')
        B.bind(on_press=self.showCombatants)
        confirmItem.add_widget(B)
        self.add_widget(self.root)

    def showCombatants(self, obj):
        i = 0
        for c in self.CharButtons:
            if c.state == 'down':
                Combatants.append(Characters[i])
            i += 1
        i = 0
        for e in self.EnemyButtons:
            if e.state == 'down':
                Combatants.append(Enemies[i])
            i += 1
        BS = BattleScreen(name="Battle Screen")
        sm.add_widget(BS)
        Screens.append(BS)
        self.manager.current = 'Battle Screen'

class BattleScreen(Screen):
    def __init__(self, **kwargs):
        super(BattleScreen, self).__init__(**kwargs)

        self.bScene = BattleScene()
        self.layout = BoxLayout(orientation='vertical')
        self.actionBar = ActionBar()
        self.view = ActionView()
        self.prompt = self.bScene.getTurn()
        self.nametag = ActionPrevious(title=self.prompt)
        self.MoveButton = ActionButton(text='Move')
        self.AttackButton = ActionButton(text='Attack')
        self.ConfirmButton = ActionButton(text='Take Turn')
        self.MoveButton.bind(on_press=self.Move)
        self.AttackButton.bind(on_press=self.Action)
        self.ConfirmButton.bind(on_press=self.TakeTurn)
        self.battleLog = 'Now Beginning Battle...'
        self.label = Label(text=self.battleLog)
        self.layout.add_widget(self.actionBar)
        self.layout.add_widget(self.label)
        self.actionBar.add_widget(self.view)
        self.view.add_widget(self.nametag)
        self.view.add_widget(self.MoveButton)
        self.view.add_widget(self.AttackButton)
        self.view.add_widget(self.ConfirmButton)
        self.add_widget(self.layout)
        self.Target = Combatants[0]

    def TakeTurn(self, obj):
        if(Combatants[0].hasMoved == True and Combatants[0].hasActed == True):
            delay = 100
        elif(Combatants[0].hasMoved == False and Combatants[0].hasActed == False):
            delay = 60
        else:
            delay = 80
        Combatants[0].CT -= delay
        Combatants[0].hasMoved = False
        Combatants[0].hasActed = False
        self.prompt = self.bScene.getTurn()
        self.nametag.title = self.prompt
        self.MoveButton.disabled = False
        self.AttackButton.disabled = False

    def Move(self, obj):
        Combatants[0].hasMoved = True
        self.MoveButton.disabled = True

    def Action(self, obj):
        Combatants[0].hasActed = True
        self.AttackButton.disabled = True
        Screens[0].populate()
        self.manager.current = 'Action Menu'

    def Attack(self):
        damage = Action.Attack(Combatants[0].acc, self.Target.eva, Combatants[0].attack, self.Target.defense)
        if(damage == -1):
            msg = "%s missed %s!" %(Combatants[0].name, self.Target.name)
            self.battleLog = self.battleLog + "\n" + msg
            self.label.text = self.battleLog
        else:
            msg = "%s hit %s for %d points of damage!" %(Combatants[0].name, self.Target.name, damage)
            self.battleLog = self.battleLog + "\n" + msg
            self.label.text = self.battleLog
            self.Target.HP -= damage
            if(self.Target.HP <= 0):
                msg = "%s was defeated!" %(self.Target.name)
                self.battleLog = self.battleLog + "\n" + msg
                self.label.text = self.battleLog

class ActionMenu(Screen):
    def __init__(self, **kwargs):
        super(ActionMenu, self).__init__(**kwargs)

        self.root = Accordion(orientation='vertical')
        self.targItem = AccordionItem(title='Target')
        self.root.add_widget(self.targItem)
        self.conItem = AccordionItem(title='Confirm')
        self.root.add_widget(self.conItem)
        B = Button(text='Confirm')
        B.bind(on_press=self.confirmTarget)
        self.conItem.add_widget(B)
        self.add_widget(self.root)

    def populate(self):
        self.ComButtons = []
        for c in Combatants:
            btn = ToggleButton(text=c.name, group='targets')
            self.targItem.add_widget(btn)
            self.ComButtons.append(btn)

    def confirmTarget(self, obj):
        hasTarget = False
        i = 0
        for b in self.ComButtons:
            if b.state == 'down':
                hasTarget = True
                Screens[1].Target = Combatants[i]
            i += 1
        if hasTarget == True:
            hasTarget = False
            self.targItem.clear_widgets(children=self.ComButtons)
            self.ComButtons.clear()
            self.manager.current = 'Battle Screen'
            Screens[1].Attack()

class CombatApp(App):
    def build(self):
        CS = ConnectionScreen(name="Connection Screen")
        sm.add_widget(CS)
        SS = SelectionScreen(name="Selection Screen")
        sm.add_widget(SS)
        AM = ActionMenu(name="Action Menu")
        Screens.append(AM)
        sm.add_widget(AM)
        return sm

class BattleScene():
    def __init__(self):
        self.Initiative()
    
    def Initiative(self):
        for c in Combatants:
            c.CT = random.randint(0, 100)

    def getTurn(self):
        Combatants.sort(key = lambda Combatant: Combatant.CT, reverse = True)
        while Combatants[0].CT < 100:
            self.ClockTick()
        prompt = Combatants[0].name
        return prompt

    def ClockTick(self):
        for c in Combatants:
            c.CT += 5

class main():
    constructor = BattleConstructor()
    constructor.Populate()
    CombatApp().run()

if __name__ == '__main__':
    main()
