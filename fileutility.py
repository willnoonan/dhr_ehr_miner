#AUTHOR: William Noonan

import os
import timeutility

DATAROOT = r"C:\Users\nnnwn00\Documents\data\osteo"
OSTEODATAXLSX = os.path.join(DATAROOT, "dhr_traumaresearch_osteofractures.xlsx")
OUTPUTROOT = os.path.join(DATAROOT, "OUTPUT")
S72DATA=os.path.join(DATAROOT,"S72-data collection file.xlsx")
SFILEROOT = os.path.join(DATAROOT, "sfiles")

def getSfilesDict():
    import os
    import re
    from collections import namedtuple
    sfiles_list = [file for file in os.listdir(SFILEROOT) if re.match(r'S\d+', file) and file.endswith('.xls')]
    sfile_abbrevs = [os.path.splitext(file)[0][:3] for file in sfiles_list]
    sfile_paths = [os.path.join(SFILEROOT, file) for file in sfiles_list]
    sfile_dict = {sfile:sfile_path for sfile, sfile_path in zip(sfile_abbrevs, sfile_paths)}
    return sfile_dict

def getSfilesDataFrameDict(simplifycolumnheaders=True): #TODO kwarg?
    import pandas as pd
    import re
    import dfutility
    sfile_dict = getSfilesDict()
    sfile_df_dict = {sfile:pd.read_excel(sfile_path) for sfile, sfile_path in sfile_dict.items()}
    for df in sfile_df_dict.values(): dfutility.simplifyDataFrameColumnHeaders(df, inplace=True) #TODO kwargs?
    for key, df in sfile_df_dict.items(): df['FILE_NAME'] = key # convenient for filtering
    for key, df in sfile_df_dict.items(): #TODO safer to create new dict w/comprehension then update sfile_df_dict?
        if 'EXCLUDE' in df.columns:
            sfile_df_dict[key] = df[~df.EXCLUDE] #TODO possible SettingWithCopyWarning bug if .copy() not used?
    return sfile_df_dict

def getSfilesNamedTuple():
    import fileutility
    sfile_dict = getSfilesDict()
    return fileutility.named_tuple_from_dict(sfile_dict)

def getSfileDataFrameNamedTuple():
    from collections import namedtuple
    #TODO allow user to specify sheet name
    #sfilesheetnames = {sfile: dfutility.getExcelFileSheetNames(path) for sfile, path in sfile_dict.items()}
    #end_TODO
    sfile_df_dict = getSfilesDataFrameDict()
    SFileDF = namedtuple('SFileDF', sorted(sfile_df_dict))
    return SFileDF(**sfile_df_dict)


def makedirs(targetpath):
    import os
    if not os.path.exists(targetpath):
        os.makedirs(targetpath)

def maketodayfolder(relpath='', root=OUTPUTROOT, dateformat=timeutility._defaultdateformatstr): # don't have to pass in keyword args
    #Makes and returns path of folder named with today's date
    import os
    targetpath = os.path.join(root, timeutility.gettodaydate(dateformat=dateformat), relpath) #TODO rethink
    makedirs(targetpath)
    return targetpath

def makenowtimefolder(root=maketodayfolder(), timeformat=timeutility._defaulttimeformatstr): # function call here is valid
    #TODO what is it going to be made relative to? path returned from maketodayfolder?
    import os
    targetpath = os.path.join(root, timeutility.gettimenow(timeformat=timeformat))
    makedirs(targetpath)
    return targetpath

def maketodayandtimenowfolders(root):
    todaypath = maketodayfolder(root=root)
    timepath = makenowtimefolder(root=todaypath)
    return timepath


NETBUPROOT = r"Z:\Trauma\Temp\transfer\wnoonan\bup\datamanager"
# NETBUPROOT = r"C:\Users\nnnwn00\Documents\testshutil"
SOURCE = r"C:\Users\nnnwn00\Documents\pycharmprojs\datamanager"

def makenetworktimefolder():
    return maketodayandtimenowfolders(NETBUPROOT)

def backupPythonFiles():
    #TODO broken
    import os
    import shutil
    import glob

    DEST = os.path.join(maketodayandtimenowfolders(NETBUPROOT))
    for file in glob.glob(os.path.join(SOURCE,"*.py")): shutil.copyfile(file, os.path.join(DEST, os.path.split(file)[0]))


def file_modified_today(filepath):
    import os
    from datetime import datetime
    date = datetime.today(); date = (date.day, date.month, date.year)
    fmoddate = datetime.fromtimestamp(os.path.getmtime(filepath)); fmoddate = (fmoddate.day, fmoddate.month, fmoddate.year)
    if date == fmoddate:
        return True
    else:
        return False

def list_files_modified_today(startdir='.', ext=None):
    if not ext: ext = ''
    return [os.path.join(root, file) for root, dirs, files in os.walk(startdir) for file in files if file.endswith(ext)
            and file_modified_today(os.path.join(root,file))]