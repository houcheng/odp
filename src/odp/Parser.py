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
from Config import GroupConfig, ActionConfig, Config, OdpConfig

class Line:
    def __init__(self):
        self.ident = 0
        self.content = ''


def process_line(line):
    id= 0
    for i in range(len(line)):
        if(line[i]==' '):
            id = id+1
        elif(line[i]=='\t'):
            id = id+8
        else:
            break
    line = line.strip()
    if line.find('#') >= 0:
        line = line[:line.find('#')]
    line = line.strip()
    if line == '':
        return None
    ret = Line()
    ret.ident = id
    ret.content = line
    return ret


class LineLex:
    '''
        get line based token to paser
            a) removing comments and empty lines
            b) providing preview
    '''
##    LEX_GROUP_STATE = 1
##    LEX_ACTION_STATE = 2

    def __init__(self, lines):
        lines = [ process_line(line) for line in lines ]
        self.pend_lines = []
        for l in lines:
            if l == None:
                continue
            self.pend_lines.append(l)
##        for tok in self.pend_lines:
##            print 'tok:"%s"' % tok.content
##        self.pend_tokens = []
##        self.state = LineLex.LEX_GROUP_STATE

    def getNextToken(self):
        if len(self.pend_lines)>0:
            t =self.pend_lines[0]
            self.pend_lines = self.pend_lines[1:]
            return t
        return None
    def previewNextToken(self):
        if len(self.pend_lines)>0:
            return self.pend_lines[0]
        return None


class Parser:

    def __init__(self, fd):
        self.lex = LineLex(fd.readlines())

    def parse(self):
        oc = OdpConfig()
        for c in self.parseConfig():
            oc.append(c)
        return oc

    def parseConfig(self):
        '''
        call other parser and yield config back
        '''
        ac = None
        while self.lex.previewNextToken() != None:
            tok = self.lex.previewNextToken()
            if tok.content =='machine:' or tok.content =='role:' or tok.content =='project:':
                yield(self.parseGroup())
            elif tok.content =='action:':
                yield(self.parseAction())
            else:
                raise Exception('wrong label at "%s"' % tok.content)

    def parseGroup(self):
        nametok = self.lex.getNextToken()
        config = GroupConfig(nametok.content[:-1])
        ident = self.lex.previewNextToken().ident
        while self.lex.previewNextToken().ident == ident:
            tok = self.lex.getNextToken()
            line = tok.content
            name = line.split('=')[0].strip()
            right = line.split('=')[1].strip()
            iplist = []
            for ips in right.split(','):
                ips = ips.strip()
                if ips.find('-') > 0:
                    start =  int( ips.split('-')[0].split('.')[3])
                    end =  int(ips.split('-')[1])
                    for i in range(start, end+1):
                        ip = '%s.%s.%s.%d' % ( ips.split('-')[0].split('.')[0], ips.split('-')[0].split('.')[1], ips.split('-')[0].split('.')[2], i)
                        iplist.append(ip)
                else:
                    ip = ips
                    iplist.append(ip)
            config.add_group(name, iplist)
        return config

    # only yield one actionconfig in normal case
    def parseAction(self):
        nametok = self.lex.getNextToken()
        config = ActionConfig(nametok.content[:-1])
        first_ident = self.lex.previewNextToken().ident
        second_ident = 0
        pending_action = None
        while self.lex.previewNextToken()!= None and self.lex.previewNextToken().ident > 0:
            tok = self.lex.getNextToken()
            # learn second_ident immediate after get
            if tok.ident > first_ident and second_ident == 0:
                second_ident = tok.ident
            if tok.ident == first_ident:
                if tok.content[-1]!=':':
                    raise Exception('Invalid action name %s' % tok.content)
                if pending_action != None:
                    config.add_action(pending_action, steps)
                steps = []
                pending_action = tok.content[:-1]
                continue
            elif tok.ident == second_ident:
                steps.append(tok.content)
            else:
                raise Exception('ident error at %s'% tok.content)
        if pending_action != None:
            config.add_action(pending_action, steps)
        return config

def test():
    fd = open('../../doc/homedc.cfg')
    parser = Parser(fd)
    oc = parser.parse()
    for c in oc.configs:
        config = oc.configs[c]
        if config.__class__ == GroupConfig:
            print 'group config:', config.name
            print config.groups
        elif config.__class__ == ActionConfig:
            print 'action config:', config.name
            print config.actions
    for aa in oc.actions:
        print aa, oc.actions[aa]
    for gg in oc.groups:
        print gg, oc.groups[gg]

if __name__ == '__main__':
    test()
