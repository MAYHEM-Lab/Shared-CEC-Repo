#!/usr/bin/python
import os
import sys

_DROPBOX_DIR = "/home/gsn/Dropbox"
_ERRORS = "/home/gsn/Dropbox/errors"
DEBUG=False
#####################################
#Pending:  Type Checking
def process_files(fname,fnamenew,fnameout,dont_append=False):
    #Step 2) append diff fnamenew and/to sensor1/2_fname
    #use double curly braces to insert a curly brace in a string processed by format
    #we overwrite fnameout here if any
    global _ERRORS
    global DEBUG
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
            print err_fname
            errstr =  'ERROR: difference between {0} and {1} should be 0, it is {2}'.format(fname,fnamenew, os.path.getsize("{0}".format(fnameout)))
            res = os.popen("cat {0}".format(fnameout)).read()
            with open(err_fname) as f:
                f.write(errstr)
                f.write(res)
        elif DEBUG:
            print 'Sanity check passed. Cleaning up...'
    #cleanup
    #leave fnameout for sanity check
    os.remove("{0}".format(fnameout))

def main():
    '''For all files in PowWow directory, calculate the diff sanitize the diff and append
    to .csv files. File paths are hardcoded as they are never expected to change.'''
    
    _DROPBOX_DIR = "/home/gsn/Dropbox/"
    _DATA_FILES = _DROPBOX_DIR + "PowWow"
    GSN_DATA_DIR = "/opt/gsn/gsn/data/"
    tempfile = "/opt/gsn/"
    global _ERRORS

    os.system("mkdir -p {0}".format(_ERRORS))
    
    file_list = os.listdir(_DATA_FILES)
    for files in file_list:
        gsn_data_file = GSN_DATA_DIR + files
        abs_files = _DATA_FILES + "/" + files
        if os.path.isfile(gsn_data_file):
            process_files(gsn_data_file, abs_files, tempfile + files + '.tmp')
        else:
            pass
            #write to errors directory in Dropbox.

######################################
if __name__ == "__main__":
    main()
######################################



