import logging
import sys

from Notification.NotificationService import NotificationService
from Ping.Pinger import Pinger


def ping ():
	p = Pinger()
	p.run_threads()


def check ():
	n = NotificationService()
	n.notify()


def parse_arguments (args):
	if len(args):
		if args[0] == "ping":
			ping()
		elif args[0] == "notify":
			check()
		else:
			logging.error("No valid argument specified")
	else:
		logging.error("No argument specified")


if __name__ == "__main__":
	parse_arguments(sys.argv[1:])
