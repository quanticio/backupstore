# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : metaoperation for rsync complete
@since   : 22/08/2014
'''
#Standard package
import os
import hashlib
import zipfile
import tarfile


#Internal package
import backupstoredbfile
import tools




class metaOperation(object):
    ''' checksum class definition '''
    verbose               = False
    
    
    def __init__(self, checksum, compression, compressionLevel, compressionAlgo, BSDbFile=None, Verbose=False):
        ''' Constructor
        @param checksum: checksum to sign the file ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
        @param compression: compression boolean to compress the archive
        @param compressionLevel: level compression for zlib using
        @param compressionAlgo: Algorithm to use [zlib, zip, tar, gzip, bz2]
        @param Verbose: Verbosity mode '''
        self.verbose          = Verbose
        self.obj_BSDbFile     = None
        self.lstFSObjToRemove = ([],[])
        
        if not checksum or checksum.lower() not in hashlib.algorithms:
            self.checksum = ''
        else:
            self.checksum = checksum.lower()
            if self.checksum == 'md5':
                self.hasher = hashlib.md5
            elif self.checksum == 'sha1':
                self.hasher = hashlib.sha1
            elif self.checksum == 'sha224':
                self.hasher = hashlib.sha224
            elif self.checksum == 'sha256':
                self.hasher = hashlib.sha256
            elif self.checksum == 'sha384':
                self.hasher = hashlib.sha384
            elif self.checksum == 'sha512':
                self.hasher = hashlib.sha512
        if not compression:
            self.compression = 0
        else:
            self.compression = compression
        if not compressionLevel:
            self.compressionLevel = 0
        else:
            self.compressionLevel = compressionLevel
        if not compressionAlgo or compressionAlgo not in ('zip', 'tar', 'gzip', 'bz2'):
            self.compressionAlgo = 'zip'
        else:
            self.compressionAlgo = compressionAlgo
        
        if BSDbFile:
            self.obj_BSDbFile = backupstoredbfile.BackupStoreDbFile(BSDbFile)
            self.obj_BSDbFile.open()
    
    
    def getChecksumOfFile(self, path, hexaCheckSum=True, BlockSize=65536):
        ''' Set checksum of file
        @param path: path of file for the checksum '''
        if self.checksum == '':
            return
        
        hasher = self.hasher()
        with open(path, 'rb') as currentfile:
            mybuffer = currentfile.read(BlockSize)
            while len(mybuffer) > 0:
                hasher.update(mybuffer)
                mybuffer = currentfile.read(BlockSize)
        
        if hexaCheckSum:
            return hasher.hexdigest()
        else:
            return hasher.digest()
    
    
    def updateFile(self, path):
        ''' UpdateMetaData of file in the database
        @param path: path of file '''
        try: 
            if not self.obj_BSDbFile:
                return
            
            self.obj_BSDbFile.updateFile(name = os.path.basename(path), path=os.path.dirname(path), stat=os.stat(path), checksum=self.getChecksumOfFile(path))
        except:
            print os.path.basename(path)
            print os.path.dirname(path)
            print os.stat(path)
            print self.getChecksumOfFile(path)
            raise
    
    
    def removeFile(self, path):
        ''' Remove file in the database (the file does not exist)
        @param path: path of file '''
        if not self.obj_BSDbFile:
            return
        
        if not os.path.isfile(path):
            self.obj_BSDbFile.removeFileOrFolder(name = os.path.basename(path), path=os.path.dirname(path))
    
    
    def makeDir(self, pathfolder):
        ''' Make a folder in the database (the folder files must exist)
        @param pathfolder: path of folder '''
        if not self.obj_BSDbFile:
            return
        
        if os.path.isdir(pathfolder):
            self.obj_BSDbFile.addFolder(path=pathfolder)
    
    
    def preRemoveTree(self, path):
        ''' Pre-remove tree in the database
        @param path: path of file '''
        if not self.obj_BSDbFile:
            return
        
        self.lstFSObjToRemove = self.__getFSObjList(path, [path], [])
    
    
    def postRemoveTree(self):
        ''' Post-remove tree in the database
        @param path: path of file '''
        if not self.obj_BSDbFile:
            return
        
        if len(self.lstFSObjToRemove[0]) == 0 and len(self.lstFSObjToRemove[1]) == 0:
            return
        
        # Remove files
        for thisfile in self.lstFSObjToRemove[1]:
            if not os.path.isfile(thisfile):
                self.obj_BSDbFile.removeFileOrFolder(name = os.path.basename(thisfile), path = os.path.dirname(thisfile))
        # Remove folders
        for thisfolder in self.lstFSObjToRemove[0]:
            if not os.path.isdir(thisfolder):
                self.obj_BSDbFile.removeFileOrFolder(name = '', path = thisfolder)
    
    
    def listdir(self, folder):
        ''' Get all filesystem object in a folder
        @param folder: folder path '''
        return self.obj_BSDbFile.getObjInFolderList(folder)
    
    
    def getFSObject(self, path):
        ''' Get FileSystem object (file or directory)
        @path: Path to search
        @return: Return a BackupStoreFSObjProperty object '''
        return self.obj_BSDbFile.getFSObj(path)
    
    
    def shouldUpdate(self, cookie, sink, target):
        ''' Define if the file was changing
        @param cookie: rsync cookie (params of all operation)
        @param sink: original path
        @param target: BackupStoreFSObjProperty object
        @return if the file change '''
        try:
            sink_st = os.stat(sink)
            sink_sz = sink_st.st_size
            sink_mt = sink_st.st_mtime
        except:
            self.log("Fail to retrieve information about sink %s (skip update)" % sink, True)
            return 1
        
        try:
            target_sz = target.getPropertyInStat(propertyLabel='st_size')
            target_mt = target.getPropertyInStat(propertyLabel='st_mtime')
        except:
            self.log("Fail to retrieve information about sink %s (skip update)" % sink, True)
            return 1
        
        try:
            if self.getChecksumOfFile(sink) != target.checksum:
                return 1
        except:
            self.log("Fail to retrieve information about sink %s (skip update)" % sink, True)
            return 1
        
        if cookie.update:
            return target_mt < sink_mt - cookie.modify_window
        
        if cookie.ignore_time:
            return 1
        
        if target_sz != sink_sz:
            return 1
        
        if cookie.size_only:
            return 0
    
        return abs(target_mt - sink_mt) > cookie.modify_window
    
    
    def isdir(self, folder):
        ''' Test if folder exist in the database
        @param folder: folder path '''
        return self.obj_BSDbFile.isFolder(folder)
    
    
    def isfile(self, filepath):
        ''' Test if folder exist in the database
        @param filepath: file path '''
        return self.obj_BSDbFile.isFile(name = os.path.basename(filepath), path = os.path.dirname(filepath))
    
    
    def log(self, message, error=False):
        ''' Log all operation
        @param message: Message to log
        @param error: Set an error (False by default) '''
        if not self.obj_BSDbFile:
            return
        if error:
            self.obj_BSDbFile.addTrace(message, self.obj_BSDbFile.ERROR)
        else:
            self.obj_BSDbFile.addTrace(message, self.obj_BSDbFile.INFO)
    
    
    def __getFSObjList(self, path, lst_dir=[], lst_file=[]):
        ''' Getting the list of folder and file in a root folder
        @param path: root folder
        @param lst_dir: list of folder
        @param lst_file: list of files '''
        for obj in os.listdir(path):
            abs_path = path + os.sep + obj
            if os.path.isfile(abs_path):
                lst_file.append(abs_path)
            elif os.path.isdir(abs_path):
                lst_dir.append(abs_path)
                lst_dir1, lst_file1 = self.__getFSObjList(abs_path, lst_dir, lst_file)
                lst_dir.extend(lst_dir1)
                lst_file.extend(lst_file1)
        return (lst_dir, lst_file)
    
    
    def compressData(self, target_dir, filenames):
        ''' Compress data in the target_dir folder (all files) and clean files
        @param target_dir: path to the folder
        @param filenames: FileSystem object list '''
        if not self.compression:
            return
        
        # Getting all files
        allAbsFilesLst = []
        for curfile in filenames:
            if not os.path.isdir(target_dir + os.sep + curfile):
                allAbsFilesLst.append(target_dir + os.sep + curfile)
        
        
        if self.compressionAlgo.lower() == 'zip':
            self.__compressDataToZipFile(self.__getArchiveName(target_dir, '.zip'), allAbsFilesLst)
        elif self.compressionAlgo.lower() in ('tar', 'gzip', 'bz2'):
            self.__compressDataToTarFile(self.__getArchiveName(target_dir, '.' + self.compressionAlgo.lower()), allAbsFilesLst)
    
    
    def __getArchiveName(self, target_dir, extension):
        ''' Getting archive name with extension
        @param target_dir: path to the folder
        @param extension: Extension of archive
        @return: Archive name '''
        templatename = 'BS_files_' + extension
        ArchiveName = target_dir + os.sep + templatename
        nameexist = True
        while nameexist:
            if os.path.isfile(ArchiveName):
                ArchiveName += '.' + templatename
            else:
                nameexist = False
        return ArchiveName
    
    
    def __compressDataToZipFile(self, zipfilename, allAbsFilesLst):
        ''' Compress data to a data file in the folder
        @param zipfilename: Name of archive
        @param allAbsFilesLst: All files to add '''
        # Get compression type
        if self.compressionLevel <= 1:
            compress = zipfile.ZIP_STORED
        else:
            compress = zipfile.ZIP_DEFLATED
        
        # Size verify : if the files in the folder (not in the subfolder) is more 2Go we use allowZip64
        if tools.folderInformation(os.path.dirname(zipfilename)).getLocalSize() >= 2147483648:
            allowZip64 = True
        else:
            allowZip64 = False
        # Create zipfile
        with zipfile.ZipFile(zipfilename, 'w', compress, allowZip64=allowZip64) as currentzip:
            for curfile in allAbsFilesLst:
                currentzip.write(curfile, os.path.basename(curfile))
            
        # Verify and clean
        error = ''
        if zipfile.is_zipfile(zipfilename):
            obj_zip = zipfile.ZipFile(zipfilename, 'r')
            if len(obj_zip.namelist()) != len(allAbsFilesLst):
                error = 'Archive is not correct (number files is not correct) !'
            if obj_zip.testzip() != None:
                error = 'Archive is not correct !'
            obj_zip.close()
        else:
            error = 'Archive is not a zipfile !'
        
        # Clean files in the folder
        if error == '':
            for curfile in allAbsFilesLst:
                os.remove(curfile)
        else:
            if self.verbose:
                print error
            self.log(error, error=True)
    
    
    def __compressDataToTarFile(self, tarfilename, allAbsFilesLst, algo='tar'):
        ''' Compress data to a data file in the folder
        @param zipfilename: Name of archive
        @param allAbsFilesLst: All files to add '''
        # Get compression type
        mode = 'w'
        if algo == 'gzip':
            mode += ':gz'
        elif algo == 'bz2':
            mode += ':bz2'
        
        # Create zipfile
        with tarfile.open(tarfilename, mode) as currenttar:
            for curfile in allAbsFilesLst:
                currenttar.add(curfile, arcname=os.path.basename(curfile), recursive=False)
        
        # Verify and clean
        error = ''
        currenttar = tarfile.open(tarfilename, 'r')
        if len(currenttar.getmembers()) != len(allAbsFilesLst):
            error = 'Archive is not correct (number files is not correct) !'
        currenttar.close()
        
        # Clean files in the folder
        if error == '':
            for curfile in allAbsFilesLst:
                os.remove(curfile)
        else:
            if self.verbose:
                print error
            self.log(error, error=True)
    
    
    def unCompressData(self, target_dir):
        ''' Uncompress data in the target_dir folder (all files) and clean archive
        @param target_dir: path to the folder '''
        if not self.compression:
            return
        
        algo = self.compressionAlgo.lower()
        ArchiveName = ''
        templatename = 'BS_files_' + '.' + self.compressionAlgo
        
        if algo in ('zip', 'tar', 'gzip', 'bz2'):
            for name in os.listdir(target_dir):
                if os.path.isfile(target_dir + os.sep + name) and name[len(name) - len(templatename):] == templatename:
                    ArchiveName = target_dir + os.sep + name
                    break
        
        
        if ArchiveName == '':
            return
            raise EnvironmentError('Not found the archive for uncompress operation in %s' % target_dir)
        
        
        if algo == 'zip':
            with zipfile.ZipFile(ArchiveName, 'r') as currentzip:
                currentzip.extractall(target_dir)
        elif algo in ('tar', 'gzip', 'bz2'):
            mode = 'r'
            if algo == 'gzip':
                mode += ':gz'
            elif algo == 'bz2':
                mode += ':bz2'
            with tarfile.open(ArchiveName, mode) as currenttar:
                currenttar.extractall(target_dir)
        os.remove(ArchiveName)