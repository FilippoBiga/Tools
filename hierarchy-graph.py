#!/usr/bin/env python

import plistlib
import argparse
import subprocess
from os.path import basename, splitext
try:
    import pydot
except Exception, e:
    print "Couldn't import pydot: you will not be able to generate dot or svg files"

# given '@interface Class : Superclass <Whatever>',
# returns [ Class, Superclass ]
def get_class_pair(line):
    # truncate protocols
    if '<' in line:
        line = line[:line.find('<')]
    line = line.replace('@interface','')
    line = line.replace(' ','').replace('\n','')
    return line.split(':')

def find_subclasses(pairs,cls):
    subs = {}
    for k in pairs:
        if pairs[k] == cls:
            subs[k] = find_subclasses(pairs, k)
    if len(subs.keys()) == 0:
        return ""
    return subs

def add_edges(graph, superclass, subclasses):
    for cls in subclasses.keys():
        edge = pydot.Edge(superclass, cls)
        graph.add_edge(edge)
        if type(subclasses[cls]) == type({}):
            add_edges(graph, cls, subclasses[cls])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Binary or header file", required=True)
    parser.add_argument("-o", "--output", help="Output file", required=True)
    parser.add_argument("-f", "--format", help="Output file format (plist, dot, svg). Defaults to svg.", required=False)
    parser.add_argument("-c", "--classdump", help="Path to class-dump[-z]. Defaults to $PATH/class-dump.", required=False)
    arguments = vars(parser.parse_args())

    classPairs={}
    hierarchy = {}

    inputFile = arguments['input']
    outputFile = arguments['output']
    format = "svg"
    classdumpPath = "class-dump-z"

    if arguments['format'] != None:
        format = arguments['format']
        if format != 'svg' and format != 'plist':
            print format + " is not a valid format!"
            exit(-1)

    if arguments['classdump'] != None:
        classdumpPath = arguments['classdump']

    try:
        subprocess.check_output([ classdumpPath ])
        print "Invalid class-dump[-z] path"
    exit(-2)

    headerLines = None
    if inputFile.endswith('.h'):
        f = open(inputFile)
        headerLines = f.readlines()
        f.close()
    else:
        cmd = classdumpPath + " " + inputFile
        headerLines = subprocess.check_output(cmd.split())

    if '@interface' not in headerLines:
        print "This file does not contain any Objective-C runtime information."
        exit(1)
    headerLines = headerLines.split('\n')

    # build a classPairs list of "subclass : superclass"
    for line in headerLines:
        # find @interface declarations but exclude categories
        if '@interface' in line and not '(' in line:
            classes = get_class_pair(line)
            classPairs[classes[0]] = classes[1]

    for k in classPairs.keys():
        # check if the value is also a key,
        # i.e. if the superclass is a root class
        if not classPairs.has_key(classPairs[k]):
            hierarchy[classPairs[k]] = {}

    for c in hierarchy.keys():
        for k in classPairs:
            # recursively find subclasses
            if classPairs[k] == c:
                hierarchy[c][k] = find_subclasses(classPairs, k)

    if format == "plist":
        plistlib.writePlist(hierarchy, outputFile)
    elif format == "svg" or format == "dot":
        graphName = splitext(basename(outputFile))[0]
        graph = pydot.Dot(graph_type='graph',graph_name=graphName,rankdir='LR')
        for rootCls in hierarchy.keys():
            add_edges(graph, rootCls, hierarchy[rootCls])
        graph.write(outputFile, format=format)


