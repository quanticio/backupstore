# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : All dump definition (dumpFileSystem, etc...)
@since   : 22/08/2014
'''
#Standard package
import os
import time
import subprocess


#Internal package
import core.common.rsyncbootstrap as rsyncbootstrap
import core.common.backupstoredbfile as backupstoredbfile
import core.common.metaoperation as metaoperation
import core.common.tools as tools




class dumpFileSystem(object):
    ''' checksum class definition '''
    FileSysOrig           = None
    repository            = None
    verbose               = False
    
    
    def __init__(self, FileSysOrig, Repository, checksum, compression, compressionLevel, compressionAlgo, Verbose):
        ''' Constructor
        @param FileSysOrig: Files system to backup
        @param Repository: Repository path
        @param checksum: checksum to sign the file
        @param compression: compression boolean to compress the archive
        @param compressionLevel: level compression for zlib using
        @param compressionAlgo: Algorithm to use [zlib, zip, tar, gzip, bz2]
        @param Verbose: Verbosity mode '''
        self.checksum          = checksum
        self.compression       = compression
        self.compressionLevel  = compressionLevel
        self.compressionAlgo   = compressionAlgo
        self.verbose           = Verbose
        self.BackupStoreDbFile = None
        self.objChrono         = tools.chrono()
        
        if self.verbose:
            print("Execute dumpFileSystem with this option :\nFileSysOrig=%s\nRepository=%s\nchecksum=%s\ncompression=%s\ncompressionLevel=%s\ncompressionAlgo=%s" % (FileSysOrig, Repository, checksum, compression, compressionLevel, compressionAlgo))
        if os.path.isdir(FileSysOrig) or os.path.isfile(FileSysOrig):
            self.FileSysOrig = FileSysOrig
        else:
            raise AttributeError('The files system to save is not a directory or a file.')
        if os.path.isfile(Repository):
            raise AttributeError('The repository target is not a directory but a file.')
        elif not os.path.isdir(Repository):
            os.mkdir(Repository)
        self.repository = Repository
        self.BackupStoreDbFile = self.repository + os.sep + '.backupstore'
        
        UpdateMode = True
        if len(os.listdir(self.repository)) == 0:
            UpdateMode = False
        # UpdateMode verify if the '.backupstore' exist else raise an error (it's not a repository)
        elif not os.path.isfile(self.BackupStoreDbFile):
            raise IOError('The repository is not empty yet he has not .backupstore file with the metadata')
        
        obj_backupstoredbfile = backupstoredbfile.BackupStoreDbFile(self.BackupStoreDbFile)
        
        if not UpdateMode:
            obj_backupstoredbfile.create(compression, compressionLevel, compressionAlgo)
    
    
    def dump(self):
        ''' Launch a dump of filesystem with rsync mode '''
        self.objChrono.start()
        
        if self.verbose:
            
            rsyncbootstrap.synchronizeFS(self.FileSysOrig, self.repository, 'delete', 'times', 'recursive', extra_operation=metaoperation.metaOperation(self.checksum, self.compression, self.compressionLevel, self.compressionAlgo, BSDbFile=self.BackupStoreDbFile, Verbose=self.verbose))
        else:
            rsyncbootstrap.synchronizeFS(self.FileSysOrig, self.repository, 'delete', 'times', 'recursive', 'quiet', extra_operation=metaoperation.metaOperation(self.checksum, self.compression, self.compressionLevel, self.compressionAlgo, BSDbFile=self.BackupStoreDbFile, Verbose=self.verbose))
        
        self.objChrono.stop()
        if self.verbose:
            print("Operation execution in %s" % self.objChrono.getTimeInMinutes())




class dataBase(object):
    ''' Dump database class definition '''
    
    
    def __init__(self, dataBase, target='export_%Y-%m-%d__%H-%M-%S.dmp', tools='pg_dump', host='localhost', port='5432', user='postgres', password=None, dumptype='std', verbose=True):
        ''' Constructor
        @param dataBase: String type for database name
        @param target: Target file
        @param tools: Tool to use (ex: pg_dump)
        @param host: String type for host server of database (localhost by default)
        @param port: String type for port instance of database (5432 by default)
        @param user: String type for database user (postgres by default)
        @param password: String type for database password (empty by default (trust authen))
        @param dumptype: std (bin) or sql
        @param verbose: Verbosity mode '''
        self.result = False
        
        if not dumptype:
            dumptype = 'std'
        if password == '':
            password = None
        if verbose:
            trace = '--verbose'
        else:
            trace = ''
        
        target   = time.strftime(target)
        dumptype = dumptype.lower()
        
        if dumptype == 'sql':
            if password is None:
                result = subprocess.call('"%s" -h %s -p %s -U %s -w -F plain --create --clean %s -d  %s -f "%s"' %(tools, host, port, user, trace, dataBase, target),stderr=subprocess.STDOUT, shell=True)
            else:
                result = subprocess.call('"%s" -h %s -p %s -U %s -W %s -F plain --create --clean %s -d %s -f "%s"' %(tools, host, port, user, password, trace, dataBase, target), stderr=subprocess.STDOUT, shell=True)
        else:
            if password is None:
                result = subprocess.call('"%s" -h %s -p %s -U %s -w -F custom %s -d %s -f "%s"' %(tools, host, port, user, trace, dataBase, target),stderr=subprocess.STDOUT, shell=True)
            else:
                result = subprocess.call('"%s" -h %s -p %s -U %s -W %s -F custom %s -d %s -f "%s"' %(tools, host, port, user, password, trace, dataBase, target), stderr=subprocess.STDOUT, shell=True)
        
        if result == 0:
            self.result = True
            if verbose:
                print "Export %s database executed in : %s" % (dataBase, target)
        elif verbose:
            print "Fail export %s database in : %s" % (dataBase, target)
    
    
    def getResult(self):
        ''' Getting result of restoration operation '''
        return self.result