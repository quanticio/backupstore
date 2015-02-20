# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : Manager of backupstore
@since   : 22/08/2014
@describe: PyBackupStore/src/manager/__init__.py -v --sync --data "D:\Conf LB" --repo "D:\backup"
'''
#Standard package
import os
import sys
import argparse


currentPath = os.path.abspath(sys.argv[0]+os.sep+'..'+os.sep+'..')
print currentPath
sys.path.append(currentPath)


#Internal package
import config
import core.operations.dump
import core.operations.archive
import core.operations.search
import core.operations.verify
import core.operations.restore




def main():
    parser = argparse.ArgumentParser(description='Manager of PyBackupStore to do the optimize backup')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    
    # Operation backup : synchronize, build archive with compression ...
    parser.add_argument('--sync', dest='synchronize', action="store_true", help='Synchronize the backup with repository and create an archive')
    
    parser.add_argument('--comp', dest='compression', action="store_true", help='Compression of repository')
    parser.add_argument('--data', dest='data', type=str, help='Path to the base of the data to backup')
    parser.add_argument('--repo', dest='repository', type=str, help='Path to the base of the repository')
    parser.add_argument('--archive', dest='archive', type=str, help='Path to archive a repository version')
    parser.add_argument('--checksum', dest='checksum', help='Hash algorithm [md5, sha1, sha224, sha256, sha384, sha512]')
    parser.add_argument('--conf', dest='configuration', type=str, help='Path to the configuration file')
    parser.add_argument('--level', dest='compressionLevel', type=int, help='Compression level [1-9] of repository. 1 is fastest and produces the least compression, 9 is slowest and produces the most')
    parser.add_argument('--algo', dest='compressionAlgo', type=str, help='Compression algorithm. [zip, tar, gzip, bz2].')
    
    # Operation  search
    parser.add_argument('--search', dest='search', action="store_true", help='Search a file or folder in archive')
    parser.add_argument('--byname', dest='searchByName', type=str, help='Search by name the folder or file')
    parser.add_argument('--bydate', dest='searchByDate', type=str, help='Search by date the folder or file')
    
    # Operation  restore
    parser.add_argument('--restore', dest='restore', action="store_true", help='Restore a file or folder or all')
    parser.add_argument('--byid', dest='restoreById', type=str, help='Restore by id of folder or file (format: "id0,id1,...")')
    parser.add_argument('--target', dest='target', type=str, help='Path to the base of the restore backup')
    
    # Operation verify : Verify repository
    parser.add_argument('--verify', dest='verify', action="store_true", help='Verify the repository')
    parser.add_argument('--apply', dest='apply', action="store_true", help='Apply the verification delete and update the repository database')
    
    # Operation DB backup :
    parser.add_argument('--dbdump', dest='dbdump', action="store_true", help='Dump a database (only postgres support)')
    parser.add_argument('--dbrestore', dest='dbrestore', action="store_true", help='Restore a database (only postgres support)')
    parser.add_argument('--dbdumptype', dest='dbdumptype', type=str, help='Format type of archive "std or sql", std by default')
    parser.add_argument('--dbconnect', dest='dbconnect', type=str, help='Database connection string, format user:password@host:port')
    parser.add_argument('--dbbase', dest='dbbase', type=str, help='Database to use')
    parser.add_argument('--dbdumptool', dest='dbdumptool', type=str, help='Path to the backup tool (\var\bin\pg_dump)')
    parser.add_argument('--dbrestoretool', dest='dbrestoretool', type=str, help='Path to the restore tool (\var\bin\pg_restore)')
    parser.add_argument('--dbtargetfile', dest='dbtargetfile', type=str, help='Path to the database export/import file')
    
    # Choose: priority to the argument else we take in the configuration file
    data       = None
    repository = None
    args = parser.parse_args()
    if args.configuration:
        obj_config = config.configBackupStore(args.configuration)
        if args.data:
            data = args.data
        else:
            data = obj_config.getDataTag()
        if args.repository:
            repository = args.repository
        else:
            repository = obj_config.getRepositoryTag()
        if args.checksum:
            checksum = args.checksum
        else:
            checksum = obj_config.getCheckSumTag().lower()
            if checksum not in ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'):
                checksum = None
        if args.compression:
            compression = args.compression
        else:
            compression = obj_config.getCompressionTag()
        if args.compressionLevel:
            compressionLevel = args.compressionLevel
        else:
            compressionLevel = obj_config.getCompressionLevelTag()
        if args.compressionAlgo:
            compressionAlgo = args.compressionAlgo
        else:
            compressionAlgo = obj_config.getCompressionAlgoTag()
        if args.dbdumptype:
            dbdumptype = args.dbdumptype
        else:
            dbdumptype = obj_config.getDbDumpTypeTag()
        if args.dbconnect:
            dbconnect = args.dbconnect
        else:
            dbconnect = obj_config.getDbConnectTag()
        if args.dbbase:
            dbbase = args.dbbase
        else:
            dbbase = obj_config.getDbBaseTag()
        if args.dbdumptool:
            dbdumptool = args.dbdumptool
        else:
            dbdumptool = obj_config.getDbDumpToolTag()
        if args.dbrestoretool:
            dbrestoretool = args.dbrestoretool
        else:
            dbrestoretool = obj_config.getDbRestoreToolTag()
        if args.dbtargetfile:
            dbtargetfile = args.dbtargetfile
        else:
            dbtargetfile = obj_config.getDbTargetFileTag()
    else:
        data             = args.data
        repository       = args.repository
        compression      = args.compression
        compressionLevel = args.compressionLevel
        compressionAlgo  = args.compressionAlgo
        checksum         = args.checksum
        dbdumptype       = args.dbdumptype
        dbconnect        = args.dbconnect
        dbbase           = args.dbbase
        dbdumptool       = args.dbdumptool
        dbrestoretool    = args.dbrestoretool
        dbtargetfile     = args.dbtargetfile
    
    # -v --archive "D:\\archivage\\Archive__2014-10-02__09-23-21.tar" --search
    if args.search:
        if args.archive is None:
            print("Error: The path of the archive is required for execute a search query.")
        else:
            obj_research = core.operations.search.searchInArchive(args.archive, args.verbose)
            print(('ID', 'TYPE', 'PATH', 'SIZE', 'MODIFY DATE'))
            for result in obj_research.getResultWithFilter(args.searchByName, args.searchByDate):
                print(result)
            obj_research.clean()
    
    elif args.verify:
        if args.apply:
            core.operations.verify.verifyRepository(repository, args.verbose).verifyAndApply()
        else:
            core.operations.verify.verifyRepository(repository, args.verbose).verify()
        
    # -v --archive "D:\archivage\Archive__2014-10-03__13-31-09.tar.bz2" --restore --target "D:\restore"
    # -v --archive "D:\archivage\Archive__2014-10-03__13-31-09.tar.bz2" --restore --target "D:\restore" --byid "16"
    # -v --archive "D:\archivage\Archive__2014-10-03__13-31-09.tar.bz2" --restore --target "D:\restore" --byid "16,17,22,5,2"
    elif args.restore:
        if args.archive is None:
            print("Error: The path of the archive is required for execute a search query.")
        if args.target is None:
            print("Error: The path of the target is required for execute a restore query.")
        else:
            obj_restore = core.operations.restore.restoreFileSystem(args.archive, args.target, args.verbose)
            if args.restoreById is None:
                obj_restore.restoreAll()
            else:
                obj_restore.restoreById(ids = args.restoreById)
    
    else:
        # -v --sync --conf "D:\projects\workspace\PyBackupStore\BackupStore.conf" --archive "D:\\archivage"
        if args.synchronize:
            if data and repository is None:
                print("Error: The path of the repository is required.")
            elif data and repository:
                core.operations.dump.dumpFileSystem(data, repository, checksum, compression, compressionLevel, compressionAlgo, args.verbose).dump()
        
        if args.archive:
            if repository is None:
                print("Error: The path of the repository is required for create a new archive.")
            else:
                core.operations.archive.archiveFileSystem(repository, args.archive, checksum, compression, compressionLevel, compressionAlgo, args.verbose).createNewArchive()
    
    # Database actions
    # Dump / Restore
    if args.dbdump or args.dbrestore:
        dbhost, dbport, dbuser, dbpwd = config.parseConnectionString(dbconnect)
        # -v --dbdump --dbconnect postgres:@pgc.intra.bull:5432 --dbbase maarch_db --dbdumptype sql --dbdumptool "C:\\Program Files (x86)\\pgAdmin III\\1.18\\pg_dump" --dbtargetfile D:\\maarch.sql
        if args.dbdump and dbdumptool:
            core.operations.dump.dataBase(dbbase, target=dbtargetfile, tools=dbdumptool, host=dbhost, port=dbport, user=dbuser, password=dbpwd, dumptype=dbdumptype, verbose=args.verbose)
        # -v --dbrestore --dbconnect postgres:@pgc.intra.bull:5432 --dbbase maarch_db --dbdumptype sql --dbrestoretool "C:\\Program Files (x86)\\pgAdmin III\\1.18\\psql" --dbtargetfile D:\\maarch.sql
        elif args.dbrestore and dbrestoretool:
            core.operations.restore.dataBase(dbbase, dbtargetfile, tools=dbrestoretool, host=dbhost, port=dbport, user=dbuser, password=dbpwd, dumptype=dbdumptype, verbose=args.verbose)




if __name__ == '__main__':
    main()