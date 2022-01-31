# AUTHOR: William Noonan

def searchforfile(foi_ext='.py', startdir='.', verbose=False):
    import os
    completefoilist = list()
    for root, dirs, files in os.walk(startdir):
        if verbose:
            print(f"Searching {root}")
        foilist = sorted([file for file in files if file.endswith(foi_ext)])
        if foilist:
            completefoilist.extend([os.path.join(root, file) for file in foilist])
    if not completefoilist:
        print(f"Could not find any files ending in {foi_ext}")
    return completefoilist


def searchforfile2(foi_ext='.py', startdir='.', verbose=False):
    import os
    for root, dirs, files in os.walk(startdir):
        if verbose:
            print(f"Searching {root}")
        for file in files:
            if file.endswith(foi_ext):
                yield os.path.join(root, file)


def functiondirsearch(function, startdir='.', verbose=False):
    import os
    for root, dirs, files in os.walk(startdir):
        if verbose:
            print(f"Searching {root}")
        for dir in dirs:
            if function(dir):
                yield os.path.join(root, dir)


def functiondirsearch(function, startdir='.'):
    import os
    dirlist = os.listdir(startdir)  # this will throw an exception if it doesn't exist
    return [os.path.join(root, dir) for root, dirs, files in os.walk(startdir) for dir in dirs if function(dir)]


def functionfilesearch(function, startdir='.'):
    import os
    return [os.path.join(root, file) for root, dirs, files in os.walk(startdir) for file in files if function(file)]


def nloopcopy(src, dst, n, verbose=True):
    import os, shutil
    from datetime import datetime
    for x in range(n):
        if verbose:
            timenow = datetime.now()
            print(f"{timenow.hour}:{timenow.minute}")
        dst = shutil.copytree(src, os.path.join(dst, "_Trauma"))
        print(dst)


def nloopcopy2(src, dst, n, verbose=True):
    import os, shutil
    from datetime import datetime
    for x in range(n):
        start_time = datetime.now()
        path = shutil.copytree(src, os.path.join(dst, str(x)))
        if verbose:
            print(f"{start_time.hour}:{start_time.minute}, {path}")


def timeloopcopy(src, dst, endtime):
    import os, shutil
    from datetime import datetime
    while datetime.now() < endtime:
        dst = shutil.copytree(src, os.path.join(dst, "_Trauma"))
        print(dst)
    print("time out")
