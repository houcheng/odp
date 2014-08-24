import time
import subprocess
import select
import sys
# (connect T/F, proc, buffer)
# status 0:nc, 1:connect 
class SshSession:
    def __init__(self, host):
        # self.connect = False
        self.proc = None
        self.buffer = ''
        self.status = 0
        self.host = host
    def connect(self):
        print 'connect to dest %s' % self.host
        self.proc = subprocess.Popen( ['ssh', 'localhost'], 
            stdin = subprocess.PIPE,
            stdout =  subprocess.PIPE,# sys.stdout,
            stderr =  subprocess.PIPE, # sys.stdout, # subprocess.PIPE,
            close_fds=True)
    # every one tick, poll status of proc, stdout and stderr
    # return (boolean, boolean, boolean) indicate state changes
    def poll(self):
        # if fail connect, return (F/F/F)
        # if output buffer, append to buffer and set newoutput=True
        # if err buffer, append to buffer and set newerr = True
        return (True, self.newoutput, self.newerr)
    def getText(self):
        return self.buffer
    def issueCommand(self, command):
        self.newerr = False
    def getStdin(self):
        return self.proc.stdin
    def getStdout(self):
        return self.proc.stdout
    def getStderr(self):
        return self.proc.stderr

def main():
    sess = SshSession()
    sess.connect()
    print 'select'
    while True:
        # print 'enter select'
        (rlist, wlist, elist) = select.select([0, sess.getStdout().fileno(), sess.getStderr().fileno()], [], [])
        if 0 in rlist:
                # read or readlines() will till EOF
                commands = sys.stdin.readline() 
                sess.getStdin().write(commands)
        if sess.getStdout().fileno() in rlist:
                print sess.getStdout().readline(),
        if sess.getStderr().fileno() in rlist:
                print sess.getStderr().readline(),

if __name__ == '__main__':
        main()
