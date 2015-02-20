# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Manager of backupstore
@since   : 22/08/2014
@describe: PyBackupStore/src/manager/__init__.py -v --sync --data "D:\Conf LB" --repo "D:\backup"
'''
#Standard package
import os
import sys


currentPath = os.path.abspath(sys.argv[0] + os.sep + '..' + os.sep + '..')
sys.path.append(currentPath)


#Internal package
import manager.main




if __name__ == '__main__':
    manager.main.main()