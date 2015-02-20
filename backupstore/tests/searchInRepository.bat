rem Test the search in an archive

set name=tomcat7.exe
rem time.strftime('%Y%m', time.localtime(os.stat('D:\\331.xml').st_mtime))
set date=14
set archive=D:\test_backupstore\archivage\Archive__2014-11-19__15-38-38.tar.bz2

D:\Software\Python27\python.exe D:\git\backupstore\backupstore\src\manager\__init__.py -v --archive "%archive%" --search --byname "%name%"

rem TO COMPLETE
D:\Software\Python27\python.exe D:\git\backupstore\backupstore\src\manager\__init__.py -v --archive "%archive%" --search --bydate "%date%"

pause