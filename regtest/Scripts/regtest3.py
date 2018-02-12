#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-09 17:10:02
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121

import sys

path = input('Please input your filepath')

print('input filepath is %s, arg1 is %s, arg2 is %s' %
      (path, sys.argv[1], sys.argv[2]))
