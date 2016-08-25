#!/usr/bin/env python
# testRun.py
import sys, os, time, threading, serial
import multiprocessing
import subprocess
import fnmatch
from tabulate import tabulate

# TODO: pass in target and toolchain on the command-line as options
rootDir = "..\\..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM"
testCaseTimeoutSeconds = 30
binaries = []

# Look for .bin files iteratively from rootDir and append their name and full path to binaries
def findBinaries():
    for root, subFolders, fileNames in os.walk(rootDir):
        for fileName in fnmatch.filter(fileNames, "*.bin"):
            binary = {}
            binary["name"] = fileName
            binary["path"] = os.path.join(root, fileName)
            binary["tests"] = {}
            binaries.append(binary)

# Flash the binaries onto the board and run the tests
def loadAndRun():
    for index, binary in enumerate(binaries):
        subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -d -f " + binary["path"], shell = True)
        binaries[index]["tests"] = listen()

# Listen to the serial output to ascertain test progress
#
# Here is a sample pattern of test output:
# {{__testcase_count;2}}
# >>> Running 2 test cases...
#{{__testcase_name;Simple Test}}
#{{__testcase_name;Repeating Test}}
# >>> Running case #1: 'Simple Test'...
#{{__testcase_start;Simple Test}}
#{{__testcase_finish;Simple Test;1;0}}
# >>> 'Simple Test': 1 passed, 0 failed
# >>> Running case #2: 'Repeating Test'...
#{{__testcase_start;Repeating Test}}
#Setting up for 'Repeating Test'
#{{__testcase_finish;Repeating Test;1;0}}
# >>> 'Repeating Test': 1 passed, 0 failed
# >>> Running case #2: 'Repeating Test'...
#{{__testcase_start;Repeating Test}}
#Setting up for 'Repeating Test'
#{{__testcase_finish;Repeating Test;2;0}}
# >>> 'Repeating Test': 2 passed, 0 failed
# >>> Test cases: 2 passed, 0 failed
#{{__testcase_summary;2;0}}
#{{end;success}}
#{{__exit;0}}
def listen():
    numTests = 0
    tests = []
    start = time.time()
    state = 0;
    line = ""
    ser = serial.Serial(port = "COM124", baudrate = 9600, timeout = 1)
    
    while time.time() - start < testCaseTimeoutSeconds and not ("{{__exit" in line and "}}" in line):
        line = ser.readline()
        print line
        parts = line.split(";")
        
        # First wait for the test case count
        if state == 0:
            if numTests > 0:
                state += 1
            else:
                if len(parts) > 1 and "{{__testcase_count" in parts[0] and "}}" in parts[1]:
                    numTests = int(parts[1].split("}}")[0])
                    
        # Next grab the names of the test cases from the list at the start
        if state == 1:
            if len(tests) == numTests:
                state += 1
            else:
                if len(parts) > 1 and "{{__testcase_name" in parts[0] and "}}" in parts[1]:
                    test = {}
                    test["name"] = parts[1].split("}}")[0]
                    test["runs"] = []
                    tests.append(test)

        # Next grab the result of having started and finished each test
        if state == 2:
            if len(parts) > 1 and getIndex(parts[1].split("}}")[0], tests) >= 0:
                idx = getIndex(parts[1].split("}}")[0], tests)
                if "{{__testcase_start" in parts[0] and "}}" in parts[1]:
                    run = {}
                    run["pass"] = 0
                    run["fail"] = 0
                    tests[idx]["runs"].append(run)
                if len(parts) > 3 and "{{__testcase_finish" in parts[0] and "}}" in parts[3]:
                    numRuns = len(tests[idx]["runs"])
                    if numRuns > 0:
                        # NOTE: the pass/fail count captured here is cumulative across runs of the same test
                        # but I have also seen it jump (i.e. intermediate steps are not reported)
                        tests[idx]["runs"][numRuns - 1]["pass"] = int(parts[2])
                        tests[idx]["runs"][numRuns - 1]["fail"] = int(parts[3].split("}}")[0])                

    return tests

# Given an associative array (tests), find the item for which the key 'name' matches the parameter name
def getIndex(name, tests):
    retValue = -1
    for index, test in enumerate(tests):
        if test["name"] == name:
            retValue = index
    return retValue

# Print out the results of running the tests
def printResults():
    totalTests = 0
    totalRuns = 0
    totalPasses = 0
    totalFails = 0
    totalNotRuns = 0
    totalInconclusive = 0
    table = []
    for binary in binaries:
        for test in binary["tests"]:
            totalTests += 1
            passes = 0
            fails = 0
            runs = len(test["runs"])
            if runs > 0:
                passes = test["runs"][runs - 1]["pass"]
                fails = test["runs"][runs - 1]["fail"]
                inconclusive = runs - (passes + fails)
                # Sometimes the intermediate runs are not reported, so it is possible to
                # get 1 run with 10 passes.  It is clearer here to report the number
                # of runs including these intermediates
                if inconclusive > 0:
                    totalInconclusive += inconclusive
                else:
                    runs = passes + fails
                totalRuns += runs
            else:
                totalNotRuns += 1
            entry = [totalTests, binary["name"].split(".bin")[0], test["name"], runs, passes, fails]
            table.append(entry)
            totalPasses += passes
            totalFails += fails
    print ""
    print tabulate(table, headers=["", "Image", "Test", "Runs", "Passes", "Fails"], tablefmt = "orgtbl")
    print ""
    print "Build(s): {0}".format(len(binaries))
    print "Test(s): {0}".format(totalTests)
    print "Run(s): {0}".format(totalRuns)
    print "Passed: {0} ({1}%)".format(totalPasses, totalPasses * 100 / totalRuns)
    print "Failed: {0} ({1}%)".format(totalFails, totalFails * 100 / totalRuns)
    print "Did not run: {0} ({1}%)".format(totalNotRuns, totalNotRuns * 100 / totalRuns)
    print "No result: {0} ({1}%)".format(totalInconclusive, totalInconclusive * 100 / totalRuns)

# main()
if __name__ == "__main__":
    try:
        findBinaries()
        loadAndRun()
        printResults()
    except:
        print "Oops something went wrong..."
        print "python testRun.py"
