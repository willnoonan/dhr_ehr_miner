import os

def renamedirs(path='.'):
    import os, re
    items = os.listdir(path)
    for item in items:
        if re.match(r'^\d+', item):
            oldpath = os.path.join(path, item)
            split = re.split(r'^(\d{4})', item)
            date = split[1]
            rest = split[2]
            newdate = "{2}{3}{0}{1}".format(*date)
            newname = f"{newdate}{rest}"
            newpath = os.path.join(path, newname)
            os.rename(oldpath, newpath)
            print(f"Renamed '{oldpath}' to '{newpath}'")
