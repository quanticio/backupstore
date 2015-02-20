# coding=utf8
'''
@author  : quanticio44
@contact : quanticio44@gmail.com
@license : See with Quanticio44
@summary : bootstrap for rsync module
@since   : 22/08/2014
'''
#Standard package
import sys
import os.path
import glob


#Internal package
import rsync
import metaoperation




class CheeseCake(rsync.Cookie):
    def __init__(self):
        rsync.Cookie.__init__(self)
        self.extra_operation = metaoperation.metaOperation('', False, 0, '')




def synchronizeFS(FileSysOrig, target_root, *args, **kwargs):
    ''' Call all services of rsync library :
     quiet              decrease verbosity
     recursive          recurse into directories
     relative           use relative path names
     update             update only (don't overwrite newer files)
     times              preserve times
     dry-run            show what would have been transferred
     existing           only update files that already exist
     delete             delete files that don't exist on the sending side
     delete-excluded    also delete excluded files on the receiving side
     delete-from-source delete excluded files on the receiving side
     ignore-times       don't exclude files that match length and time
     size-only          only use file size when determining if a file should
                         be transferred
     existing           only update existing target files or folders
     cvs-exclude        auto ignore files in the same way CVS does
     version            print version number
     help               show this help screen
     modify-window=NUM  timestamp window (seconds) for file match (default=2)
     exclude=PATTERN    exclude files matching PATTERN
     exclude-from=FILE  exclude patterns listed in FILE
     include=PATTERN    don't exclude files matching PATTERN
     include-from=FILE  don't exclude patterns listed in FILE
     '''
    cookie = CheeseCake()
    
    if 'quiet' in args:
        cookie.quiet = 1
    if 'recursive' in args:
        cookie.recursive = 1
    if 'relative' in args:
        cookie.relative = 1
    if 'dry_run' in args:
        cookie.dry_run = 1
    if 'quiet' in args:
        cookie.quiet = 1
    if 'times' in args or 'time' in args:
        cookie.time = 1
    if 'update' in args:
        cookie.update = 1
    if 'cvs_ignore' in args:
        cookie.cvs_ignore = 1
    if 'ignore_time' in args:
        cookie.ignore_time = 1
    if 'delete' in args:
        cookie.delete = 1
    if 'delete_excluded' in args:
        cookie.delete   = 1
        cookie.delete_excluded = 1
    if 'delete_from_source' in args:
        cookie.delete_from_source = 1
    if 'size_only' in args:
        cookie.size_only = 1
    if 'existing' in args:
        cookie.existing = 1
    if 'modify_window' in kwargs:
        cookie.modify_window = int(kwargs['modify_window'])
    if 'exclude' in kwargs:
        cookie.filters = cookie.filters + [rsync.convertPattern(kwargs['exclude'], "-")]
    if 'exclude_from' in kwargs:
        cookie.filters = cookie.filters + [rsync.convertPattern(kwargs['exclude_from'], "-")]
    if 'include' in kwargs:
        cookie.filters = cookie.filters + [rsync.convertPattern(kwargs['include'], "+")]
    if 'include_from' in kwargs:
        cookie.filters = cookie.filters + [rsync.convertPattern(kwargs['include_from'], "+")]
    if 'extra_operation' in kwargs:
        cookie.extra_operation = kwargs['extra_operation']
    
    try: # In order to allow compatibility below 2.3.
        pass
        if os.path.__dict__.has_key("supports_unicode_filenames") and os.path.supports_unicode_filenames:
            target_root = unicode(target_root, sys.getfilesystemencoding())
    finally:
        cookie.target_root = target_root
    
    sinks = glob.glob(FileSysOrig)
    if not sinks:
        return 0
    
    sink_families = {}
    for sink in sinks:
        try: # In order to allow compatibility below 2.3.
            if os.path.__dict__.has_key("supports_unicode_filenames") and os.path.supports_unicode_filenames:
                sink = unicode(sink, sys.getfilesystemencoding())
        except:
            pass
        sink_name = ""
        sink_root = sink
        sink_drive, sink_root = os.path.splitdrive(sink)
        while not sink_name:
            if sink_root == os.path.sep:
                sink_name = "."
                break
            sink_root, sink_name = os.path.split(sink_root)
        sink_root = sink_drive + sink_root
        if not sink_families.has_key(sink_root):
            sink_families[sink_root] = []
        sink_families[sink_root] = sink_families[sink_root] + [sink_name]
    
    for sink_root in sink_families.keys():
        if cookie.relative:
            cookie.sink_root = ""
        else:
            cookie.sink_root = sink_root
        
        global y # In order to allow compatibility below 2.1 (nested scope where used before).
        y = sink_root
        files = filter(lambda x: os.path.isfile(os.path.join(y, x)), sink_families[sink_root])
        if files:
            rsync.visit(cookie, sink_root, files)
        
        #global y # In order to allow compatibility below 2.1 (nested scope where used before).
        y = sink_root
        folders = filter(lambda x: os.path.isdir(os.path.join(y, x)), sink_families[sink_root])
        for folder in folders:
            folder_path = os.path.join(sink_root, folder)
            if not cookie.recursive:
                rsync.visit(cookie, folder_path, os.listdir(folder_path))
            else:
                os.path.walk(folder_path, rsync.visit, cookie)