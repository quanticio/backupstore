# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Manager of backupstore
@since   : 04/12/2014
'''
#Standard package
import os
import unittest
import tempfile
import subprocess


#Internal package
import manager
import core.operations




class Test(unittest.TestCase):


    def setUp(self):
        self.DictDumpParam = {'DBBASE':     'test_backupstore',
                              'TARGETFILE_STD': tempfile.gettempdir() + os.sep + 'test_backupstore.bkp', 
                              'TARGETFILE_SQL': tempfile.gettempdir() + os.sep + 'test_backupstore.sql', 
                              'TOOLS':      'C:\\Program Files (x86)\\pgAdmin III\\1.18\\pg_dump', # TO CUSTOMIZE
                              'HOST':       'localhost',                                           # TO CUSTOMIZE
                              'PORT':       '5432',                                                # TO CUSTOMIZE
                              'USER':       'postgres', 
                              'PWD' :       ''}
        
        self.DictRestoreParam = {'DBBASE':     'test_backupstore',
                                 'SOURCEFILE_STD': tempfile.gettempdir() + os.sep + 'test_backupstore.bkp', 
                                 'SOURCEFILE_SQL': tempfile.gettempdir() + os.sep + 'test_backupstore.sql', 
                                 'TOOLS_STD':      'C:\\Program Files (x86)\\pgAdmin III\\1.18\\pg_restore', # TO CUSTOMIZE
                                 'TOOLS_SQL':      'C:\\Program Files (x86)\\pgAdmin III\\1.18\\psql',       # TO CUSTOMIZE
                                 'HOST':       'localhost',                                             # TO CUSTOMIZE
                                 'PORT':       '5432',                                                       # TO CUSTOMIZE
                                 'USER':       'postgres', 
                                 'PWD' :       ''}


    def tearDown(self):
        pass


    def test1_ParseConnectionString(self):
        ''' Test parseConnectionString function '''
        self.assertEqual(manager.config.parseConnectionString('postgres:mypWD:44@localhost:5432'), ('localhost', '5432', 'postgres', 'mypWD:44'))
        self.assertEqual(manager.config.parseConnectionString(':mypWD:44@localhost:5432'), ('localhost', '5432', 'postgres', 'mypWD:44'))
        self.assertEqual(manager.config.parseConnectionString('postgres:mypWD:44@localhost'), ('localhost', '5432', 'postgres', 'mypWD:44'))
        self.assertEqual(manager.config.parseConnectionString('postgres:mypWD:44@:5432'), ('localhost', '5432', 'postgres', 'mypWD:44'))
        self.assertEqual(manager.config.parseConnectionString('postgres:@localhost:5432'), ('localhost', '5432', 'postgres', ''))
        self.assertEqual(manager.config.parseConnectionString('postgres@localhost:5432'), ('localhost', '5432', 'postgres', ''))
        self.assertEqual(manager.config.parseConnectionString('localhost'), ('localhost', '5432', 'postgres', ''))
        self.assertEqual(manager.config.parseConnectionString('localhost:5432'), ('localhost', '5432', 'postgres', ''))
        self.assertEqual(manager.config.parseConnectionString(''), ('localhost', '5432', 'postgres', ''))
    
    
    def test2_DumpToStdFormat(self):
        ''' Dump to Standard format (custom format for postgres) '''
        # product dump file
        self.assertTrue(core.operations.dump.dataBase(self.DictDumpParam['DBBASE'], target=self.DictDumpParam['TARGETFILE_STD'], tools=self.DictDumpParam['TOOLS'], 
                                                      host=self.DictDumpParam['HOST'], port=self.DictDumpParam['PORT'], user=self.DictDumpParam['USER'], 
                                                      password=self.DictDumpParam['PWD'], dumptype='std', verbose=False).getResult(), msg='Fail to dump with standard format.')
        # testing exist file
        self.assertTrue(os.path.isfile(self.DictDumpParam['TARGETFILE_STD']), msg="Fail to dump to standard format. Output file don't exist")
        # testing if the file is not empty
        self.assertNotEqual(os.stat(self.DictDumpParam['TARGETFILE_STD']).st_size, 0, msg="Dump file is empty")
    
    
    def test3_RestoreToStdFormat(self):
        ''' Restore to Standard format (custom format for postgres) '''
        lstCommands = ("select pg_terminate_backend(pid) from pg_stat_activity where datname='%s'" % self.DictRestoreParam['DBBASE'], 
                       "DROP DATABASE IF EXISTS %s" % self.DictRestoreParam['DBBASE'], 
                       "CREATE DATABASE %s WITH OWNER=%s" % (self.DictRestoreParam['DBBASE'], self.DictRestoreParam['USER']), )
        for cmd in lstCommands:
            subprocess.call('"%s" -h %s -p %s -U %s -w -F plain --quiet -c "%s;"' % (self.DictRestoreParam['TOOLS_SQL'], self.DictRestoreParam['HOST'], self.DictRestoreParam['PORT'], self.DictRestoreParam['USER'], cmd) ,
                            stderr=subprocess.STDOUT, shell=True)
        
        self.assertTrue(core.operations.restore.dataBase(self.DictRestoreParam['DBBASE'], restoreFile=self.DictRestoreParam['SOURCEFILE_STD'], tools=self.DictRestoreParam['TOOLS_STD'], 
                                                      host=self.DictRestoreParam['HOST'], port=self.DictRestoreParam['PORT'], user=self.DictRestoreParam['USER'], 
                                                      password=self.DictRestoreParam['PWD'], dumptype='std', verbose=False).getResult(), msg='Fail to restore with standard format.')
    
    
    def test4_DumpToSqlFormat(self):
        ''' Dump to SQL format (custom format for postgres) '''
        # product dump file
        self.assertTrue(core.operations.dump.dataBase(self.DictDumpParam['DBBASE'], target=self.DictDumpParam['TARGETFILE_SQL'], tools=self.DictDumpParam['TOOLS'], 
                                                      host=self.DictDumpParam['HOST'], port=self.DictDumpParam['PORT'], user=self.DictDumpParam['USER'], 
                                                      password=self.DictDumpParam['PWD'], dumptype='sql', verbose=False).getResult(), msg='Fail to dump with standard format.')
        # testing exist file
        self.assertTrue(os.path.isfile(self.DictDumpParam['TARGETFILE_SQL']), msg="Fail to dump to standard format. Output file don't exist")
        # testing if the file is not empty
        self.assertNotEqual(os.stat(self.DictDumpParam['TARGETFILE_SQL']).st_size, 0, msg="Dump file is empty")
    
    
    def test5_RestoreToSqlFormat(self):
        ''' Restore to SQL format (custom format for postgres) '''
        self.assertTrue(core.operations.restore.dataBase(self.DictRestoreParam['DBBASE'], restoreFile=self.DictRestoreParam['SOURCEFILE_SQL'], tools=self.DictRestoreParam['TOOLS_SQL'], 
                                                      host=self.DictRestoreParam['HOST'], port=self.DictRestoreParam['PORT'], user=self.DictRestoreParam['USER'], 
                                                      password=self.DictRestoreParam['PWD'], dumptype='sql', verbose=False).getResult(), msg='Fail to restore with sql format.')
    
    
    def test6_ShortDumpToStdFormat(self):
        ''' Dump to Standard format (custom format for postgres) '''
        # product dump file
        self.assertTrue(core.operations.dump.dataBase(self.DictDumpParam['DBBASE'], target=self.DictDumpParam['TARGETFILE_STD'] + '.short').getResult(), msg='Fail to dump with standard format in the localhost database.')
        # testing exist file
        self.assertTrue(os.path.isfile(self.DictDumpParam['TARGETFILE_STD']), msg="Fail to dump to standard format. Output file don't exist")
        # testing if the file is not empty
        self.assertNotEqual(os.stat(self.DictDumpParam['TARGETFILE_STD']).st_size, 0, msg="Dump file is empty")
    
    
    def test7_ShortRestoreToStdFormat(self):
        ''' Restore to Standard format (custom format for postgres) '''
        lstCommands = ("select pg_terminate_backend(pid) from pg_stat_activity where datname='%s'" % self.DictRestoreParam['DBBASE'], 
                       "DROP DATABASE IF EXISTS %s" % self.DictRestoreParam['DBBASE'], 
                       "CREATE DATABASE %s WITH OWNER=postgres" % self.DictRestoreParam['DBBASE'], )
        for cmd in lstCommands:
            subprocess.call('"%s" -h %s -p %s -U %s -w -F plain --quiet -c "%s;"' % (self.DictRestoreParam['TOOLS_SQL'], self.DictRestoreParam['HOST'], self.DictRestoreParam['PORT'], self.DictRestoreParam['USER'], cmd) ,
                            stderr=subprocess.STDOUT, shell=True)
        
        self.assertTrue(core.operations.restore.dataBase(self.DictRestoreParam['DBBASE'], restoreFile=self.DictRestoreParam['SOURCEFILE_STD'] + '.short', tools=self.DictRestoreParam['TOOLS_STD']).getResult(), 
                        msg='Fail to restore with standard format in the localhost database')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=10)