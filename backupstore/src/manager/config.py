# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Manager of backupstore
@since   : 22/08/2014
'''
#Standard package
import os.path
import ConfigParser




class configBackupStore(object):
    ''' configBackupStore class definition '''
    data             = None
    repository       = None
    compression      = None
    compressionLevel = None
    compressionAlgo  = None
    checksum         = None
    dbDumpType       = None
    dbConnect        = None
    dbBase           = None
    dbDumpTool       = None
    dbRestoreTool    = None
    dbTargetFile     = None
    
    
    def __init__(self, path):
        ''' Constructor
        @param path: Path to the configuration file '''
        if os.path.isfile(path):
            self.config = ConfigParser.ConfigParser()
            self.config.read(path)
            self.__setDataTagOfConfig()
            self.__setRepositoryTagOfConfig()
            self.__setCheckSumOfConfig()
            self.__setCompressionTagOfConfig()
            self.__setCompressionLevelTagOfConfig()
            self.__setCompressionAlgoTagOfConfig()
            self.__setDbDumpTypeTagOfConfig()
            self.__setDbConnectTagOfConfig()
            self.__setDbBaseTagOfConfig()
            self.__setDbTargetFileTagOfConfig()
    
    
    def __setDataTagOfConfig(self):
        ''' Setting data tag value in the configuration '''
        if self.config:
            try:
                self.data = self.config.get('MAIN', 'data')
            except:
                pass
    
    
    def __setRepositoryTagOfConfig(self):
        ''' Setting repository tag value in the configuration '''
        if self.config:
            try:
                self.repository = self.config.get('MAIN', 'repository')
            except:
                pass
    
    
    def __setCheckSumOfConfig(self):
        ''' Setting checksum tag value in the configuration '''
        if self.config:
            try:
                self.checksum = self.config.get('MAIN', 'checksum')
            except:
                pass
    
    
    def __setCompressionTagOfConfig(self):
        ''' Setting the compression boolean tag value in the configuration '''
        if self.config:
            try:
                self.compression = self.config.getboolean('COMPRESSION', 'compression')
            except:
                pass
    
    
    def __setCompressionLevelTagOfConfig(self):
        ''' Setting compressionLevel tag value in the configuration '''
        if self.config:
            try:
                self.compressionLevel = self.config.get('COMPRESSION', 'compressionLevel')
            except:
                pass
    
    
    def __setCompressionAlgoTagOfConfig(self):
        ''' Setting compressionAlgo tag value in the configuration '''
        if self.config:
            try:
                self.compressionAlgo = self.config.get('COMPRESSION', 'compressionAlgo')
            except:
                pass
    def __setDbDumpTypeTagOfConfig(self):
        ''' Setting dumpType tag value in the configuration '''
        if self.config:
            try:
                self.dbDumpType = self.config.get('DATABASE', 'dumpType')
            except:
                pass
    
    
    def __setDbConnectTagOfConfig(self):
        ''' Setting dumpType tag value in the configuration '''
        if self.config:
            try:
                self.dbConnect = '%s:%s@%s:%s' % (self.config.get('DATABASE', 'host'), self.config.get('DATABASE', 'port'), self.config.get('DATABASE', 'user'), self.config.get('DATABASE', 'pwd'))
            except:
                pass
    
    
    def __setDbBaseTagOfConfig(self):
        ''' Setting dbBase tag value in the configuration '''
        if self.config:
            try:
                self.dbBase = self.config.get('DATABASE', 'base')
            except:
                pass
    
    
    def __setDumpToolTagOfConfig(self):
        ''' Setting dbDumpTool tag value in the configuration '''
        if self.config:
            try:
                self.dbDumpTool = self.config.get('DATABASE', 'dbDumpTool')
            except:
                pass
    
    
    def __setRestoreToolTagOfConfig(self):
        ''' Setting dbRestoreTool tag value in the configuration '''
        if self.config:
            try:
                self.dbRestoreTool = self.config.get('DATABASE', 'dbRestoreTool')
            except:
                pass
    
    
    def __setDbTargetFileTagOfConfig(self):
        ''' Setting dbTargetFile tag value in the configuration '''
        if self.config:
            try:
                self.dbTargetFile = self.config.get('DATABASE', 'dbTargetFile')
            except:
                pass
    
    
    def getDataTag(self):
        ''' Getting data tag in the configuration
        @return: data path '''
        return self.data
    
    
    def getRepositoryTag(self):
        ''' Getting repository tag in the configuration
        @return: repository path '''
        return self.repository
    
    
    def getCompressionTag(self):
        ''' Getting compression tag in the configuration
        @return: compression boolean '''
        return self.compression
    
    
    def getCompressionLevelTag(self):
        ''' Getting compressionLevel tag in the configuration
        @return: compressionLevel [1-9]/None '''
        return self.compressionLevel
    
    
    def getCompressionAlgoTag(self):
        ''' Getting compressionAlgo tag in the configuration
        @return: compressionAlgo '''
        return self.compressionAlgo
    
    
    def getCheckSumTag(self):
        ''' Getting checksum tag in the configuration
        @return: checksum '''
        return self.checksum
    
    
    def getDbDumpTypeTag(self):
        ''' Getting dbDumpType tag in the configuration
        @return: dbDumpType '''
        return self.dbDumpType
    
    
    def getDbConnectTag(self):
        ''' Getting dbConnect tag in the configuration
        @return: dbConnect '''
        return self.dbConnect
    
    
    def getDbBaseTag(self):
        ''' Getting dbBase tag in the configuration
        @return: dbBase '''
        return self.dbBase
    
    
    def getDbDumpToolTag(self):
        ''' Getting dbDumpTool tag in the configuration
        @return: dbDumpTool '''
        return self.dbDumpTool
    
    
    def getDbRestoreToolTag(self):
        ''' Getting dbRestoreTool tag in the configuration
        @return: dbRestoreTool '''
        return self.dbRestoreTool
    
    
    def getDbTargetFileTag(self):
        ''' Getting dbTargetFile tag in the configuration
        @return: dbTargetFile '''
        return self.dbTargetFile




def parseConnectionString(dbconnect):
    ''' Getting dbhost, dbport, dbuser, dbpwd by this format user:password@host:port in dbconnect
    @param dbconnect: connection string (format user:password@host:port)
    @return: dbhost, dbport, dbuser, dbpwd '''
    if dbconnect in (None, ''):
        return 'localhost', '5432', 'postgres', ''
    
    dbhost = ''
    dbport = ''
    dbuser = ''
    dbpwd = ''
    indexAt = dbconnect.rfind('@')
    if indexAt > -1:
        auth = dbconnect[:indexAt]
        sgbd = dbconnect[indexAt+1:]
        
        index2Pt = auth.find(':')
        if index2Pt <= -1:
            dbuser = auth
        elif index2Pt == 0:
            dbuser = 'postgres'
            dbpwd  = auth[index2Pt+1:]
        else:
            dbuser = auth[:index2Pt]
            dbpwd  = auth[index2Pt+1:]
        
    else:
        dbuser = 'postgres'
        dbpwd  = ''
        sgbd   = dbconnect
    
    index2Pt = sgbd.rfind(':')
    if index2Pt <= -1:
        dbhost = sgbd
        dbport = '5432'
    elif index2Pt == 0:
        dbhost = 'localhost'
        dbport  = sgbd[index2Pt+1:]
    else:
        dbhost = sgbd[:index2Pt]
        dbport = sgbd[index2Pt+1:]
    
    
    return dbhost, dbport, dbuser, dbpwd