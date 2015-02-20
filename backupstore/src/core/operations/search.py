# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : search operation
@since   : 22/08/2014
'''
#Standard package
import os
import zipfile
import tarfile
import tempfile


#Internal package
import core.common.backupstoredbfile
import core.common.tools




class searchInArchive(object):
    ''' searchInArchive class definition '''
    backupStoreFile = ''
    verbose         = False
    
    
    def __init__(self, archive, verbose):
        ''' Constructor 
        @param archive: Path of archive file (format zip, tar, gzip, bz2 (automatic research)
        @param verbose: Verbosity mode '''
        self.verbose = verbose

        if self.verbose:
            print("Execute searchInArchive with this option :\narchive=%s" % (archive))
        
        if not os.path.isfile(archive):
            raise IOError("Research impossible : The archive path is not a file or don't exist")
        
        # Research a compression algorithm type and uncompress the portable database of file system
        target = tempfile.gettempdir() + os.sep + os.path.basename(archive)
        
        CompressionType = core.common.tools.getArchiveCompressionType(archive)
        if CompressionType == 'zip':
            obj_zipfile = zipfile.ZipFile(archive, 'r')
            obj_zipfile.extract('.backupstore', target)
            obj_zipfile.close()
        else:
            currenttar = None
            if CompressionType == 'tar':
                currenttar = tarfile.open(archive, 'r')
            elif CompressionType == 'gzip':
                currenttar = tarfile.open(archive, 'r:gz')
            elif CompressionType == 'bz2':
                currenttar = tarfile.open(archive, 'r:bz2')
                
            if currenttar is not None:
                currenttar.extract('./.backupstore', target)
                currenttar.close()
            else:
                raise IOError("Research impossible : The archive path is not a compatible archive")
        
        self.backupStoreFile = target + os.sep + '.backupstore'
    
    
    def getResultWithFilter(self, searchByName, searchByDate):
        ''' Get result of the research with using a filter (by name or by date)
        @param searchByName: String name to search
        @param searchByDate: String date to search
        @return: Return a result list '''
        if searchByName is None:
            searchByName = ''
        if searchByDate is None:
            searchByDate = ''
        
        obj_backupstoredbfile = core.common.backupstoredbfile.BackupStoreDbFile(self.backupStoreFile)
        
        obj_backupstoredbfile.open()
        
        result = []
        for response in obj_backupstoredbfile.searchFileOrFolder(name=searchByName, date=searchByDate):
            if response[4] == 0:
                val = response[5].index('st_size=')
                size = long(response[5][val+8:val + response[5][val:].index(',')])
                val = response[5].index('st_mtime=')
                modif = long(response[5][val+9:val + response[5][val:].index(',')])
                
                result.append((response[0], 'file', response[3] + os.sep + response[2], str(size), str(modif)))
            else:
                result.append((response[0], 'folder', response[3] + os.sep + response[2], '', ''))
        
        obj_backupstoredbfile.close()
        
        return result
    
    
    def clean(self):
        ''' Clean the temporary file and folder '''
        try:
            os.remove(self.backupStoreFile)
            os.rmdir(os.path.basename(self.backupStoreFile))
        except:
            pass