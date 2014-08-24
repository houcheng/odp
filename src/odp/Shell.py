#!/usr/bin/env python
import weakref
import npyscreen
import curses
from SshSession import SshSession

class OdpControl:
    def __init__(self, p):
        self.parent = p
        self.ssh = {}  
        self.active = '' # active ssh
        self.connect = False
        self.group = 'all'
    def parse(self, command_line):
            if command_line == 'test':
                self.parent.value.set_values([command_line+str(x) for x in range(5)])
                self.parent.wMain.values = self.parent.value.get()
                self.parent.update_sessions(self.active, self.ssh)
            elif command_line == 'connect':
                self.ssh['test1'].connect()
            else:
                self.parent.value.set_values([command_line+str(x) for x in range(250)])
                self.parent.wMain.values = self.parent.value.get()
                self.parent.wMain.display()
                self.parent.update_sessions(self.active, self.ssh)
    def load(self):
        print 'load test config'
        self.ssh = {'test1': SshSession('test1'), 'test2':SshSession('test2')}
        self.active = 'test1'
        self.parent.update_sessions(self.active, self.ssh)
    def connect(self):
        for x in self.ssh:
                self.ssh[x].connect()

# parser here
class ActionControllerOdp(npyscreen.ActionControllerSimple):
    def create(self):
        # self.add_action('^/.*', self.set_search, True)
        # self.add_action('.*', self.issue_cmd, True)
        pass
    def process_command_live(self, command_line, control_widget_proxy):
    	if command_line=='KEY_LEFT':
		self.parent.value.set_values(['LEFT'+str(x) for x in range(3)])
		self.parent.wMain.values = self.parent.value.get()
		self.parent.wMain.display()
    	elif command_line == 'KEY_RIGHT':
		self.parent.value.set_values(['RIGHT'+str(x) for x in range(3)])
		self.parent.wMain.values = self.parent.value.get()
		self.parent.wMain.display()
    def process_command_complete(self, command_line, control_widget_proxy):
            self.parent.odpControl.parse(command_line)
    def while_waiting(self):
        self.parent.while_waiting()

class MyTextCommandBox(npyscreen.TextCommandBox):
    def __init__(self, screen, 
                    history=False, 
                    history_max=100, 
                    set_up_history_keys=True,
                    *args, **keywords):
        super(MyTextCommandBox, self).__init__(screen, history=history, history_max=history_max, 
        	set_up_history_keys=set_up_history_keys, *args, **keywords)
        self.keypress_timeout = 5
    def set_up_handlers(self):
        super(MyTextCommandBox, self).set_up_handlers()
        self.handlers.update({
                   curses.ascii.NL:     self.h_execute_command,
                   curses.ascii.CR:     self.h_execute_command,
                   curses.KEY_F1: self.h_pass_left_command,
                   curses.KEY_F2: self.h_pass_right_command,
#                   "^g":     self.kick, not working
#                   "^G":     self.kick,
        })
        self.keypress_timeout = 5
    def h_pass_left_command(self, command):
    	self.parent.action_controller.process_command_live('KEY_LEFT', weakref.proxy(self))
    def h_pass_right_command(self, command):
    	self.parent.action_controller.process_command_live('KEY_RIGHT', weakref.proxy(self))
    def while_waiting(self):
        self.parent.while_waiting()

class OdpMainForm(npyscreen.FormMuttActive):
    ACTION_CONTROLLER = ActionControllerOdp
    COMMAND_WIDGET_CLASS = MyTextCommandBox
    keypress_timeout_default = 5
    def setupOdp(self):
        self.count = 0
        self.count2 = 0
        self.odpControl = OdpControl(self)
        self.odpControl.load()
        self.keypress_timeout = 5
    def update_sessions(self, active, sessions):
        self.count2= self.count2 + 1
        self.wStatus1.value = '('+ str(self.count) + '.' + str(self.count2) +') [' + active +']' 
        for x in sessions:
                self.wStatus1.value += ' '+x
        self.wStatus1.display()
        self.wMain.display()
    def while_waiting(self):
        self.count = self.count +1
        self.wStatus1.value = '('+ str(self.count) + '.' + str(self.count2) +') [' 
        self.wStatus1.display()


'''

'''
class TestApp(npyscreen.NPSAppManaged):
    keypress_timeout_default = 5
    def main(self):
        F = OdpMainForm()
        F.wStatus1.value = "Console Output"
        F.wStatus2.value = "Command"
        F.value.set_values([str(x) for x in range(500)])
        F.wMain.values = F.value.get()
        F.setupOdp()
        F.edit()
        #print 'ha'
        #self.F = F
    def while_waiting(self):
        self.F.while_waiting()



if __name__ == "__main__":
    App = TestApp()
    App.run()
