"""
Copyright (c) 2018, Christopher Nitta
All rights reserved.

This assembler has been provided to the students of ECS 154A at the University
of California, Davis. It is for class use only and not to be redistributed 
without the written consent of the copyright owner.
"""
import glob
import os
import sys
import csv
import chardet
            
def main():
    if 2 > len(sys.argv):
        print('Syntax Error: str2dat string')
        return
    
    for Char in sys.argv[1]:
        print('DAT #x{:04X}'.format(ord(Char)))
    print('DAT #x0000')

if __name__ == '__main__':
    main()
