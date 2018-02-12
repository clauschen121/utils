#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-07 16:07:43
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


import os
import glob
import time
import sys
from subprocess import Popen, PIPE


testdir = sys.argv[1] if len(sys.argv) > 1 else os.curdir
testdir = os.path.abspath(testdir)
print('开始执行回归测试，时间：', time.asctime())
print('执行目录：%s' % testdir)

testpattern = os.path.join(testdir, 'Scripts', '*.py')
testfiles = glob.glob(testpattern)
testfiles.sort()

numfail = 0

for testfile in testfiles:
    testname = os.path.basename(testfile)

    infile = testname.replace('.py', '.in')
    inpath = os.path.join(testdir, 'Inputs', infile)
    indata = open(inpath, 'rb').read() if os.path.exists(inpath) else b''

    argfile = testname.replace('.py', '.args')
    argpath = os.path.join(testdir, 'Args', argfile)
    argdata = open(argpath).read() if os.path.exists(argpath) else ''

    outfile = testname.replace('.py', '.out')
    outpath = os.path.join(testdir, 'Outputs', outfile)
    outpathbad = outpath + '.bad'
    if os.path.exists(outpathbad):
        os.remove(outpathbad)

    errfile = testname.replace('.py', '.err')
    errpath = os.path.join(testdir, 'Errors', errfile)
    if os.path.exists(errpath):
        os.remove(errpath)

    pypath = sys.executable
    command = '%s %s %s' % (pypath, testfile, argdata)

    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    process.stdin.write(indata)
    process.stdin.close()
    outdata = process.stdout.read()
    errdata = process.stderr.read()
    exitstatus = process.wait()

    if exitstatus != 0:
        print('ERROR status:', testname, exitstatus)
    if errdata:
        print('ERROR stream:', testname, errpath)
        open(errpath, 'wb').write(errdata)
    if exitstatus or errdata:
        numfail += 1
        open(outpathbad, 'wb').write(outdata)
    elif not os.path.exists(outpath):
        print('generating:', outpath)
        open(outpath, 'wb').write(outdata)

    else:
        priorout = open(outpath, 'rb').read()
        if priorout == outdata:
            print('passed:', testname)
        else:
            numfail += 1
            print('FAILED output:', testname, outpathbad)
            open(outpathbad, 'wb').write(outdata)
