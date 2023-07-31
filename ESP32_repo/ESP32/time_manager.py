import machine
import time
import _thread

# Initialize the Real-Time Clock (RTC)
rtc = machine.RTC()


lock = _thread.allocate_lock()

def set_time(year, month, day, hour, minute, sec):
    """
    Set the date and time for the RTC.

    :param year: int - The year to set
    :param month: int - The month to set
    :param day: int - The day to set
    :param hour: int - The hour to set
    :param minute: int - The minute to set
    :param sec: int - The second to set
    """

    from utils import print_log
    
    with lock:
        rtc.datetime((year, month, day, 0, hour, minute, sec, 0))
        
    print_log("date & time set! current date & time: %d-%02d-%02d %02d:%02d:%02d" % (year, month, day, hour, minute, sec))


def read_time():
    """
    Read the current date and time from the RTC.

    :return: str - A string representing the current date and time in the format "YYYY-MM-DD HH:MM:SS"
    """

    with lock:
        year, month, day, weekday, hours, minutes, seconds, subseconds = rtc.datetime()
        time_str = "%d-%02d-%02d %02d:%02d:%02d" % (year, month, day, hours, minutes, seconds)
    
    
    return time_str

