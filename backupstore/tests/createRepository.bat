rem Test for create a repository and create an archive

set data=D:\test_backupstore\apache-tomcat-7.0.54
set repository=D:\test_backupstore\backup
set archive=D:\test_backupstore\archivage
set configfile=.\createRepository.conf

D:\Software\Python27\python.exe D:\git\backupstore\backupstore\src\manager\__init__.py -v --sync --conf "%configfile%" --data "%data%" --repo "%repository%" --archive "%archive%"

pause