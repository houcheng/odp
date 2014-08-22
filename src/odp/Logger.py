#-------------------------------------------------------------------------------
# Name:        Logger.py
# Purpose:     Logger to log job logs
#
# Author:      980255
#
# Created:     19/11/2012
# Copyright:   (c) 980255 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class ActionLog:
    pass
class JobLog:
    def __init__(self):
        self.logs = []
    def append(self, log):
        self.logs.append(log)

class StepLog:
    pass


class Log:
    def __init__(self, ret):
        self.status = ret

class Logger:
    pass


def main():
    pass

if __name__ == '__main__':
    main()
