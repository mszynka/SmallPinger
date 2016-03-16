import logging


# noinspection SpellCheckingInspection
class Loggers:
	@staticmethod
	def configure_logger (max_threads):
		"""
		Configures logger and initiates logging by inserting info message
		:param max_threads: Max number of workers
		"""
		# Hack for log line separator
		with open("pinger.log", "a") as log:
			log.write(
				"==============================================================================================\n")

		logging.basicConfig(filename="pinger.log", level=logging.DEBUG, filemode='a',
		                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
		logging.info("Started with max threads: %d", max_threads)

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

	@staticmethod
	def configure_database_logger (database_stream_str):
		"""
		Defines custom database logger for future info
		:param database_stream_str: Database logger stream
		"""
		database_logger = logging.StreamHandler(stream=database_stream_str)
		database_logger.setLevel(logging.NOTSET)
		formatter = logging.Formatter('%(levelname)-8s %(message)s')
		database_logger.setFormatter(formatter)
		logging.getLogger('').addHandler(database_logger)

	@staticmethod
	def entry_message (hosts, max_threads):
		if len(hosts) < max_threads:
			logging.warning("Set workers is greater than required. Min required workers is %d.", len(hosts))

		if len(hosts) > 1:
			logging.info("Pinging %d hosts", len(hosts))
		else:
			logging.info("Pinging %s", hosts[0]["name"])

	@staticmethod
	def exit_message (hosts):
		if len(hosts) > 1:
			logging.info("Finished pinging %d hosts", len(hosts))
		else:
			logging.info("Finished pinging %s", hosts[0]["name"])
