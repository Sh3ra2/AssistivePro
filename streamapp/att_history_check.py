import datetime

# StartTime = '2022-01-01 01:00:00'
# EndTime = '2022-01-01 02:00:00'

#  -- Returns time difference in minutes.
def time_difference(start_time, end_time):
    start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    
    # -- gets time difference in time datatype
    diff = end - start
    # print(diff)

    #  -- convert time datatype to secounds in int the convert to minute by dividing with 60
    # print ((diff.total_seconds())/60)
    return ((diff.total_seconds())/60)

# time_difference(StartTime, EndTime)