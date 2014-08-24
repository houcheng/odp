import weakref
import npyscreen
import curses
from SshSession import SshSession

class BeepForm(npyscreen.ActionForm):
    def while_waiting(self):
    	print 'he'
        curses.beep()


class TestApp(npyscreen.NPSAppManaged):
    def main(self):
        F = BeepForm()
        F.edit()
    def while_waiting(self):
    	print 'he'
        curses.beep()

if __name__ == "__main__":
    App = TestApp()
    App.run()
