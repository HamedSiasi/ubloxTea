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
                binary["badExit"] = False
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
        binaries[index]["tests"] = listen(binary)

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
def listen(binary):
    stopNow = False
    listOnly = False
    numTests = 0
    tests = []
    start = time.time()
    state = 0;
    line = ""
    ser = serial.Serial(port = "COM124", baudrate = 9600, timeout = 1)
    
    if binary["skipped"]:
        listOnly = True
        
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
                # Some test cases don't emit a count, they just skip straight to listing the test names
                if len(parts) == 1 and ">>> Running " in parts[0] and "test cases..." in parts[0]:
                    numTests = -1
                    state += 1
                    
        # Next grab the names of the test cases from the list at the start
        if state == 1:
            if numTests >= 0 and len(tests) == numTests:
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
                #  Catch the case where we never had a count at the outset
                if len(parts) == 1 and ">>> Running case " in parts[0] and "..." in parts[0]:
                    numTests = len(tests)
                    state += 1
                    if listOnly:
                        stopNow = True

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
            # Can only realistically do this if each test case is run once (because we don't know know
            # how many runs represent a pass)
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
    # If we've hit the exit line, check that the exit code is zero.  If it is not, flag the test as "bad exit"
    if "{{__exit" in line and "}}" in line and len(parts) > 1 and not int(parts[1].split("}}")[0]) == 0:
        binary["badExit"] = True

    return tests

# Given an associative array (tests[]), find the item for which the key "name" matches the parameter name
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
    totalUnstructuredOutput = 0
    totalBadExit = 0
    table = []
    for binary in binaries:
        badExitText = ""
        if binary["badExit"]:
            totalBadExit += 1
            badExitText = "x"
        if len(binary["tests"]) > 0:
            for test in binary["tests"]:
                runs = 0
                passes = 0
                fails = 0
                notRuns = 0
                inconclusive = 0
                if not test["skipped"]:
                    totalTests += 1
                    if len(test["runs"]) > 0:
                        for run in test["runs"]:
                            runs += 1
                            passes += run["pass"]
                            fails += run["fail"]
                        if passes == 0 and fails == 0:
                            inconclusive += 1
                    else:
                        notRuns += 1
                else:
                    totalSkipped += 1
                skipText = ""
                if test["skipped"]:
                    skipText = "x"
                entry = [totalTests, binary["name"].split(".bin")[0], test["name"], runs, skipText, passes, fails, badExitText]
                table.append(entry)
                totalRuns += runs
                totalPasses += passes
                totalFails += fails
                totalNotRuns += notRuns
                totalInconclusive += inconclusive
        else:
            totalUnstructuredOutput += 1
            entry = ["--", binary["name"].split(".bin")[0], "[unstructured test output]", "", "", "", "", badExitText]
            table.append(entry)
    print ""
    print tabulate(table, headers=["", "Image", "Test", "Runs", "Skip?", "Passes", "Fails", "Bad Exit?"], tablefmt = "orgtbl")
    print ""
    print "Build(s): {0}".format(len(binaries))
    print "Test(s): {0}".format(totalTests)
    print "Run(s): {0}".format(totalRuns)
    print "Passed: {0} ({1}%)".format(totalPasses, totalPasses * 100 / (totalPasses + totalFails))
    print "Failed: {0} ({1}%)".format(totalFails, totalFails * 100 / (totalPasses + totalFails))
    print "No result: {0} ({1}%)".format(totalInconclusive, totalInconclusive * 100 / totalRuns)
    print "Skipped: {0}".format(totalSkipped)
    print "Tests that should have run and did not: {0}".format(totalNotRuns)
    print "Builds that did not emit structured output: {0}".format(totalUnstructuredOutput)
    print "Builds that did not exit cleanly: {0}".format(totalBadExit)

# main()
if __name__ == "__main__":
    try:
        findBinaries()
        loadAndRun()
        printResults()
    except:
        print "Oops something went wrong..."
        print "python testRun.py"
