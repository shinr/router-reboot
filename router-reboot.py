# run every ... 5 minutes?
# ping 192.168.11.34 
# if we can't reach the host, reboot router
# yay?
# uses ping.py by george notaras, further modified by me
import telnetlib
import os
import ping
import time
import sys
import threading
import queue

target_host = ''
router_host = ''
reboot_limit = 4
wait_delay = 84

user_name = ''
password = ''

def check_message(message):
    if message == 'reboot':
        reboot_router()
        return 0
    elif message == 'reset_failed':
        print ("resetting failed packets to 0")
        return 0


def socket_loop(messages):
    failed_packets = 0
    while True:
        reached = ping_host(target_host)
        if reached:
            failed_packets = 0
        else:
            failed_packets += 1

        if failed_packets > reboot_limit:
            reboot_router()
        else:
            print ("current failed packets =", failed_packets, end="")
            print (", command? ")
        for i in range(wait_delay):
            time.sleep(1)
            if not messages.empty():
                item = messages.get()
                failed_packets = check_message(item)


def ping_host(host):
    print ("pinging ", host, "... ", end="")
    if ping.verbose_ping(host):
        print ("reached OK, ", end="")
        return True
    print ("not reached, ", end="")
    return False

# todo fix:
def reboot_router():
    print ("rebooting ", router_host, "...")
    try:
        connection = telnetlib.Telnet(router_host)
        connection.read_until("DD-WRT login: ")
        connection.write(user_name + '\n')
        connection.read_until("Password: ")
        connection.write(password+'\n')
        connection.read_until("# ", 15)
        connection.write("reboot" + '\n')
        connection.read_until("# ", 15)
        connection.close()
    except EOFError:
        return

def read_command(command):
    global message_queue
    if command == 'help':
        print ('available commands:')
        print ('help         - show help')
        print ('reboot       - reboot immediately')
        print ('reset_failed - resets failed packets to 0')
    elif command == 'reboot':
        message_queue.put(command)
    elif command == 'reset_failed':
        message_queue.put(command)



if __name__ == "__main__":		
    if len(sys.argv) < 5:
        print ("Usage: router-reboot.py [router-ip] [target-ip] [router-username] [router-password]")
        sys.exit()

    user_name = sys.argv[3]
    password = sys.argv[4]
    target_host = sys.argv[2]
    router_host = sys.argv[1]

    message_queue = queue.Queue()

    connections = threading.Thread(target=socket_loop, name="connections", args=[message_queue])
    connections.daemon = True
    connections.start()



    while True:
        user_command = input()
        read_command(user_command)