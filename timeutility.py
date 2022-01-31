#AUTHOR: William Noonan

_defaultdateformatstr = '%d%m%Y'
_defaulttimeformatstr = '%H%M%S'

#would like to send output to folder named by date
def _gettodaydatetime():
    from datetime import datetime
    return datetime.today() # a date

def gettodaydate(dateformat=_defaultdateformatstr):
    return _gettodaydatetime().strftime(dateformat)

def gettimenow(timeformat=_defaulttimeformatstr):
    return _gettodaydatetime().strftime(timeformat)