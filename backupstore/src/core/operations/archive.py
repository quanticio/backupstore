# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Archive a filesystem
@since   : 22/08/2014
'''
#Standard package
import os
import time
import shutil


#Internal package





class archiveFileSystem(object):
    ''' archiveFileSystem class definition '''
    FileSysOrig           = None
    repository            = None
    verbose               = False


    def __init__(self, FsObjIn, FolderOut, checksum, compression, compressionLevel, compressionAlgo, Verbose):
        ''' Constructor
        @param FsObjIn: Files system object to archive
        @param FolderOut: Files system object of stockage
        @param checksum: checksum to sign the file
        @param compression: compression boolean to compress the archive
        @param compressionLevel: level compression for zlib using
        @param compressionAlgo: Algorithm to use [zip, tar, gzip, bz2]
        @param Verbose: Verbosity mode '''
        self.FsObjIn           = FsObjIn
        self.FolderOut         = FolderOut
        self.checksum          = checksum
        self.compression       = compression
        self.compressionLevel  = compressionLevel
        self.compressionAlgo   = compressionAlgo
        self.verbose           = Verbose
        self.BackupStoreDbFile = None
        
        if self.verbose:
            print("Execute archiveFileSystem with this option :\nFsObjIn=%s\nFolderOut=%s\nchecksum=%s\ncompression=%s\ncompressionLevel=%s\ncompressionAlgo=%s" % (FsObjIn, FolderOut, checksum, compression, compressionLevel, compressionAlgo))
        
        if os.path.isfile(FolderOut):
            raise IOError('The folder name for the archive is a file. Impossible to continue.')
        
        if self.compressionAlgo is None:
            self.compressionAlgo = 'zip'
    
    
    def createNewArchive(self, ArchiveName='Archive__%Y-%m-%d__%H-%M-%S'):
        ''' Create an new archive '''
        ArchiveName = time.strftime(ArchiveName)
        
        if not os.path.isdir(self.FolderOut):
            os.mkdir(self.FolderOut)
        
        algo = self.compressionAlgo.lower()
        if algo == 'gzip':
            algo = 'gztar'
        elif algo == 'bz2':
            algo = 'bztar'
        shutil.make_archive(self.FolderOut + os.sep + ArchiveName, algo, root_dir=self.FsObjIn, verbose=self.verbose)