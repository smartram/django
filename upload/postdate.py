'''
Created on Mar 24, 2013

@author: venkataedara
'''
months={1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'June',
        7:'July',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec'}

DAY_INSECS=24 * 60 * 60
HOUR_INSECS=1 * 60 * 60

def gettimeformat(now,timestamp):
    elapsed=now-timestamp
    total_seconds=int(elapsed.total_seconds())    
    
    if total_seconds > DAY_INSECS: # more than 24 hours. so give date only.
        if  timestamp.month in months:
            month=months[timestamp.month]
        else:
            month=`timestamp.month`
               
        timeformat="%s-%s"%(month,`timestamp.day`)
    
    elif total_seconds >= HOUR_INSECS: # more than 1 hour
        num_of_hours=total_seconds / HOUR_INSECS

        if num_of_hours==1:
            timeformat="%s hour"%(num_of_hours)
        else:
            timeformat="%s hours"%(num_of_hours)

                
    elif total_seconds > 60:# more than 1 minute. so give num of minutes elapsed
        minutes=int(total_seconds/60)
        timeformat="%d mins"%(minutes)
    else:
        timeformat="%d secs"%(total_seconds)
            
    return timeformat