#!/usr/bin/env python

import sys
import subprocess

def get_class_list(binPath):
    clsList = [];
    cmd = "class-dump "+binPath
    output = subprocess.check_output(cmd.split());

    for line in output.split('\n'):
        parsedLine = ""
        if line.find('@interface') != -1 and line.find('(') == -1:
            parsedLine = line.replace('@interface','')
            parsedLine = line.replace(':', '\n')
            for subline in parsedLine.split('\n'):
                if subline.find('@interface') != -1:
                    clsList.append(subline.replace('@interface ',''))
    return clsList


def listDiff(listA, listB):
    set_a = set(listA)
    set_b = set(listB)
    diff = set_a.difference(set_b);
    return sorted(list(diff))



if len(sys.argv) < 3:
    print "Usage: "+sys.argv[0]+"<first binary> <second binary>"
    exit(1)

firstBinPath = sys.argv[1]
secondBinPath = sys.argv[2]

firstBinDump = get_class_list(firstBinPath)
secondBinDump = get_class_list(secondBinPath)

print "Classes in "+ firstBinPath + " not in " + secondBinPath + ":"
for l in listDiff(firstBinDump,secondBinDump):
    print "\t"+l


print ""
print "Classes in "+ secondBinPath + " not in " + firstBinPath + ":"
for l in listDiff(secondBinDump,firstBinDump):
    print "\t"+l
