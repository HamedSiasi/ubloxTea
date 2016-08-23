#!/usr/bin/env python
# testRun.py
import sys, os, time, threading, serial
import multiprocessing
import subprocess
from tabulate import tabulate

numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,26]
results = []
tests = ["mbed_drivers-c_strings",
         "mbed_drivers-callback",
         "mbed_drivers-dev_null",
         "mbed_drivers-echo",
         "mbed_drivers-generic_tests",
         "mbed_drivers-rtc",
         "mbed_drivers-stl_features",
         "mbed_drivers-ticker",
         "mbed_drivers-ticker_2",
         "mbed_drivers-ticker_3",
         "mbed_drivers-timeout",
         "mbed_drivers-wait_us",
         "mbedmicro-mbed-attributes",
         "mbedmicro-mbed-call_before_main",
         "mbedmicro-mbed-cpp",
         "mbedmicro-mbed-div",
         "mbedmicro-mbed-heap_and_stack",
         "mbedmicro-rtos-mbed-basic",
         "mbedmicro-rtos-mbed-isr",
         "mbedmicro-rtos-mbed-mail",
         "mbedmicro-rtos-mbed-mutex",
         "mbedmicro-rtos-mbed-queue",
         "mbedmicro-rtos-mbed-semaphore",
         "mbedmicro-rtos-mbed-signals",
         "mbedmicro-rtos-mbed-threads",
         "mbedmicro-rtos-mbed-timer"]



def testsCompile():
        subprocess.call("cls", shell=True)
        #subprocess.call("mbed test -c", shell=True)
        
def flash():
	#1
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\c_strings\\mbed-os-tests-mbed_drivers-c_strings.bin", shell=True)
	results.append(listen())
	#2
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\callback\\mbed-os-tests-mbed_drivers-callback.bin", shell=True)
	results.append(listen())
	#3
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\dev_null\\mbed-os-tests-mbed_drivers-dev_null.bin", shell=True)
	results.append(listen())
	#4
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\echo\\mbed-os-tests-mbed_drivers-echo.bin", shell=True)
	results.append(listen())
	#5
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\generic_tests\\mbed-os-tests-mbed_drivers-generic_tests.bin", shell=True)
	results.append(listen())
	#6
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\rtc\\mbed-os-tests-mbed_drivers-rtc.bin", shell=True)
	results.append(listen())
	#7
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\stl_features\\mbed-os-tests-mbed_drivers-stl_features.bin", shell=True)
	results.append(listen())
	#8
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\ticker\\mbed-os-tests-mbed_drivers-ticker.bin", shell=True)
	results.append(listen())
	#9
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\ticker_2\\mbed-os-tests-mbed_drivers-ticker_2.bin", shell=True)
	results.append(listen())
	#10
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\ticker_3\\mbed-os-tests-mbed_drivers-ticker_3.bin", shell=True)
	results.append(listen())
	#11
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\timeout\\mbed-os-tests-mbed_drivers-timeout.bin", shell=True)
	results.append(listen())
	#12
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbed_drivers\\wait_us\\mbed-os-tests-mbed_drivers-wait_us.bin", shell=True)
	results.append(listen())
	#13
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-mbed\\attributes\\mbed-os-tests-mbedmicro-mbed-attributes.bin", shell=True)
	results.append(listen())
	#14
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-mbed\\call_before_main\\mbed-os-tests-mbedmicro-mbed-call_before_main.bin", shell=True)
	results.append(listen())
	#15
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-mbed\\cpp\\mbed-os-tests-mbedmicro-mbed-cpp.bin", shell=True)
	results.append(listen())
	#16
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-mbed\\div\\mbed-os-tests-mbedmicro-mbed-div.bin", shell=True)
	results.append(listen())
	#17
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-mbed\\heap_and_stack\\mbed-os-tests-mbedmicro-mbed-heap_and_stack.bin", shell=True)
	results.append(listen())
	#18
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\basic\\mbed-os-tests-mbedmicro-rtos-mbed-basic.bin", shell=True)
	results.append(listen())
	#19
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\isr\\mbed-os-tests-mbedmicro-rtos-mbed-isr.bin", shell=True)
	results.append(listen())
	#20
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\mail\\mbed-os-tests-mbedmicro-rtos-mbed-mail.bin", shell=True)
	results.append(listen())
	#21
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\mutex\\mbed-os-tests-mbedmicro-rtos-mbed-mutex.bin", shell=True)
	results.append(listen())
	#22
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\queue\\mbed-os-tests-mbedmicro-rtos-mbed-queue.bin", shell=True)
	results.append(listen())
	#23
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\semaphore\\mbed-os-tests-mbedmicro-rtos-mbed-semaphore.bin", shell=True)
	results.append(listen())
	#24
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\signals\\mbed-os-tests-mbedmicro-rtos-mbed-signals.bin", shell=True)
	results.append(listen())
	#25
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\threads\\mbed-os-tests-mbedmicro-rtos-mbed-threads.bin", shell=True)
	results.append(listen())
	#26
	subprocess.call("FlashErase.exe -c A -s e7000 -l 10000 -v -d -f ..\.build\\tests\\SARA_NBIOT_EVK\\GCC_ARM\\mbed-os\\TESTS\\mbedmicro-rtos-mbed\\timer\\mbed-os-tests-mbedmicro-rtos-mbed-timer.bin", shell=True)
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
        table =( [
         [numbers[0], tests[0],results[0]],
         [numbers[1], tests[1],results[1]],
         [numbers[2], tests[2],results[2]],
         [numbers[3], tests[3],results[3]],
         [numbers[4], tests[4],results[4]],
         [numbers[5], tests[5],results[5]],
         [numbers[6], tests[6],results[6]],
         [numbers[7], tests[7],results[7]],
         [numbers[8], tests[8],results[8]],
         [numbers[9], tests[9],results[9]],
         [numbers[10], tests[10],results[10]],
         [numbers[11], tests[11],results[11]],
         [numbers[12], tests[12],results[12]],
         [numbers[13], tests[13],results[13]],
         [numbers[14], tests[14],results[14]],
         [numbers[15], tests[15],results[15]],
         [numbers[16], tests[16],results[16]],
         [numbers[17], tests[17],results[17]],
         [numbers[18], tests[18],results[18]],
         [numbers[19], tests[19],results[19]],
         [numbers[20], tests[20],results[20]],
         [numbers[21], tests[21],results[21]],
         [numbers[22], tests[22],results[22]],
         [numbers[23], tests[23],results[23]],
         [numbers[24], tests[24],results[24]],
         [numbers[25], tests[25],results[15]]
         ])
        print ""
        print tabulate(table, headers=["TEST NUMBER","TEST NAME","RESULTS"], tablefmt="orgtbl")


if __name__ == "__main__":
        try:
                testsCompile()
                flash()
                printResults()
        except:
                print "oops something went wrong ..."
                print "python testRun.py"
