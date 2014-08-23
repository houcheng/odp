#!/usr/bin/env python
import weakref
import npyscreen
import curses

class ActionControllerSearch(npyscreen.ActionControllerSimple):
    def create(self):
        #self.add_action('^/.*', self.set_search, True)
        #self.add_action('.*', self.issue_cmd, True)
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
	self.parent.value.set_values([command_line+str(x) for x in range(250)])
	self.parent.wMain.values = self.parent.value.get()
	self.parent.wMain.display()
    def issue_cmd(self, command_line, widget_proxy, live):
    	#if len(command_line) > 0:
    	#	self.command = command_line
    	#	return
    	#self.parent.value.set_values([command_line, command_line, command_line, len(command_line)])
    	#
    	#self.command = command_line
    	#self.parent.value.set_values([self.command+str(x) for x in range(100)])
        #self.parent.wMain.values = self.parent.value.get()
        #self.parent.wMain.display()
        pass

class MyTextCommandBox(npyscreen.TextCommandBox):
    def __init__(self, screen, 
                    history=False, 
                    history_max=100, 
                    set_up_history_keys=True,
                    *args, **keywords):
        super(MyTextCommandBox, self).__init__(screen, history=history, history_max=history_max, 
        	set_up_history_keys=set_up_history_keys, *args, **keywords)
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
    def h_pass_left_command(self, command):
    	self.parent.action_controller.process_command_live('KEY_LEFT', weakref.proxy(self))
    def h_pass_right_command(self, command):
    	self.parent.action_controller.process_command_live('KEY_RIGHT', weakref.proxy(self))

class FmSearchActive(npyscreen.FormMuttActive):
    ACTION_CONTROLLER = ActionControllerSearch
    COMMAND_WIDGET_CLASS = MyTextCommandBox

class TestApp(npyscreen.NPSApp):
    def main(self):
        F = FmSearchActive()
        F.wStatus1.value = "Status Line "
        F.wStatus2.value = "Second Status Line "
        F.value.set_values([str(x) for x in range(500)])
        F.wMain.values = F.value.get()
        F.edit()



if __name__ == "__main__":
    App = TestApp()
    App.run()