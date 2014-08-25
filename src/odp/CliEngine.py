#!/usr/bin/python
import cmd, os, sys, time, traceback, datetime, getopt

from Config import Config, GroupConfig, ActionConfig, OdpConfig
from Parser import Parser
from Runner import JobRunner
def parseParam(pstr):
    pstr = pstr.replace('\t', ' ')
    return(pstr.split(' '))


class ActiveConfigSenity:
    config = None

class CliEngine(cmd.Cmd):
    """
       Simple command processor for ODP.
    """
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.debug = False
        self.config = None
        self.fn = ''
    def feedConfig(self, fn):
        fd = open(fn, 'r')
        parser = Parser(fd)
        self.config = parser.parse()
        self.runner = JobRunner(self.config)
        # config file info
        self.fn = fn
        self.ftime = datetime.datetime.fromtimestamp(os.path.getmtime(self.fn))

    def do_config(self, pstr):
        self.feedConfig(pstr)
        return False

    def do_list(self, pstr):
        for g in self.config.groups:
            print g
            print self.config.groups[g]
        for a in self.config.actions:
            print a
            print self.config.actions[a]
        return False

    def do_run(self, pstr):
        '''
        run <group-name> <action1>, <action2>, ...
        '''
        gname = pstr.split(' ')[0]
        remain = pstr[len(gname):]
        actnames = [ a.strip() for a in remain.split(',') ]
        log = self.runner.run(gname, actnames)
        return False
    def do_err(self, pstr):
        '''
        err: print error message of last step.
        err g: print error message of last step by windows GUI.
        '''
        if pstr.strip() == 'g':
            os.system('gedit ~/.odp/err/*')
        else:
            os.system('less ~/.odp/err/*')

    def do_out(self, pstr):
        '''
        out: print message of last step.
        out g: print message of last step by windows GUI.
        '''
        if pstr.strip() == 'g':
            os.system('gedit ~/.odp/out/*')
        else:
            os.system('less ~/.odp/out/*')

    def emptyline(self):
        return False

    def do_exit(self, pstr):
        '''
        exit
        Description:
            Exit froms shell
        '''
        return True

    def do_EOF(self, pstr):
        return True

    def do_debug(self, pstr):
        '''
        debug : toggle debug mode
        '''
        self.debug = not self.debug
        print 'debug set to ', self.debug

    def precmd(self, pstr):
        ftime = datetime.datetime.fromtimestamp(os.path.getmtime(self.fn))
        if ftime > self.ftime:
            print 'detect config file changed, reload!'
            self.feedConfig(self.fn)
        return pstr

def usage():
    print 'Usage: %s  [ -f <config-file> ] [ cmds ... ]' % sys.argv[0]
    print 'Default config-file is /opt/odp/odp.cfg'




def run_cli_loop(cfgfile):
    print 'usage config file', cfgfile
    cli = CliEngine()
    cli.feedConfig(cfgfile)
    again = True
    while again:
        try:
            again = False
            cli.cmdloop()
        except KeyboardInterrupt:
            pass
        except:
            print "Exception: ", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            again = True

def run_cli_one(cfgfile, args):
    cli = CliEngine()
    cli.feedConfig(cfgfile)
    st = ''
    for i in args:
        st = st + i  + ' '
    cli.onecmd(st)


def run_cli(cfgfile, args):
    if len(args) > 0:
        run_cli_one(cfgfile, args)
    else:
        run_cli_loop(cfgfile)


def main():
    cfgfile = './odp.cfg'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:")
        for o,v in opts:
            if o == '-h' or o == '--help':
                usage()
                sys.exit(0)
            if o=='-f':
                cfgfile=v
    except getopt.GetoptError:
        usage()
        sys.exit(-1)
    run_cli(cfgfile, args)




if __name__ == '__main__':
    main()
