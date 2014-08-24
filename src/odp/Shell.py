#!/usr/bin/env python
import weakref
import npyscreen
import curses
import select, os
from npyscreen import MultiLine
from SshSession import SshSession

class OdpControl:
    def __init__(self, p):
        self.parent = p
        self.ssh_active = ''
        self.ssh_connect = False
        self.ssh_group = 'all'
        self.ssh = {}  
    def parse(self, command_line):
            if command_line == 'test':
                self.parent.value.set_values([command_line+str(x) for x in range(5)])
                self.parent.wMain.values = self.parent.value.get()
                self.parent.update_sessions(self.ssh_active, self.ssh)
            elif command_line == 'connect':
                self.connect()
            elif command_line == 'll':
                self.parent.value.set_values([command_line+str(x) for x in range(250)])
                self.parent.wMain.values = self.parent.value.get()
                self.parent.wMain.display()
                self.parent.update_sessions(self.ssh_active, self.ssh)                
            else:
                self.feed(command_line)
    def feed(self, command):
        alive_names= filter(lambda x: self.ssh[x].status>0, self.ssh.keys())
        wfiles = map(lambda x: self.ssh[x].getStdin(), alive_names)
        for wfile in wfiles:
            #print 'write command to '+str(wfile)
            wfile.write(command)
            wfile.write('\n')
    def load(self):
        self.ssh = {'test1': SshSession('test1'), 'test2':SshSession('test2'), 'test3':SshSession('test3')}
        self.ssh_active = 'test1'
        self.parent.update_sessions(self.ssh_active, self.ssh)
    def connect(self):
        for x in self.ssh:
            self.ssh[x].connect()
        self.ssh_connect = True
    def pollfd(self):
        update= False
        if self.ssh_connect:
            alive_names= filter(lambda x: self.ssh[x].status>0, self.ssh.keys())
            rlist = map(lambda x: self.ssh[x].getStdout().fileno(), alive_names)
            rlist2 = map(lambda x: self.ssh[x].getStderr().fileno(), alive_names)
            fd2name ={}
            for i in range(len(rlist)):
                fd2name[rlist[i]] = alive_names[i]
            for i in range(len(rlist2)):
                fd2name[rlist2[i]] = alive_names[i] + '_stderr'
            rlist += rlist2
            (rlist, wlist, elist) = select.select(rlist, [], [], 0) # no blocking select
            return [fd2name[rfd] for rfd in rlist]
        return []
    def readfd(self, names):
        for n in names:
            if n.find('_stderr')>=0:
                # if no error, return an ack and terminal print $
                # what's value of ack?
                n=n.replace('_stderr', '')
                buf = os.read(self.ssh[n].getStderr().fileno(), 128000)
            else:
                buf = os.read(self.ssh[n].getStdout().fileno(), 128000)
            self.ssh[n].buffer += buf
    # return (activec_changed, background changed)
    def poll(self):
        bchg = False
        achg = False
        while True:
            names = self.pollfd()
            if len(names)==0:
                return (achg, bchg)
            bchg = True
            if self.ssh_active in names:
                achg = True
            self.readfd(names)
        
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


'''
    do the synchronization between UI and odpControl
'''
class OdpMainForm(npyscreen.FormMuttActive):
    ACTION_CONTROLLER = ActionControllerOdp
    COMMAND_WIDGET_CLASS = MyTextCommandBox
    MAIN_WIDGET_CLASS = MultiLine
    def setupOdp(self):
        self.count = 0
        self.count2 = 0
        self.odpControl = OdpControl(self)
        self.odpControl.load()
        # fixed the while_waiting issue
        self.keypress_timeout = 5
    def update_sessions(self, active, sessions):
        self.count2= self.count2 + 1
        self.wStatus1.value = '('+ str(self.count) + '.' + str(self.count2) +') [' + active +']' 
        for x in sessions:
                self.wStatus1.value += ' '+x
        self.wStatus1.display()
        self.wMain.display()
    def while_waiting(self):
        (achg, bchg) = self.odpControl.poll()
        if achg:
                self.wMain.values = self.odpControl.ssh[self.odpControl.ssh_active].buffer.split('\n') 
                self.wMain.display()
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
