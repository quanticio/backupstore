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
import time
import tempfile


#Internal package
import core.common.tools




class Test(unittest.TestCase):
    
    
    @classmethod
    def setUpClass(cls):
        cls.objChrono = core.common.tools.chrono()
        cls.objChrono.start()
        time.sleep(1)
        cls.objChrono.stop()
        cls.objChronoWithNoOffset = core.common.tools.chrono(secondPrecision=0)
        cls.objChronoWithNoOffset.start()
        time.sleep(1)
        cls.objChronoWithNoOffset.stop()
        
        cls.objFold = core.common.tools.folderInformation(tempfile.gettempdir())
    
    
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test1_standardChronoGettingSec(self):
        ''' Test standard timer to obtain the difference in seconds '''
        self.assertEqual(str(self.objChrono.getTimeInSecond()), str(1.0))
    
    
    def test2_WithNoOffsetChronoGettingSec(self):
        ''' Test with no offset second to obtain the difference in seconds '''
        self.assertEqual(str(self.objChronoWithNoOffset.getTimeInSecond()), str(1.0))
    
    
    def test3_standardChronoGettingMin(self):
        ''' Test standard timer to obtain the difference in minutes '''
        self.assertEqual(self.objChrono.getTimeInMinutes(), "0 minutes 1.000 seconds")
    
    
    def test4_WithNoOffsetChronoGettingMin(self):
        ''' Test with no offset second to obtain the difference in minutes '''
        self.assertEqual(self.objChronoWithNoOffset.getTimeInMinutes(), "0 minutes 1 seconds")
    
    
    def test5_WithNoOffsetChronoWithOtherFormat(self):
        ''' Test with no offset second to obtain the difference in minutes with other format '''
        self.assertEqual(self.objChronoWithNoOffset.getTimeInMinutes('%s:%s'), "0:1")
    
    
    def test6_FinishBeforeStart(self):
        ''' Test if stop is used before the start '''
        objChrono = core.common.tools.chrono()
        objChrono.stop()
        time.sleep(1)
        objChrono.start()
        self.assertEqual(objChrono.getTimeInSecond(), 0.0)
        self.assertEqual(objChrono.getTimeInMinutes(), "0 minutes 0.000 seconds")
    
    
    def test10_folderInformation(self):
        ''' Test folder information class '''
        self.assertRaises(AttributeError, core.common.tools.folderInformation, tempfile.gettempdir() + os.sep + 'filenotexist')
    
    
    def test11_folderInformation_getGlobalSizeAndNumberFiles(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getGlobalSizeAndNumberFiles(), "The result can't be none")
    
    
    def test12_folderInformation_getGlobalSize(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getGlobalSize(), "The result can't be none")
    
    
    def test13_folderInformation_getGlobalNumberFiles(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getGlobalNumberFiles(), "The result can't be none")
    
    
    def test14_folderInformation_getLocalSizeAndNumberFiles(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getLocalSizeAndNumberFiles(), "The result can't be none")
    
    
    def test15_folderInformation_getLocalSize(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getLocalSize(), "The result can't be none")
    
    
    def test16_folderInformation_getLocalNumberFiles(self):
        ''' Test folder information class '''
        self.assertIsNotNone(self.objFold.getLocalNumberFiles(), "The result can't be none")
    
    
    def test17_folderInformation_convertByteUnitSizeToOthers_byte(self):
        ''' Test folder information class '''
        self.assertEqual(self.objFold.convertByteUnitSizeToOthers(2147483648), '2147483648')
    
    
    def test18_folderInformation_convertByteUnitSizeToOthers_ko(self):
        ''' Test folder information class '''
        self.assertEqual(self.objFold.convertByteUnitSizeToOthers(2147483648, 'ko'), '2097152')
    
    
    def test19_folderInformation_convertByteUnitSizeToOthers_mo(self):
        ''' Test folder information class '''
        self.assertEqual(self.objFold.convertByteUnitSizeToOthers(2147483648, 'mo'), '2048')
    
    
    def test20_folderInformation_convertByteUnitSizeToOthers_go(self):
        ''' Test folder information class '''
        self.assertEqual(self.objFold.convertByteUnitSizeToOthers(2147483648, 'go'), '2')



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=10)