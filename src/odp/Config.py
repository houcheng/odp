#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      980255
#
# Created:     16/11/2012
# Copyright:   (c) 980255 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class Config:
    def __init__(self, name):
        self.name = name
    def getName(self):
        return self.name

class GroupConfig(Config):
    def __init__(self, name):
        Config.__init__(self, name)
        self.groups = {}
    def add_group(self, gname, iplist):
        self.groups[gname] = iplist
    def get_group_hosts(self, gname):
        return self.groups[gname]
    def enum_group_hosts(self, gname):
        for ip in self.groups[gname]:
            yield ip

class ActionConfig(Config):
    def __init__(self, name):
        Config.__init__(self, name)
        self.actions = {}
        self.aa = None
    def add_action(self, aname, steplist):
        self.actions[aname] = steplist
    def get_action_steps(self, gname):
        return self.actions[gname]
    def enum_action_steps(self, gname):
        for step in self.actions[gname]:
            yield step


class OdpConfig:
    def __init__(self):
        self.groups = {}
        self.actions = {}
        self.configs = {}
    def append(self, config):
        self.configs[config.getName()] = config
        if config.__class__ == GroupConfig:
            for g in config.groups:
                self.groups[g] = config.groups[g]
        if config.__class__ == ActionConfig:
            for a in config.actions:
                self.actions[a] = config.actions[a]
def test():
    c = Config('ha')
    g = GroupConfig('machine')
    a = ActionConfig('action')
    print 'done'

if __name__ == '__main__':
    test()
