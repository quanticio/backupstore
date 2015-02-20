# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Verify operation
@since   : 09/01/2015
'''
#Standard package
import os


#Internal package
import core.common.backupstoredbfile




class verifyRepository(object):
    ''' verifyRepository class definition '''
    
    
    def __init__(self, repository, verbose):
        ''' Constructor 
        @param repository: Path of repository
        @param applyChange: Verbosity mode
        @param param:  '''
        self.repository  = repository
        self.verbose     = verbose
        self.applyChange = False
    
    
    def verify(self):
        ''' Verify the coherence between DB and the repository (no change) '''
        self.applyChange = False
        self.__synchronizeDbAndRepository()
        
        
    def verifyAndApply(self):
        ''' Verify the coherence between DB and the repository (with change) '''
        self.applyChange = True
        self.__synchronizeDbAndRepository()
    
    
    def __synchronizeDbAndRepository(self):
        ''' Private method for verify the coherence between DB and the repository '''
        if self.verbose:
            print("Execute the verification with this option :\nrepository=%s\napplyChange=%s" % (self.repository, self.applyChange))
        
        obj_backupstoredbfile = core.common.backupstoredbfile.BackupStoreDbFile(self.repository + os.sep + '.backupstore')
        obj_backupstoredbfile.open()
        
        try:
            limit = 100
            lstData = obj_backupstoredbfile.getRepository(limit)
            while len(lstData) > 0:
                for data in lstData:
                    self.__verifyRecord(data)
                lstData = obj_backupstoredbfile.getRepository(limit)
        finally:
            obj_backupstoredbfile.close()
    
    
    def __verifyRecord(self, record):
        if record.isFolder():
            print record
        else:
            print record
            print 'est un fichier'