# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : BackupStoreDbFile definition
@since   : 22/08/2014
'''
#Standard package
import os
import sqlite3
import time




class BackupStoreFSObjProperty(unicode):
    ''' BackupStoreFSObjectProperty class definition '''
    
    
    def __new__(cls, Id=None, parentId=None, name='', path='', isfolder=False, stat='', checksum='', compress=False, archVerified=False, archSec=False, relativePath=None):
        ''' Setting the properties of file system object
        @param Id: 
        @param name: 
        @param path: 
        @param isfolder: 
        @param stat: 
        @param checksum: 
        @param compress: 
        @param archVerified: 
        @param archSec:  '''
        obj = unicode.__new__(cls, name)
        obj.id           = Id
        obj.parentId     = parentId
        obj.name         = name
        obj.path         = path
        obj.stat         = stat
        obj.checksum     = checksum
        obj.compress     = compress
        obj.archVerified = archVerified
        obj.archSec      = archSec
        obj.relativePath = relativePath
        
        if isfolder is True or isfolder == 1:
            obj.isfolder = True
        else:
            obj.isfolder = False
        
        return obj
    
    
    def isFolder(self):
        ''' Test if object is a folder
        @return: Return True or False '''
        return self.isfolder
    
    
    def isFile(self):
        ''' Test if object is a file
        @return: Return True or False '''
        return not self.isfolder
    
    
    def getPropertyInStat(self, propertyLabel):
        ''' Get a property in stat file
        @return: st_size long '''
        val = self.stat.index(propertyLabel + '=')
        return long(self.stat[val+len(propertyLabel)+1:val + self.stat[val:].index(',')])




class BackupStoreDbFile(object):
    ''' BackupStoreDbFile class definition '''
    TRACE = 1
    INFO  = 2
    DEBUG = 4
    WARN  = 8
    ERROR = 16
    FATAL = 32
    
    
    def __init__(self, filepath):
        ''' Constructor
        @param filepath: .backupstore file path '''
        self.filepath   = filepath
        self.connection = None
        self.cursor     = None
        self.record     = 0
    
    
    def open(self):
        ''' Open the connection with the database '''
        self.__connect()
    
    
    def close(self):
        ''' Open the connection with the database '''
        self.__close()
    
    
    def __connect(self):
        ''' Private method to connect the database '''
        if not self.cursor:
            self.connection = sqlite3.connect(self.filepath)
            self.connection.isolation_level = None
            self.cursor     = self.connection.cursor()
    
    
    def __close(self):
        ''' Private method to connect the database '''
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            self.connection.close()
            self.connection = None
    
    
    def setPaging(self, record=0):
        ''' Use paging for query. Set the index state
        @param record: 0 by default '''
        self.record = record
    
    
    def __execQuery(self, query, withReturn=False):
        ''' Execute query '''
        self.cursor.execute(query)
        if withReturn:
            return self.cursor.fetchone()
    
    
    def create(self, compression, compressionLevel, compressionAlgo):
        ''' Constructor 
        @param filepath: .backupstore file path
        @param compression: compression boolean to compress the archive
        @param compressionLevel: level compression for zlib using
        @param compressionAlgo: Algorithm to use [zlib, zip, tar, gzip, bz2] '''
        self.__connect()
        
        self.__execQuery('''CREATE TABLE BS_config (id INTEGER PRIMARY KEY, date text, time text, compress integer, compressLevel integer, compressAlgo text)''')
        self.__execQuery('''CREATE TABLE BS_filesystem (id INTEGER PRIMARY KEY, parentId integer, name text, path text, isFolder integer, stat text, checksum text, compress integer, archVerified integer, archSec integer)''')
        self.__execQuery('''CREATE TABLE BS_log (id INTEGER PRIMARY KEY, date text, time text, level integer, description text)''')
        self.addConfig(compression, compressionLevel, compressionAlgo)
        
        self.__close()
    
    
    def addConfig(self, compression, compressionLevel, compressionAlgo):
        ''' Add a new config in database
        @param compression: compression boolean to compress the archive
        @param compressionLevel: level compression for zlib using
        @param compressionAlgo: Algorithm to use [zlib, zip, tar, gzip, bz2] '''
        if not compression:
            compression=0
        if not compressionLevel:
            compressionLevel=0
        else:
            compressionLevel = int(compressionLevel)
        if compressionAlgo not in ('zlib', 'zip', 'tar', 'gzip', 'bz2'):
            compressionAlgo = ''
        
        self.__connect()
        
        self.addTrace('Create a new configuration with compress=%d, compressLevel=%d, compressAlgo=%s' % (compression, compressionLevel, compressionAlgo), self.TRACE)
        self.__execQuery('''INSERT INTO BS_config (date, time, compress, compressLevel, compressAlgo) VALUES ('%s', '%s', %d, %d, '%s');''' % (time.strftime("%x"), time.strftime("%X"), compression, compressionLevel, compressionAlgo))
        
        self.__close()
    
    
    def addTrace(self, description, level=2):
        ''' Add trace in log table
        @param level: level of trace (integer ex: 0 for INFO)
        @param description: Description of the trace [(TRACE,1),(INFO,2),(DEBUG,4),(WARN,8),(ERROR,16),(FATAL,32)] '''
        self.__execQuery('''INSERT INTO BS_log (date, time, level, description) VALUES ('%s', '%s', %d, '%s');''' % (time.strftime("%x"), time.strftime("%X"), level, description.replace("'", "''")))
    
    
    def updateFile(self, Id=None, parentId=None, name='', path='', stat='', checksum='', compress=0, archVerified=0, archSec=0):
        ''' Update file in database or insert if it don't exist
        @param Id: Unique id of file
        @param parentId: Parent id (parent folder)
        @param name:Name of file
        @param path: path of folder
        @param checksum: checksum file
        @param compress: compression data (false by default)
        @param param: Verified archive next time the compression (false by default)
        @param param: Secure archive by encryption (false by default)
        '''
        if parentId is None:
            #Search the parentId if parentId isn't given to the method
            result = self.__execQuery('''SELECT id FROM BS_filesystem WHERE isFolder=1 and name='%s' and path='%s';''' % (os.path.basename(path).replace("'", "''"), os.path.dirname(path).replace("'", "''")), True)
            if result is not None:
                parentId = str(result[0])
            else:
                parentId = 'NULL'
        else:
            parentId = str(parentId)
        
        if Id == None:
            #Search the id
            result = self.__execQuery('''SELECT id FROM BS_filesystem WHERE isFolder=0 and name='%s' and path='%s';''' % (name.replace("'", "''"), path.replace("'", "''")), True)
        else:
            result = (Id,)
        
        #No id then we create the record
        if result == None:
            self.__execQuery('''INSERT INTO BS_filesystem (parentId, name, path, isFolder, stat, checksum, compress, archVerified, archSec) VALUES (%s, '%s', '%s', 0, '%s', '%s', %d, %d, %d);''' % (parentId, name.replace("'", "''"), path.replace("'", "''"), stat, checksum, compress, archVerified, archSec))
        
        #have an id then we update the record
        else:
            self.__execQuery('''UPDATE BS_filesystem SET stat='%s', checksum='%s', compress=%d, archVerified=%d, archSec=%d WHERE id=%d''' % (stat, checksum, compress, archVerified, archSec, result[0]))
    
    
    def addFolder(self, path):
        ''' Add a folder in database
        @param path: path of folder '''
        if path not in (None, ''):
            result = self.__execQuery('''SELECT id FROM BS_filesystem WHERE isFolder=1 and name='%s' and path='%s';''' % (os.path.basename(os.path.dirname(path)).replace("'", "''"), os.path.dirname(os.path.dirname(path)).replace("'", "''")), True)
            if result is None:
                self.__execQuery('''INSERT INTO BS_filesystem (parentId, name, path, isFolder) VALUES (NULL, '%s', '%s', 1);''' % (os.path.basename(path).replace("'", "''"), os.path.dirname(path).replace("'", "''")))
            else:
                self.__execQuery('''INSERT INTO BS_filesystem (parentId, name, path, isFolder) VALUES (%d, '%s', '%s', 1);''' % (result[0], os.path.basename(path).replace("'", "''"), os.path.dirname(path).replace("'", "''")))
    
    
    def getObjInFolderList(self, path):
        ''' Get all object filesystem in a folder*
        @param path: path of folder '''
        #TO DO
        objLst = []
        if path not in (None, ''):
            result = self.__execQuery('''SELECT id, parentId, name, path, isFolder, stat, checksum, compress, archVerified, archSec FROM BS_filesystem WHERE path='%s';''' % path.replace("'", "''"), True)
            while result is not None:
                objLst.append(BackupStoreFSObjProperty(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9]))
                result = self.cursor.fetchone()
        return objLst
    
    
    def getFSObj(self, path):
        ''' Get all filesystem object in a folder
        @path: Path to search
        @return: Return a BackupStoreFSObjProperty object '''
        if path not in (None, ''):
            result = self.__execQuery('''SELECT id, parentId, name, path, isFolder, stat, checksum, compress, archVerified, archSec FROM BS_filesystem WHERE name='%s' and path='%s';''' % (os.path.basename(path).replace("'", "''"), os.path.dirname(path).replace("'", "''")), True)
        if result is not None:
            return BackupStoreFSObjProperty(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9])
        else:
            return None
    
    
    def isFolder(self, path):
        ''' Test if the folder exist
        @param path: path of folder '''
        return not self.isFile(os.path.basename(path), os.path.dirname(path))
    
    
    def isFile(self, name, path):
        ''' Test if the file exist
        @param path: path of folder '''
        
        result = self.__execQuery('''SELECT isFolder FROM BS_filesystem WHERE name='%s' AND path='%s';''' % (name.replace("'", "''"), path.replace("'", "''")), True)
        if result is None or result[0] == 1:
            return False
        else:
            return True
    
    
    def removeFileOrFolder(self, Id=None, name='', path=''):
        ''' Remove file in database by id else by name and path
        @param Id: Unique id of file
        @param name:Name of file
        @param path: path of folder '''
        if Id is not None and isinstance(Id, int):
            self.__execQuery('''DELETE FROM BS_filesystem WHERE id=%d;''' % Id)
        elif name is not None and path not in (None, ''):
            self.__execQuery('''DELETE FROM BS_filesystem WHERE name='%s' AND path='%s';'''  % (name.replace("'", "''"), path.replace("'", "''")))
    
    
    def searchFileOrFolder(self, name='', date=''):
        ''' Search file or a folder with an optional filter (by name or by date)
        @param name: String name to search (by like) (name empty by default)
        @param date: String date to search (date empty by default)
        @return: Return a list of tuple (id, parentId, name, path, isFolder, stat) '''
        print date
        filter_criteria = ''
        if name not in (None, ''):
            filter_criteria = " WHERE name like '%" + str(name.replace("'", "''")) + "%'"
        if filter_criteria != '' and date not in (None, ''):
            filter_criteria += " AND stat like '%" + str(date.replace("'", "''")) + "%'"
        elif date not in (None, ''):
            filter_criteria += " WHERE stat like '%" + str(date.replace("'", "''")) + "%'"
        
        self.cursor.execute('''SELECT id, parentId, name, path, isFolder, stat FROM BS_filesystem%s''' % filter_criteria)
        return self.cursor.fetchall()
    
    
    def getFSObjById(self, Id, WithParent=False):
        ''' Get all filesystem object by the id
        @param id: id object
        @param WithParent: Get the relative parent path
        @return: Return a BackupStoreFSObjProperty object '''
        if id not in (None, ''):
            result = self.__execQuery('''SELECT id, parentId, name, path, isFolder, stat, checksum, compress, archVerified, archSec FROM BS_filesystem WHERE id=%d;''' % Id, True)
        if result is not None:
            if WithParent:
                return BackupStoreFSObjProperty(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], relativePath=self.getRelativePath(Id=result[1]))
            else:
                return BackupStoreFSObjProperty(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9])
        else:
            return None
    
    
    def getRelativePath(self, Id):
        ''' Get the relative path
        @param Id: Id of parent
        @return: return a string path '''
        path = ''
        result = self.__execQuery('''SELECT parentId, name FROM BS_filesystem WHERE id=%d;''' % Id, True)
        if result is not None:
            while result is not None and result[0] not in (None, ''):
                path = '/' + result[1] + path
                result = self.__execQuery('''SELECT parentId, name FROM BS_filesystem WHERE id=%d;''' % result[0], True)
            if result is not None:
                path = '/' + result[1] + path
        return path
    
    
    def getSubTree(self, Id, WithParent=True):
        ''' Get the subtree list of BackupStoreFSObjProperty object
        @param Id: Id of folder
        @return: list of BackupStoreFSObjProperty object '''
        lstobj = []
        for currentid in self.__getSubTreeId(Id):
            lstobj.append(self.getFSObjById(currentid, WithParent))
        return lstobj
    
    
    
    def __getSubTreeId(self, Id):
        ''' Get the subtree list of subid
        @param Id: Id of folder
        @return: list of ids '''
        lst_ids = [Id]
        self.cursor.execute('''SELECT id, isFolder FROM BS_filesystem WHERE parentId=%d;''' % Id)
        for obj in self.cursor.fetchall():
            if obj[1] == 1:
                lst_ids.extend(self.__getSubTreeId(obj[0]))
            else:
                lst_ids.append(obj[0])
        return lst_ids
    
    
    def getRepository(self, limit=-1):
        ''' Get all repository data in database use limit for the memory
        @param limit: Limit the result
        @return: Return a list of BackupStoreFSObjProperty object '''
        lstBackupStoreFSObjProperty = []
        query = ''' SELECT id, parentId, name, path, isFolder, stat, checksum, compress, archVerified, archSec FROM BS_filesystem'''
        
        if limit is not None and limit >= 0:
            query += ' LIMIT %d,%d' % (self.record, limit)
        
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        
        if result is not None:
            for data in result:
                lstBackupStoreFSObjProperty.append(BackupStoreFSObjProperty(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9]))
        
        self.record += len(result)
        return lstBackupStoreFSObjProperty