# run every ... 5 minutes?
# ping 192.168.11.34 
# if we can't reach the host, reboot router
# yay?

import telnetlib
import os
import ping
import time
import sys

target_host = ''
router_host = ''
failed_packets = 0
wait_delay = 84

user_name = ''
password = ''

def ping_host(host):
	print "pinging " + host + "... ",
	if ping.verbose_ping(host):
		print "reached OK, ",
		return True
	print "not reached, ",
	return False

def reboot_router():
	print "rebooting "+ router_host + "..."
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
if len(sys.argv) < 5:
	print "Usage: router-reboot.py [router-ip] [target-ip] [router-username] [router-password]"
	sys.exit()
user_name = sys.argv[3]
password = sys.argv[4]
target_host = sys.argv[2]
router_host = sys.argv[1]

while True:
	reached = ping_host(target_host)
	if reached:
		failed_packets = 0
	else:
		failed_packets += 1

	if failed_packets > 4:
		reboot_router()
	else:
		print "current failed packets = %d" % failed_packets
	time.sleep(wait_delay)