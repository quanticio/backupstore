rem Test for restoration

set data=D:\test_backupstore\apache-tomcat-7.0.54
set archive=D:\test_backupstore\archivage\Archive__2014-11-19__15-38-38.tar.bz2

rmdir /s /q %data%

D:\Software\Python27\python.exe D:\git\backupstore\backupstore\src\manager\__init__.py -v --archive "%archive%" --restore --target "%data%"

pause