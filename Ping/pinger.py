import json
import logging
import subprocess
from datetime import datetime
from io import StringIO
from queue import Queue
from threading import Thread

from Database.DatabaseController import Database


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

	def configure_logger (self):
		"""
		Configures logger and initiates logging by inserting info message
		"""
		# Hack for log line separator
		with open("pinger.log", "a") as log:
			log.write(
				"==============================================================================================\n")

		logging.basicConfig(filename="pinger.log", level=logging.DEBUG, filemode='a',
		                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
		logging.info("Started with max threads: %d", self.max_threads)

	@staticmethod
	def configure_console_logger ():
		"""
		Defines custom console logger for development and info for user
		"""
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)  # Change level for console logger in development mode
		formatter = logging.Formatter('%(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)

	def configure_database_logger (self):
		"""
		Defines custom database logger for future info
		"""
		database_logger = logging.StreamHandler(stream=self.database_stream_str)
		database_logger.setLevel(logging.NOTSET)
		formatter = logging.Formatter('%(levelname)-8s %(message)s')
		database_logger.setFormatter(formatter)
		logging.getLogger('').addHandler(database_logger)

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
		self.configure_logger()
		self.configure_console_logger()
		self.configure_database_logger()

		if len(self.hosts) < self.max_threads:
			logging.warning("Set workers is greater than required. Min required workers is %d.", len(self.hosts))

		if len(self.hosts) > 1:
			logging.info("Pinging %d hosts", len(self.hosts))
		else:
			logging.info("Pinging %s", self.hosts[0]["name"])

		for thread_id in range(self.max_threads):
			worker = Thread(target=self.pinger, args=(thread_id,))
			worker.setDaemon(True)
			worker.start()

		for ip in self.hosts:
			self.queue.put(ip)

		self.queue.join()

		if len(self.hosts) > 1:
			logging.info("Finished pinging %d hosts", len(self.hosts))
		else:
			logging.info("Finished pinging %s", self.hosts[0]["name"])

		self.save_log_to_database()
