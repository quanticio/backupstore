# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : tools
@since   : 22/08/2014
'''
#Standard package
import os.path
import zipfile
import tarfile
import time




def getArchiveCompressionType(ArchivePath):
    ''' Define the compression type usingfor an archive ['zip', 'tar', 'gzip', 'bz2'] '''
    if not os.path.isfile(ArchivePath):
        raise IOError("The archive path is not a file or don't exist")
    
    if zipfile.is_zipfile(ArchivePath):
        return 'zip'
    elif tarfile.is_tarfile(ArchivePath):
        name = os.path.basename(ArchivePath)
        index = name.rfind('.')
        
        if index > -1:
            ext = name[index:]
            
            if ext == '.tar':
                return 'tar'
            
            elif ext == '.gz':
                return 'gzip'
            
            elif ext == '.bz2':
                return 'bz2'
    
    raise IOError("The archive path is not a compatible archive")




class chrono(object):
    ''' chrono definition class '''
    
    
    def __init__(self, secondPrecision=3):
        ''' Constructor
        @param secondPrecision: Second precision for calculation and print '''
        self.secondPrecision = secondPrecision
        self.finishChrono    = False
        self.startTime       = 0.0
        self.finishTime      = 0.0
    
    
    def start(self):
        ''' Start chrono (current timestamp) '''
        self.finishChrono = False
        self.startTime = time.time()
    
    
    def stop(self):
        ''' Finish chrono (current timestamp) '''
        if not self.finishChrono:
            self.finishTime = time.time()
            self.finishChrono = True
    
    
    def getTimeInSecond(self):
        ''' Gives the time in seconds
        @return: Time in seconds (or 0.0 if chrono is not finish) (float value) '''
        if self.finishChrono:
            return round(self.finishTime - self.startTime, int(self.secondPrecision))
        else:
            return 0.0
    
    
    def getTimeInMinutes(self, resultFormat="%s minutes %s seconds"):
        ''' Gives the time in minutes
        @param resultFormat: Definition of result format for minutes and seconds presentation
        @return: Time in minutes (or 0.0 if chrono is not finish) (string value) '''
        currentSec = self.getTimeInSecond()
        
        minutes = 0
        
        while currentSec >= 60.0:
            minutes += 1
            currentSec -= 60.0
        
        return resultFormat % (str(minutes), ('{:.%df}'%self.secondPrecision).format(round(currentSec, 3)))




class folderInformation(object):
    ''' Folder information definition class '''
    
    
    def __init__(self, folder):
        ''' Constructor
        @param folder: Path to folder '''
        if os.path.isdir(folder):
            self.__folder        = folder
            self.__globalSize    = None
            self.__numberFiles = None
        else:
            raise AttributeError("The argument passed as a parameter is not a folder : %s" % str(folder))
    
    
    def getGlobalSizeAndNumberFiles(self, ignoreCache=False):
        ''' Getting folder informations about the global size and files number
        @param ignoreCache: Ignore cache or not (if the object has the data or not)
        @return: Global size and files number '''
        if not ignoreCache and self.__globalSize is not None and self.__numberFiles is not None:
            return self.__globalSize, self.__numberFiles
        
        globalSize    = 0
        numberFiles = 0
        for root, dirs, files in os.walk(self.__folder):
            for fic in files:
                globalSize += os.path.getsize(os.path.join(root, fic))
                numberFiles += 1
        if not ignoreCache:
            self.__globalSize    = globalSize
            self.__numberFiles = numberFiles
        
        return globalSize, numberFiles
    
    
    def getGlobalSize(self, ignoreCache=False):
        ''' Getting folder informations about the global size
        @param ignoreCache: Ignore cache or not (if the object has the data or not)
        @return: Global size (bytes unit) '''
        return self.getGlobalSizeAndNumberFiles(ignoreCache=ignoreCache)[0]
    
    
    def getGlobalNumberFiles(self, ignoreCache=False):
        ''' Getting folder informations about the global size
        @param ignoreCache: Ignore cache or not (if the object has the data or not)
        @return: Number files '''
        return self.getGlobalSizeAndNumberFiles(ignoreCache=ignoreCache)[1]
    
    
    def convertByteUnitSizeToOthers(self, value, unitSize='byte', resultFormat='%s'):
        ''' Convert a unit size (byte to megabyte for sample)
        @param value: Decimal value to convert (to bytes)
        @param unitSize: define the unit of global size (can be 'byte' (by default), 'ko', 'mo', 'go', 'to', 'po', 'eo')
        @param format: Format the string result ('%s' by default or '%s Mo' ...)
        @return: Return a string value '''
        if unitSize == 'ko':
            value = value / 1024
        elif unitSize == 'mo':
            value = value / 1024 / 1024
        elif unitSize == 'go':
            value = value / 1024 / 1024 / 1024
        elif unitSize == 'to':
            value = value / 1024 / 1024 / 1024 / 1024
        elif unitSize == 'po':
            value = value / 1024 / 1024 / 1024 / 1024 / 1024
        elif unitSize == 'eo':
            value = value / 1024 / 1024 / 1024 / 1024 / 1024 / 1024
        
        return resultFormat % value
    
    
    def getLocalSizeAndNumberFiles(self):
        ''' Getting folder informations about the local size and files number (no recursive method, only in the folder)
        @return: Local size and files number '''
        localSize     = 0
        numberFiles = 0
        
        for currentObject in os.listdir(self.__folder):
            path = os.path.join(self.__folder, currentObject)
            if os.path.isfile(path):
                localSize += os.path.getsize(path)
                numberFiles += 1
        
        return localSize, numberFiles
    
    
    def getLocalSize(self):
        ''' Getting folder informations about the local size (no recursive method, only in the folder)
        @return: Local size '''
        return self.getLocalSizeAndNumberFiles()[0]
    
    
    def getLocalNumberFiles(self, ignoreCache=False):
        ''' Getting folder informations about the local size (no recursive method, only in the folder)
        @return: Local number files '''
        return self.getLocalSizeAndNumberFiles()[1]