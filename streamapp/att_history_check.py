import datetime

StartTime = '2022-01-01 01:00:00'
EndTime = '2022-01-01 02:00:00'

def time_difference(start_time, end_time):
    """Returns the time difference between two timestamps in seconds."""
    start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    diff = end - start
    return (diff.total_seconds())/60