#-------------------------------------------------------------------------------
# Name:        Runner
# Purpose:     Job/ action/step Runner defined here
#              Corresonding logs is also defined here
# Author:      Houcheng
#
# Created:     19/11/2012
# Copyright:   (c) 980255 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from Logger import Log, Logger, JobLog
import os

class Path:
    odp_home = '%s/.odp/' % os.environ['HOME']
    odp_var = '%s/.odp/var/' % os.environ['HOME']
    odp_host = '%s/.odp/hosts/' % os.environ['HOME']
    odp_log = '%s/.odp/log/' % os.environ['HOME']


class JobRunner:
    def __init__(self, config):
        self.config = config
        self.ar = ActionRunner()  # delegate
        self.prepareEnv()
    def prepareEnv(self):
        for dir in [ Path.odp_host, Path.odp_log, Path.odp_var]:
            os.system('mkdir -p %s' % dir)
            os.system('rm -f %s/*' % dir)
        for g in self.config.groups:
            fd = open( '%s/%s' % (Path.odp_host, g), 'w')
            for ip in self.config.groups[g]:
                fd.write('%s\n' % ip)
            fd.close()

    def run(self, gname, actnames):
        jrlog = JobLog()
        for act in actnames:
            localname = '%s:%s' % (gname, act)
            if localname in self.config.actions:
                act = localname
            steplist = self.config.actions[act]
            arlog = self.ar.run(gname, act, steplist )
            jrlog.append(arlog)
            if arlog.status != 0:
                jrlog.status = arlog.status
                break


class ActionRunner:
    '''
    aggregate continuous local or remote commands into a bulk and delegate to ParallelRunner to run
    '''
    def __init__(self):
        self.sr = ParallelRunner() # delegate

    def run(self, gname, actname, steplist):
        cmds = []
        for step in steplist:
            if (step[0]=='$' or step[0]=="'") and len(cmds) > 0 :
                srlog = self.sr.runRemoteCmds(gname, actname, cmds)
                if srlog.status != 0:
                    break
            if step[0]=='$':
                srlog = self.sr.runMacroCmd(gname, step)
            elif step[0]== "'":
                srlog = self.sr.runLocalCmd(gname, step)
            else:
                cmds.append(step)
                continue
            if srlog.status != 0:
                break
        if len(cmds) > 0:
                srlog = self.sr.runRemoteCmds(gname, actname, cmds)
        return srlog # need modify to arlog

class ParallelRunner:
    def __init__(self):
        self.count = 0
        self.gname = ''
    def runLocalCmd(self, gname, stmt):
        words = stmt[1:]
        ret = os.system(words)
        return Log(ret)
    def runMacroCmd(self, gname, stmt):
        os.system('rm -f ~/.odp/out/*')
        os.system('rm -f ~/.odp/err/*')
        words = stmt[1:].split(' ')
        if words[0] == 'put':
                print 'Put files %s to remote hosts group (%s)' % (words[1], gname)
                ret = os.system('parallel-scp -p 10 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s %s ~/%s' % (gname, words[1], words[1].split('/')[-1]))
                return Log(ret)
        if words[0] == 'sync':
            if os.path.isdir(words[1]):
                fn = words[1]
                if fn[-1] == '/':
                    fn = fn[:-1]
                sfn = fn.split('/')[-1]
                print 'Sync directory %s/ to remote hosts group (%s)' % (words[1], gname)
                ret = os.system('rm -f %s.tgz' % (sfn))
                ret = os.system('tar czvf %s.tgz %s' % (sfn, fn))
                if(ret != 0):
                    return Log(ret)
                ret = os.system('parallel-scp -p 10 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s %s.tgz ~/%s.tgz' % (gname, sfn, sfn))
                if(ret != 0):
                    return Log(ret)
                ret = os.system('parallel-ssh -p 10 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s "rm -fr %s; tar xzvf %s.tgz; rm -f %s.tgz"' % (gname, sfn, sfn, sfn))
                if(ret != 0):
                    return Log(ret)
                ret = os.system('rm -f %s.tgz' % sfn)
                return Log(ret)
            else:
                print 'Sync file %s to remote hosts group (%s)' % (words[1], gname)
                ret = os.system('parallel-scp -p 10 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s %s ~/%s' % (gname, words[1], words[1].split('/')[-1]))
                return Log(ret)
        return Log(100)

    def runRemoteCmds(self, gname, aname, steps):
        if self.gname != gname:
            self.count = 0
        fn ='%s/%s_%d.sh'% (Path.odp_var, aname, self.count)
        fd = open(fn, 'w')
        fd.write('set -e\n')
        fd.write('set -x\n')
        for step in steps:
            fd.write('%s\n'% step)
        fd.close()
        os.system('rm -f ~/.odp/out/*')
        os.system('rm -f ~/.odp/err/*')
        print 'Put script %s to remote hosts group (%s)' % (fn.split('/')[-1], gname)
        ret = os.system('parallel-scp -p 10 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s %s ~/%s' % (gname, fn, fn.split('/')[-1]))
        if ret!= 0:
            return Log(ret)
        print 'Execute script %s in remote hosts group (%s)' % (fn.split('/')[-1], gname)
        ret = os.system('parallel-ssh -p 10 -t 0 -o ~/.odp/out -e ~/.odp/err -h ~/.odp/hosts/%s "bash %s"' % (gname, fn.split('/')[-1]))
        return Log(ret)

def test():
    from Parser import Parser
    fd = open('../../doc/homedc.cfg')
    parser = Parser(fd)
    oc = parser.parse()
    runner = JobRunner(oc)

if __name__ == '__main__':
    test()
