# Standard library imports
import time
import network
import socket

# Local application/library-specific imports
from utils import print_log, file_log
from mqtt import initialize_wifi_handler

MAX_CONNECTION_ATTEMPTS = 10

class TimeoutError(Exception):
    pass

def url_decode(input):
    """
    Decodes a URL-encoded string.

    :param input: URL-encoded string
    :return: str - Decoded string
    """
    input = input.replace("+", " ")
    i = 0
    while i < len(input):
        if input[i] == '%' and (i < len(input) - 2):
            try:
                input = input[:i] + chr(int(input[i + 1:i + 3], 16)) + input[i + 3:]
            except ValueError as exc:
                print_log(f"Invalid percent-encoded character: {input[i:i+3]}", error=True, exc=exc)
                raise
        i += 1
    return input


def handle_client(client_socket):
    """
    Handles client requests to get or set Wi-Fi credentials.

    :param client_socket: Client socket object
    :return: Tuple[str, str] - Tuple containing SSID and password if set, otherwise None
    """
    try:
        # HTML code for the Wi-Fi Configuration page
        HTML = """<!DOCTYPE html>
        <html>
        <head><title>Wi-Fi Config</title></head>
        <body>
            <h2>Wi-Fi Configuration</h2>
            <form action="/set_wifi">
                SSID:<br>
                <input type="text" name="ssid"><br>
                Password:<br>
                <input type="password" name="password"><br><br>
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """

        request = client_socket.recv(1024)
        request = request.decode()

        lines = request.split('\n')
        for line in lines:
            if line.startswith('GET /set_wifi'):
                params = line.split(' ')[1].split('?')[1].split('&')
                ssid = url_decode(params[0].split('=')[1])
                password = url_decode(params[1].split('=')[1])

                client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                client_socket.send("<p>Wi-Fi settings saved. You can now close this page.</p>")
                client_socket.close()

                return ssid, password

        client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        client_socket.send(HTML)
        client_socket.close()

        return None, None
    
    except Exception as exc:
        print_log(f"Error handling client", error=True, exc=exc)
        raise


def start_ap():
    """
    Starts an Access Point (AP) for Wi-Fi configuration.
    """
    try:
        essid = "ESP32_Setup"
        password = "abcdefgh"
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=essid, password=password)
    except Exception as exc:
        print_log(f"Error starting Access Point", error=True, exc=exc)
        raise


def start_web_server():
    """
    Starts a web server for Wi-Fi configuration.

    :return: Tuple[str, str] or None - Tuple containing SSID and password if set, otherwise None
    """
    try:
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

        s = socket.socket()
        s.bind(addr)
        s.listen(1)

        print_log("Listening for connections on {}".format(addr))
        
        while True:
            cl, addr = s.accept()
            print_log("Client connected from {}".format(addr))
            ssid, password = handle_client(cl)
            if ssid:
                s.close()  # Close the socket
                return ssid, password
    except Exception as exc:
        print_log(f"Web server error", error=True, exc=exc)
        raise


class WIFI_handler:
    def __init__(self):
        self.ssid, self.password = self.check_wifi_credentials()
        self.setup_wifi()
        initialize_wifi_handler(self)


    def check_wifi_credentials(self):
        """
        Check if WiFi credentials are available from a file or start configuration if not.

        :return: Tuple[str, str] - The SSID and password retrieved or configured
        """
        ssid, password = "", ""

        try:
            with open('wifi_creds.txt', 'r') as f:
                ssid, password = f.read().split(',')

            print_log('Wifi credentials found')

        except OSError as e:
            # If wifi_creds.txt not found:
            file_log('File not present, starting AP for setup')
            ssid, password = self.start_wifi_creds_config()

        return ssid, password
    

    def start_wifi_creds_config(self):
        """
        Start the WiFi credentials configuration process.

        :return: Tuple[str, str] - A tuple containing the WiFi SSID and password entered by the user.
        """
        start_ap()  # Start the access point for WiFi setup

        # Start the web server and retrieve the SSID and password from the user
        ssid, password = start_web_server()

        try:
            with open('wifi_creds.txt', 'w') as f:
                f.write(f'{ssid},{password}')
        except Exception as exc:
            print_log(f"Could not save WiFi credentials to file", error=True, exc=exc)
            raise

        print_log('Wifi ssid and password retrieved from user.')
        #debug_print('wifi.py', 26, 'Wifi ssid and password retrieved from user.')
        return ssid, password


    def setup_wifi(self):
        """
        Connect to a WiFi network using provided credentials.
        Initializes self.wlan

        :param ssid: str - The SSID of the WiFi network
        :param password: str - The password of the WiFi network
        """
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        try:
            self.wlan.connect(self.ssid, self.password)
        except Exception as exc:
            print_log(f"Could not connect to WiFi network", error=True, exc=exc)
            raise

        # Give WiFi 30 seconds to connect
        start_time = time.time()
        while not self.isconnected():
            if time.time() - start_time > 30:  # After 30 seconds
                break
            time.sleep(0.1)
        
        print_log(f'connected: {self.isconnected()} after {time.time() - start_time}s')


    def isconnected(self):
        return self.wlan.isconnected()
    

    def try_connect(self):
        '''
        Tries to connect to the wifi for 30s, than waits for 10s.
        This for up to 10 times, total 400s.
        '''
        attempts = 0
        while attempts < MAX_CONNECTION_ATTEMPTS:
            attempts += 1

            if not self.isconnected():
                # Log WLAN Reconnect Attempt
                print_log('WLAN not connected, trying to reconnect.')

                try:
                    self.setup_wifi()
                except Exception as exc:
                    print_log(f"Error trying to reconnect", error=True, exc=exc)
                    raise
            else:
                break
            
            # Try again afte 10s
            time.sleep(10) 
        else: 
            raise TimeoutError('Unable to connect to the wifi')
