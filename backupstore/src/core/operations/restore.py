# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Restore operation
@since   : 22/08/2014
'''
#Standard package
import os
import zipfile
import tarfile
import tempfile
import subprocess


#Internal package
import core.common.tools
import core.common.backupstoredbfile




class restoreFileSystem(object):
    ''' restoreFileSystem class definition '''
    verbose         = False
    archive         = None
    target          = None
    CompressionType = 'zip'
    
    
    def __init__(self, archive, target, verbose):
        ''' Constructor
        @param archive: Path of archive file (format zip, tar, gzip, bz2 (automatic research)
        @param target: Target folder
        @param verbose: Verbosity mode '''
        self.verbose = verbose
        
        if self.verbose:
            print("Execute restoreFileSystem with this option :\narchive=%s\ntarget=%s" % (archive, target))
        
        self.CompressionType = core.common.tools.getArchiveCompressionType(archive)
        
        if os.path.isfile(target):
            raise IOError("Restore impossible : The target path is a file, a folder is required")
        elif not os.path.isdir(target):
            os.mkdir(target)
        
        self.archive = archive
        self.target = target
    
    
    def restoreAll(self):
        ''' Restore all archive '''
        if self.verbose:
            print("Execute restoreFileSystem.restoreAll")
        
        if self.CompressionType == 'zip':
            with zipfile.ZipFile(self.archive, 'r') as currentzip:
                currentzip.extractall(self.target)
        elif self.CompressionType in ('tar', 'gzip', 'bz2'):
            mode = 'r'
            if self.CompressionType == 'gzip':
                mode += ':gz'
            elif self.CompressionType == 'bz2':
                mode += ':bz2'
            with tarfile.open(self.archive, mode) as currenttar:
                currenttar.extractall(self.target)
    
    
    def restoreById(self, ids):
        ''' Restore a list ids '''
        if self.verbose:
            print("Execute restoreFileSystem.restoreById with this option :\nids=%s" % str(ids))
        
        backupStoreFile = self.__getTemporaryBackupStoreFile()
        obj_backupstoredbfile = core.common.backupstoredbfile.BackupStoreDbFile(backupStoreFile)
        
        obj_backupstoredbfile.open()
        
        objList = []
        ids = ids.split(",")
        for Id in ids:
            obj = obj_backupstoredbfile.getFSObjById(int(Id.strip()), WithParent=True)
            if obj is not None and obj.isFolder():
                objList.extend(obj_backupstoredbfile.getSubTree(int(Id.strip()), WithParent=True))
            else:
                objList.append(obj)
        obj_backupstoredbfile.close()
        os.remove(backupStoreFile)
        os.rmdir(os.path.dirname(backupStoreFile))
        
        lstReleaseId = []
        if self.CompressionType == 'zip':
            with zipfile.ZipFile(self.archive, 'r') as currentzip:
                for i, obj in enumerate(objList):
                    if obj is not None:
                        # Filtering between the same id
                        if obj.id not in lstReleaseId:
                            currentzip.extract(obj.path + os.sep + obj.name, self.target)
                            lstReleaseId.append(obj.id)
                    else:
                        print("Warning: id(%s) is unknown. The file will not be restored." % ids[i])
        elif self.CompressionType in ('tar', 'gzip', 'bz2'):
            mode = 'r'
            if self.CompressionType == 'gzip':
                mode += ':gz'
            elif self.CompressionType == 'bz2':
                mode += ':bz2'
            with tarfile.open(self.archive, mode) as currenttar:
                for i, obj in enumerate(objList):
                    if obj is not None:
                        # Filtering between the same id
                        if obj.id not in lstReleaseId:
                            currenttar.extract('.' + obj.relativePath + '/' + obj.name, self.target)
                            lstReleaseId.append(obj.id)
                    else:
                        print("Warning: id(%s) is unknown. The file will not be restored." % ids[i])
    
    
    
    
    def __getTemporaryBackupStoreFile(self):
        ''' Get a temporary backupStoreFile (.backupstore) '''
        tmp = tempfile.gettempdir() + os.sep + os.path.basename(self.archive)
        if self.CompressionType == 'zip':
            obj_zipfile = zipfile.ZipFile(self.archive, 'r')
            obj_zipfile.extract('.backupstore', tmp)
            obj_zipfile.close()
        else:
            currenttar = None
            if self.CompressionType == 'tar':
                currenttar = tarfile.open(self.archive, 'r')
            elif self.CompressionType == 'gzip':
                currenttar = tarfile.open(self.archive, 'r:gz')
            elif self.CompressionType == 'bz2':
                currenttar = tarfile.open(self.archive, 'r:bz2')
                
            if currenttar is not None:
                currenttar.extract('./.backupstore', tmp)
                currenttar.close()
            else:
                raise IOError("Research impossible : The archive path is not a compatible archive")
        
        return tmp + os.sep + '.backupstore'




class dataBase(object):
    ''' Restore database class definition  '''
    
    
    def __init__(self, dataBase, restoreFile, tools='pg_restore', host='localhost', port='5432', user='postgres', password=None, dumptype='std', verbose=True):
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
        
        dumptype = dumptype.lower()
        if not dumptype:
            dumptype = 'std'
        if password == '':
            password = None
        if not verbose and dumptype == 'sql':
            trace = '--quiet'
        elif verbose and dumptype != 'sql':
            trace = '--verbose'
        else:
            trace = ''
        
        if dumptype == 'sql':
            if password is None:
                result = subprocess.call('"%s" -h %s -p %s -U %s -w -F plain %s -f "%s"' %(tools, host, port, user, trace, restoreFile),stderr=subprocess.STDOUT, shell=True)
            else:
                result = subprocess.call('"%s" -h %s -p %s -U %s -W %s -F plain %s -f "%s"' %(tools, host, port, user, password, trace, restoreFile), stderr=subprocess.STDOUT, shell=True)
        else:
            if password is None:
                result = subprocess.call('"%s" -h %s -p %s -U %s -w -F custom %s -d %s "%s"' %(tools, host, port, user, trace, dataBase, restoreFile),stderr=subprocess.STDOUT, shell=True)
            else:
                result = subprocess.call('"%s" -h %s -p %s -U %s -W %s -F custom %s -d %s "%s"' %(tools, host, port, user, password, trace, dataBase, restoreFile), stderr=subprocess.STDOUT, shell=True)
        
        if result == 0:
            self.result = True
            if verbose:
                print "The %s database was imported from  : %s" % (dataBase, restoreFile)
        elif verbose:
            print "Fail to import %s database from : %s" % (dataBase, restoreFile)
    
    
    def getResult(self):
        ''' Getting result of restoration operation '''
        return self.result