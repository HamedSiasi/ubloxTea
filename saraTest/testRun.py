#!/usr/bin/env python
# testRun.py
import sys, os, time, threading, serial
import multiprocessing
import subprocess
import fnmatch
from tabulate import tabulate

# TODO: pass in target and toolchain on the command-line
rootDir = '..\\..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM'
binPaths = []
binNames = []
results = []

def findBinaries():
    for root, subFolders, fileNames in os.walk(rootDir):
        for fileName in fnmatch.filter(fileNames, '*.bin'):
            binNames.append(fileName)
            binPaths.append(os.path.join(root, fileName))

def flash():
    for path in binPaths:
        subprocess.call('FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ' + path, shell=True)
        results.append(listen())

def listen():
    abort_after = 5 
    start = time.time()
    ser = serial.Serial(port="COM124",baudrate=9600, timeout=1)
    while True:
        delta = time.time() - start
        if delta >= abort_after:
            break
        line = ser.readline()
        print line
        if "0 failed" in line:
            return "PASSED"
    return "FAILED"

def printResults():
    table = []
    count = 0
    for path in binPaths:
        count += 1
        entry = [count, binNames[count - 1], results[count - 1]]
        table.append(entry)
    print ""
    print tabulate(table, headers=["TEST NUMBER","TEST NAME","RESULTS"], tablefmt="orgtbl")

if __name__ == "__main__":
    try:
        findBinaries()
        flash()
        printResults()
    except:
        print "oops something went wrong ..."
        print "python testRun.py"
