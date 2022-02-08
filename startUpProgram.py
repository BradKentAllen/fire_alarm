#!/usr/bin/env python
# -*- coding: utf-8 -*-
# startUpProgram.py
'''startUpProgram makes it easy to set up RPi to
automatically start your machine on boot.  By 
calling startUpProgram, you can start any program.
Note how you can uncomment lines to reach into a 
directory.

AditNW LLC, Redmond , WA
www.AditNW.com
'''

#### uncomment these two lines to start a program
# in a directory
#import sys
#sys.path.insert(1, './<directory>)

import fire_alarm as startProgram

if __name__ == '__main__':
    startProgram.remote_startUp()