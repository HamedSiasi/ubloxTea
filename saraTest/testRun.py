#!/usr/bin/env python
# testRun.py
import sys, os, time, threading, serial
import multiprocessing
import subprocess
import fnmatch
from tabulate import tabulate

# Where the built binaries are placed
# TODO: pass in target and toolchain on the command-line as options and then this can be generated from that
rootDir = "..\\..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM"
# Skip the STDIO redirect tests entirely as they require the PC side to be involved and don't even give
# a test count at the start
skipBinariesEntirely = ["dev_null.bin"]
# Skip running the tests from the echo binary as they require the PC side to be involvd
skipBinariesTests = ["echo.bin"]
# Skip this test as the %f formatter doesn't seem to work out of the box for nano.specs
skipTests = ["C strings: %f %f float formatting"]
# This needs to be more than 30 seconds for one of the ticker tests
testCaseTimeoutSeconds = 60
# All the test data is stored here
binaries = []

# Look for .bin files iteratively from rootDir and append their name and full path to binaries
def findBinaries():
    for root, subFolders, fileNames in os.walk(rootDir):
        for fileName in fnmatch.filter(fileNames, "*.bin"):
            if fileName not in skipBinariesEntirely:
                binary = {}
                binary["name"] = fileName
                binary["path"] = os.path.join(root, fileName)
                binary["skipped"] = False
                binary["tests"] = {}
                if binary["name"] in skipBinariesTests:
                    binary["skipped"] = True
                binaries.append(binary)
            else:
                print "Skipping binary '{0}' entirely.".format(fileName)

# Flash the binaries onto the board and run the tests
def loadAndRun():
    for index, binary in enumerate(binaries):
        subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -d -f " + binary["path"], shell = True)
        binaries[index]["tests"] = listen(binary["skipped"])

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
def listen(listOnly):
    stopNow = False
    numTests = 0
    tests = []
    start = time.time()
    state = 0;
    line = ""
    ser = serial.Serial(port = "COM124", baudrate = 9600, timeout = 1)
    
    while time.time() - start < testCaseTimeoutSeconds and not ("{{__exit" in line and "}}" in line) and not stopNow:
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
                if listOnly:
                    stopNow = True
            else:
                if len(parts) > 1 and "{{__testcase_name" in parts[0] and "}}" in parts[1]:
                    testName = parts[1].split("}}")[0]
                    test = {}
                    test["name"] = parts[1].split("}}")[0]
                    test["runs"] = []
                    test["skipped"] = listOnly
                    if testName in skipTests:
                        test["skipped"] = True
                    tests.append(test)

        # Next grab the result of having started and finished each test
        if state == 2 and not stopNow:
            if len(parts) > 1 and getIndex(parts[1].split("}}")[0], tests) >= 0:
                index = getIndex(parts[1].split("}}")[0], tests)
                if not tests[index]["skipped"]:
                    if "{{__testcase_start" in parts[0] and "}}" in parts[1]:
                        run = {}
                        run["pass"] = 0
                        run["fail"] = 0
                        tests[index]["runs"].append(run)
                    if len(parts) > 3 and "{{__testcase_finish" in parts[0] and "}}" in parts[3]:
                        numRuns = len(tests[index]["runs"])
                        if numRuns > 0:
                            # NOTE: the pass/fail count captured here is cumulative across runs of the same test
                            # but I have also seen it jump (i.e. intermediate steps are not reported), so
                            # grab the result from the end
                            tests[index]["runs"][numRuns - 1]["pass"] = int(parts[2])
                            tests[index]["runs"][numRuns - 1]["fail"] = int(parts[3].split("}}")[0])

            # Some test cases check that failures are caused, i.e. they come up as failures and that is the
            # intended outcome.  So that we don't keep thinking the darned things are a problem, capture
            # the test cases summary and, if the number of passes is equal to the number of tests and the
            # number of failures is zero, make sure that the pass count for each test is at max. and the
            # fail count is zero
            # Can only realistically do this if each test case is run once (because not all of the intermediate
            # runs are always reported we don't know know how many runs represent a pass)
            if len(parts) > 2 and "{{__testcase_summary" in parts[0] and "}}" in parts[2]:
                if int(parts[1]) == numTests and int(parts[2].split("}}")[0]) == 0:
                    runOnce = True
                    for test in tests:
                        if len(test["runs"]) != 1:
                            runOnce = False
                    if runOnce:
                        for test in tests:
                            test["runs"][0]["pass"] = 1
                            test["runs"][0]["fail"] = 0
                state += 1

    return tests

# Given an associative array (tests[]), find the item for which the key 'name' matches the parameter name
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
    totalSkipped = 0
    totalInconclusive = 0
    table = []
    for binary in binaries:
        for test in binary["tests"]:
            if not test["skipped"]:
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
            else:
                passes = 0
                fails = 0
                runs = 0
                totalSkipped += 1
            entry = [totalTests, binary["name"].split(".bin")[0], test["name"], runs, test["skipped"], passes, fails]
            table.append(entry)
            totalPasses += passes
            totalFails += fails
    print ""
    print tabulate(table, headers=["", "Image", "Test", "Runs", "Skipped", "Passes", "Fails"], tablefmt = "orgtbl")
    print ""
    print "Build(s): {0}".format(len(binaries))
    print "Test(s): {0}".format(totalTests)
    print "Run(s): {0}".format(totalRuns)
    print "Passed: {0} ({1}%)".format(totalPasses, totalPasses * 100 / totalRuns)
    print "Failed: {0} ({1}%)".format(totalFails, totalFails * 100 / totalRuns)
    print "No result: {0} ({1}%)".format(totalInconclusive, totalInconclusive * 100 / totalRuns)
    print "Skipped: {0}".format(totalSkipped)
    print "Tests that should have run and did not: {0}".format(totalNotRuns)

# main()
if __name__ == "__main__":
    try:
        findBinaries()
        loadAndRun()
        printResults()
    except:
        print "Oops something went wrong..."
        print "python testRun.py"
