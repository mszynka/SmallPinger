import json
import logging
import subprocess
from datetime import datetime
from io import StringIO
from queue import Queue
from threading import Thread

from Database.DatabaseController import Database
from Ping.Loggers import Loggers


# noinspection SpellCheckingInspection
class Pinger:
	def __init__ (self):
		"""
		Default constructor
		Sets config values and destination hosts
		"""
		self.database = Database()
		self.database_stream_str = StringIO()
		self.database_date_time = datetime.today().strftime("%d.%m.%Y %H:%M:%S")
		self.queue = Queue()
		self.config_path = "config/config.json"
		self.hosts_path = "config/hosts.json"

		with open(self.hosts_path) as data_file:
			self.hosts = json.load(data_file)

		with open(self.config_path) as data_file:
			config = json.load(data_file)
			self.max_threads = config.get("maxWorkers") if config.get("maxWorkers") else 4
			self.useSqlte = config.get("usesDatabase") if config.get("usesDatabase") else True
			self.sqlitePath = config.get("databasePath") if config.get("databasePath") else "sqlite_log.db"

	def save_log_to_database (self):
		self.database.log(self.database_date_time, str(self.hosts), self.database_stream_str.getvalue())

	def pinger (self, thread_id):
		"""
		Pings subnet
		:param thread_id: Worker ID
		"""
		while True:
			host = self.queue.get()
			logging.debug("Thread %s: Pinging %s", thread_id, host["name"])
			logging.debug("ping -c 1 %s", host["url"])
			ret = subprocess.call("ping -c 1 %s" % host["url"], shell=True, stdout=open('/dev/null', 'w'),
			                      stderr=subprocess.STDOUT)
			if ret == 0:
				logging.info("%s: is alive", host["name"])
			else:
				logging.error("%s: did not respond", host["name"])
			logging.debug("Thread %s: Ping returned: %s with url: %s ", thread_id, ret, host["url"])
			self.queue.task_done()

	def run_threads (self):
		"""
		Runs threads with pinger
		"""
		Loggers.configure_logger(self.max_threads)
		Loggers.configure_console_logger()
		Loggers.configure_database_logger(self.database_stream_str)
		Loggers.entry_message(self.hosts, self.max_threads)

		for thread_id in range(self.max_threads):
			worker = Thread(target=self.pinger, args=(thread_id,))
			worker.setDaemon(True)
			worker.start()

		for ip in self.hosts:
			self.queue.put(ip)

		self.queue.join()

		Loggers.exit_message(self.hosts)
		self.save_log_to_database()
