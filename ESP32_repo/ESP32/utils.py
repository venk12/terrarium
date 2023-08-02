# Standard library imports
import socket
import sys
import uio
import os

# Local application/library-specific imports
from time_manager import read_time

# Constants declaration
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
MQTT_HANDLER_INSTANCE = None


def initialize_mqtt_handler(mqtt_handler):
    ''' 
    This function is needed for the correct operation of the utils module, 
    so that it also can access the mqtt_handler object.
    '''

    global MQTT_HANDLER_INSTANCE
    MQTT_HANDLER_INSTANCE = mqtt_handler


def resolve_mdns_hostname(hostname):
    """
    Resolves the provided hostname using the mDNS protocol.

    :param hostname: str - The hostname to be resolved
    :return: str - The resolved IP address
    """
    addr_info = socket.getaddrinfo(hostname, 1883)
    return addr_info[0][-1][0]


def truncate_log_file(file_path):
    """
    Truncates the log file if its size exceeds the maximum allowed size.
    The function keeps the second half of the file and overwrites the original file.
    Also, it sends the file over MQTT.
    
    :param file_path: str - Path to the log file to be truncated
    """
    
    
     # Check if file exists
    try:
        file_size = os.stat(file_path)[6]  # Get the size of the file
        if file_size > MAX_FILE_SIZE:
            if MQTT_HANDLER_INSTANCE is not None:
                MQTT_HANDLER_INSTANCE.mqtt_send_file(file_path)

            with open(file_path, 'r') as file:
                # Skip the first half of the content
                file.seek(int(file_size / 2))
                content = file.read()

            # Open the file in write mode and overwrite it with the truncated content
            with open(file_path, 'w') as file:
                file.write(content)

    except OSError:
        # Handle the case where the file does not exist
        pass


def convert_traceback(exc):
    """
    Converts an error message to a traceback string.

    :param exc: Exception - The exception object
    :return: str - The formatted traceback as a string
    """

    # Create a StringIO object to capture the traceback
    traceback_str = uio.StringIO()
    sys.print_exception(exc, traceback_str)

    return traceback_str.getvalue()


def file_log_error(exc, *args, **kwargs):
    """
    DEPRECATED
    Logs an error message to a file.

    :param exc: Exception - The exception object
    :param args: tuple - Additional messages to be included in the error logging
    :param kwargs: dict - Additional keyword arguments to be included in the error logging, formatted as key=value
    """
    
    traceback_str = convert_traceback(exc)
    
    
    # Constructing the error message
    error_message = f"[ERROR] {read_time()} {traceback_str} " + " ".join(map(str, args)) + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
    
    log_files = {'error_file':'error_logfile.log', 'log_file':'logfile.log'}
    
    for log_file in log_files:
        # truncate only if bigger than 1Mb
        truncate_log_file(log_file)

        try:
            with open(log_file, 'a') as file:
                file.write(error_message + '\n')
        except Exception as e:
            print(f"An error occurred while writing to the log file: {e}")
    

def debug_print(file_name, line_number, *args, **kwargs):
    """
    Prints a debug message with the filename and line number.

    :param file_name: str - The name of the file
    :param line_number: int - The line number
    :param args: tuple - Additional messages to be included in the debug print
    :param kwargs: dict - Additional keyword arguments to be included in the debug print, formatted as key=value
    """
    print(f"[DEBUG] {file_name}:{line_number}", *args, **kwargs)


def file_log(message, error=False, exc=None, print_flag = True):
    """
    Logs a message to a file and prints it.
    Use this function with error=True only if the exception is handled, not if it's just propagated upwards!

    :param message: str - The message to be included in the log file
    :param error: bool - If True, logs an error message to both logfile.log and error_logfile.log
    :param exc: Exception - An exception object to include in error_logfile.log (but not logfile.log)
    """

    if print_flag:
        print_log(message, error=error)

    log_type = "[ERROR]" if error else "[LOG]"
    log_message = f'{log_type} - {read_time()} - {message}'
    
    log_files = {'error_file':'error_logfile.log', 'log_file':'logfile.log'}
    # Truncate only if bigger than 1Mb
    truncate_log_file('logfile.log')

    # Logs both [LOG] or [ERROR] to the log file
    with open(log_files['log_file'], 'a') as file:
                file.write(log_message + '\n')
    
    if error:
        if exc:
            traceback_str = convert_traceback(exc)
            log_message += f"\n\tException traceback: {traceback_str}"
        
        # Logs [ERROR] to the log file, including the traceback if present
        with open(log_files['error_file'], 'a') as file:
                file.write(log_message + '\n')
        


def print_log(message, error=False, exc=None):
    """
    Prints a log message.

    :param message: str - The message to be included in the log print
    :param error: bool - If True, prints an error message
    :param exc: Exception - An exception object to include in the log print
    """
    log_type = "[ERROR]" if error else "[LOG]"
    log_message = f'{log_type} {message}'

    if error and exc:
        traceback_str = convert_traceback(exc)
        log_message += f"\n\tException traceback: {traceback_str}"

    print(log_message)


