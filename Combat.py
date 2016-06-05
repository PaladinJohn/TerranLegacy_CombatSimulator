from _thread import *
from Action import *
from Character import *
from Item import *
from Roster import *
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.actionbar import ActionBar, ActionButton, ActionPrevious, ActionView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
import Pyro4, Pyro4.util, random, socket, sys, threading, time

Combatants = None
Screens = []
sm = ScreenManager()
sys.excepthook = Pyro4.util.excepthook
isDM = False

Builder.load_string('''
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')

class ScrollableLabel(ScrollView):
    text = StringProperty('')

class ConnectionScreen(Screen):
    def __init__(self, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)

        self.root = Accordion()
        roleItem = AccordionItem(title='Role')
        self.root.add_widget(roleItem)
        serverItem = AccordionItem(title='Server')
        self.root.add_widget(serverItem)
        self.dmBtn = ToggleButton(text="DM", group="role")
        self.pcBtn = ToggleButton(text="Player", group="role", state="down")
        self.textinput = TextInput(text='John-LAPTOP', multiline=False)
        self.textinput.bind(on_text_validate=self.on_confirm)
        roleItem.add_widget(self.dmBtn)
        roleItem.add_widget(self.pcBtn)
        serverItem.add_widget(self.textinput)
        self.add_widget(self.root)

    def on_confirm(self, instance):
        global Combatants
        if self.dmBtn.state == "down":
            Combatants = Roster()
            t = threading.Thread(target = self.startServer)
            t.start()
            global isDM
            isDM = True
        elif self.pcBtn.state == "down":
            nameserver = Pyro4.locateNS(host=self.textinput.text)
            Combatants = Pyro4.Proxy("PYRONAME:Combatants")
        SS = SelectionScreen(name="Selection Screen")
        sm.add_widget(SS)
        self.manager.current = 'Selection Screen'

    def startServer(self):
        Pyro4.Daemon.serveSimple({Combatants: "Combatants"}, host=socket.gethostname(), ns=True)

class SelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(SelectionScreen, self).__init__(**kwargs)

        global Combatants
        self.root = Accordion()
        charItem = AccordionItem(title='Characters')
        self.root.add_widget(charItem)
        enItem = AccordionItem(title='Enemies')
        self.root.add_widget(enItem)
        confirmItem = AccordionItem(title='Done')
        self.root.add_widget(confirmItem)
        self.CharButtons = []
        self.EnemyButtons = []
        self.enemyIter = 0
        self.quantity = 0
        self.content = TextInput(text='1', multiline=False)
        self.content.bind(on_text_validate=self.setQuantity)
        i = 0
        while i < Combatants.getNumChars():
            btn = ToggleButton(text=Combatants.getCharName(i))
            charItem.add_widget(btn)
            self.CharButtons.append(btn)
            i = i+ 1
        i = 0
        while i < Combatants.getNumEn():
            btn = ToggleButton(text=Combatants.getEnName(i))
            enItem.add_widget(btn)
            self.EnemyButtons.append(btn)
            i = i + 1
        B = Button(text='Go!')
        B.bind(on_press=self.showCombatants)
        confirmItem.add_widget(B)
        self.add_widget(self.root)

    def showCombatants(self, obj):
        i = 0
        NoEnemies = True
        for c in self.CharButtons:
            if c.state == 'down':
                Combatants.add(i, True)
            i += 1
        i = 0
        for e in self.EnemyButtons:
            if e.state == 'down':
                labStr = "How many " + e.text + "?"
                NoEnemies = False
                self.popup = Popup(title=labStr, content=self.content)
                self.popup.open()
                self.enemyIter = i
            i += 1
        if NoEnemies == True:
            self.beginBattle()

    def setQuantity(self, instance):
        self.quantity = self.content.text
        j = 0
        while j < int(self.quantity):
            Combatants.add(self.enemyIter, False)
            j += 1
            if int(self.quantity) > 1:
                Combatants.getLast().name = Combatants.getLast().name + " " + str(j)
        self.popup.dismiss()
        self.beginBattle()

    def beginBattle(self):
        if isDM == True:
            Combatants.isWaiting = False
            BS = BattleScreen(name="Battle Screen")
            sm.add_widget(BS)
            Screens.append(BS)
            self.manager.current = 'Battle Screen'
        else:
            WS = WaitScreen(name="Wait Screen")
            sm.add_widget(WS)
            self.manager.current = 'Wait Screen'

class WaitScreen(Screen):
    def __init__(self, **kwargs):
        super(WaitScreen, self).__init__(**kwargs)

        self.button = Button(text='Check if Ready')
        self.button.bind(on_press=self.waitForPlayers)
        self.add_widget(self.button)

    def waitForPlayers(self, obj):
        if Combatants.waiting() == False:
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
        self.AbilityButton = ActionButton(text='Item')
        self.ConfirmButton = ActionButton(text='Take Turn')
        self.MoveButton.bind(on_press=self.Move)
        self.AttackButton.bind(on_press=self.Action)
        self.AbilityButton.bind(on_press=self.Ability)
        self.ConfirmButton.bind(on_press=self.TakeTurn)
        self.battleLog = 'Now Beginning Battle...'
        self.label = ScrollableLabel(text=self.battleLog)
        self.layout.add_widget(self.actionBar)
        self.layout.add_widget(self.label)
        self.actionBar.add_widget(self.view)
        self.view.add_widget(self.nametag)
        self.view.add_widget(self.MoveButton)
        self.view.add_widget(self.AttackButton)
        self.view.add_widget(self.AbilityButton)
        self.view.add_widget(self.ConfirmButton)
        self.add_widget(self.layout)
        self.Target = Combatants.get(0)
        Combatants.checkItems(0)
        if Combatants.getHasItems(0) == False:
            self.AbilityButton.disabled = True

    def TakeTurn(self, obj):
        if isDM == True:
            if(Combatants.get(0).hasMoved == True and Combatants.get(0).hasActed == True):
                delay = 100
            elif(Combatants.get(0).hasMoved == False and Combatants.get(0).hasActed == False):
                delay = 60
            else:
                delay = 80
            Combatants.get(0).CT -= delay
            Combatants.get(0).hasMoved = False
            Combatants.get(0).hasActed = False
            self.prompt = self.bScene.getTurn()
            self.nametag.title = self.prompt
        self.MoveButton.disabled = False
        self.AttackButton.disabled = False
        Combatants.checkItems(0)
        if Combatants.getHasItems(0) == True:
            self.AbilityButton.disabled = False
        else:
            self.AbilityButton.disabled = True

    def Move(self, obj):
        Combatants.get(0).hasMoved = True
        self.MoveButton.disabled = True

    def Action(self, obj):
        Screens[0].populate()
        self.manager.current = 'Action Menu'

    def Ability(self, obj):
        Screens[1].populateItems()
        Screens[1].populateTargs()
        self.manager.current = 'Ability Menu'

    def Attack(self):
        damage = Action.Attack(Combatants.get(0).acc, self.Target.eva, Combatants.get(0).attack, self.Target.defense)
        if(damage == -1):
            msg = "%s missed %s!" %(Combatants.get(0).name, self.Target.name)
            self.battleLog = self.battleLog + "\n" + msg
            self.label.text = self.battleLog
        else:
            msg = "%s hit %s for %d points of damage!" %(Combatants.get(0).name, self.Target.name, damage)
            self.battleLog = self.battleLog + "\n" + msg
            self.label.text = self.battleLog
            self.Target.HP -= damage
            if(self.Target.HP <= 0):
                msg = "%s was defeated!" %(self.Target.name)
                self.battleLog = self.battleLog + "\n" + msg
                self.label.text = self.battleLog

    def UseItem(self, num):
        Combatants.get(0).inventory[num].quantity -= 1
        methodToCall = getattr(Item, Combatants.get(0).inventory[num].name)
        msg = methodToCall(self.Target)
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
        B2 = Button(text='Cancel')
        B.bind(on_press=self.confirmTarget)
        B2.bind(on_press=self.cancel)
        self.conItem.add_widget(B)
        self.conItem.add_widget(B2)
        self.add_widget(self.root)

    def populate(self):
        self.ComButtons = []
        for c in Combatants.retList():
            btn = ToggleButton(text=c.name, group='targets')
            self.targItem.add_widget(btn)
            self.ComButtons.append(btn)

    def confirmTarget(self, obj):
        hasTarget = False
        i = 0
        for b in self.ComButtons:
            if b.state == 'down':
                hasTarget = True
                Screens[2].Target = Combatants.get(i)
            i += 1
        if hasTarget == True:
            hasTarget = False
            self.targItem.clear_widgets(children=self.ComButtons)
            self.ComButtons.clear()
            Combatants.get(0).hasActed = True
            Screens[2].AttackButton.disabled = True
            self.manager.current = 'Battle Screen'
            Screens[2].Attack()

    def cancel(self, obj):
        self.targItem.clear_widgets(children=self.ComButtons)
        self.ComButtons.clear()
        self.manager.current = 'Battle Screen'

class AbilityMenu(Screen):
    def __init__(self, **kwargs):
        super(AbilityMenu, self).__init__(**kwargs)

        self.root = Accordion(orientation='vertical')
        self.invItem = AccordionItem(title='Item')
        self.root.add_widget(self.invItem)
        self.targItem = AccordionItem(title='Target')
        self.root.add_widget(self.targItem)
        self.conItem = AccordionItem(title='Confirm')
        self.root.add_widget(self.conItem)
        B = Button(text='Confirm')
        B2 = Button(text='Cancel')
        B.bind(on_press=self.confirmTarget)
        B2.bind(on_press=self.cancel)
        self.conItem.add_widget(B)
        self.conItem.add_widget(B2)
        self.add_widget(self.root)

    def populateItems(self):
        self.ItemButtons = []
        for item in Combatants.get(0).inventory:
            if item.quantity > 0:
                btn = ToggleButton(text=item.name, group='items')
                self.invItem.add_widget(btn)
                self.ItemButtons.append(btn)

    def populateTargs(self):
        self.ComButtons = []
        for c in Combatants.retList():
            btn = ToggleButton(text=c.name, group='targets')
            self.targItem.add_widget(btn)
            self.ComButtons.append(btn)

    def confirmTarget(self, obj):
        hasTarget = False
        hasItem = False
        itemNum = None
        i = 0
        for a in self.ItemButtons:
            if a.state == 'down':
                hasItem = True
                itemNum = i
            i += 1
        i = 0
        for b in self.ComButtons:
            if b.state == 'down':
                hasTarget = True
                Screens[2].Target = Combatants.get(i)
            i += 1
        if hasTarget == True and hasItem == True:
            hasTarget = False
            hasItem = False
            self.targItem.clear_widgets(children=self.ComButtons)
            self.ComButtons.clear()
            self.invItem.clear_widgets(children=self.ItemButtons)
            self.ItemButtons.clear()
            Combatants.get(0).abilitiesUsed = Combatants.get(0).abilitiesUsed + 1
            Screens[2].AbilityButton.disabled = True
            self.manager.current = 'Battle Screen'
            Screens[2].UseItem(itemNum)

    def cancel(self, obj):
        self.targItem.clear_widgets(children=self.ComButtons)
        self.ComButtons.clear()
        self.invItem.clear_widgets(children=self.ItemButtons)
        self.ItemButtons.clear()
        self.manager.current = 'Battle Screen'

class CombatApp(App):
    def build(self):
        CS = ConnectionScreen(name="Connection Screen")
        sm.add_widget(CS)
        AM = ActionMenu(name="Action Menu")
        Screens.append(AM)
        sm.add_widget(AM)
        AbM = AbilityMenu(name="Ability Menu")
        Screens.append(AbM)
        sm.add_widget(AbM)
        return sm

class BattleScene():
    def __init__(self):
        if isDM == True:
            self.Initiative()
    
    def Initiative(self):
        for c in Combatants.retList():
            c.CT = random.randint(0, 100)

    def getTurn(self):
        if isDM == True:
            Combatants.retList().sort(key = lambda Combatant: Combatant.CT, reverse = True)
            while Combatants.get(0).CT < 100:
                self.ClockTick()
        prompt = Combatants.getName(0)
        return prompt

    def ClockTick(self):
        for c in Combatants.retList():
            if c.HP > 0:
                c.CT += 5

class main():
    CombatApp().run()

if __name__ == '__main__':
    main()
