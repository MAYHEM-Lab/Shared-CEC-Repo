#!/usr/bin/python
import os
import sys

DEBUG=False
def process_files(fname,fnamenew,fnameout,err_fname='errors.txt',dont_append=False):
    ''' Calculates diff between fname and fnamenew and appends the change to fname.
        fnameout is temp file used to store the diff.
    '''    
    os.system("diff {0} {1}| grep '^>'|awk -F'> ' '{{print $2}}' > {2}".format(fname,fnamenew,fnameout))
    if DEBUG:
        res = os.popen("cat {0}".format(fnameout)).read()
        print 'DEBUG: adding diffs: '
        print res

    #append fnameout to fname
    if dont_append:
        print 'testing: not appending to file {0}'.format(fname)
    else:
        os.system("cat {0} >> {1}".format(fnameout,fname))
        #sanity check - there should be nothing in fnameout file
        os.system("diff {0} {1} |grep '^>'|awk -F'> ' '{{print $2}}' > {2}".format(fname,fnamenew,fnameout))
        if os.path.getsize("{0}".format(fnameout)) != 0:
            err_fname = _ERRORS + "/" + fnamenew.split("/")[-1:] + ".err"
            errstr =  'ERROR: difference between {0} and {1} should be 0, it is {2}'.format(fname,fnamenew, os.path.getsize("{0}".format(fnameout)))
            res = os.popen("cat {0}".format(fnameout)).read()
            with open(err_fname) as f:
                f.write(errstr)
                f.write(res)
        elif DEBUG:
            print 'Sanity check passed. Cleaning up...'
    os.remove("{0}".format(fnameout))

def usage():
    print '''Usage: python dropbox_sync_general.py <dropbox_dir_to_monitor> <local_directory>'''
    sys.exit(0)


def main():
    
    if len(sys.argv) < 3:
        usage()
    
    DROPBOX_DIR = sys.argv[1].strip("/") 
    DATA_DIR = sys.argv[2].strip("/")
    
    file_list = os.listdir(DROPBOX_DIR)
    for files in file_list:
        data_file = DATA_DIR + "/" + files
        abs_files = DROPBOX_DIR + "/" + files
        if os.path.isfile(data_file):
            process_files(data_file, abs_files, files + '.tmp')
        else:
            pass
            #write to errors directory in Dropbox.

if __name__ == "__main__":
    main()



