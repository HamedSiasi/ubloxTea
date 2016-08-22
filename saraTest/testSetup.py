#!/usr/bin/env python
# testSetup.py
import sys, os, time, threading, serial
import multiprocessing
import subprocess

def copyFiles():
    subprocess.call("rmdir ..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS /s", shell=True)
    subprocess.call("mkdir ..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS", shell=True)
    subprocess.call("xcopy TESTS ..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS /s /e /h", shell=True)
    
    print "Delete the original test_env.cpp ..."
    subprocess.call("del ..\\..\\mbed-os\\features\\frameworks\\greentea-client\\source\\test_env.cpp", shell=True)
    print "Copy the new test_env.cpp ..."
    subprocess.call("copy test_env.cpp_new ..\\..\\mbed-os\\features\\frameworks\\greentea-client\\source\\test_env.cpp", shell=True)

    print "Delete the original utest_default_handlers.cpp ..."
    subprocess.call("del ..\\..\\mbed-os\\features\\frameworks\\utest\\source\\utest_default_handlers.cpp", shell=True)
    print "Copy the new utest_default_handlers.cpp ..."
    subprocess.call("copy utest_default_handlers.cpp_new ..\\..\\mbed-os\\features\\frameworks\\utest\\source\\utest_default_handlers.cpp", shell=True)

    

def installPackets():
    subprocess.call("pip install tabulate", shell=True)
    

if __name__ == "__main__":
    try:
        copyFiles()
        installPackets()
        print ""
        print "all done!"
        print "now python testSetup.py"
    except:
        print "oops something went wrong ..."
