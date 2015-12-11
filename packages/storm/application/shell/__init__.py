#
# This file is part of STORM.
#
# STORM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STORM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STORM.  If not, see <http://www.gnu.org/licenses/>.
#

from storm import engine

from storm.application.shell import printer

from storm.module import properties
from storm.module import resource

import argparse
import multiprocessing
import os
import sys

application_name = "storm"

#
# Event queue
#
class EventQueue:

	def __init__(self):
	
		self.__queue = multiprocessing.Queue()
		
	def __iter__(self):
	
		event = self.__queue.get()
		while not event[1] != "finished":
			yield event
			event = self.__queue.get()
			
	def dispatch(self, task, name, value):
	
		self.__queue.put(( task, name, value ))
		
#
# Command error
#
class CommandError(Exception):

	def __init__(self, args):
	
		super().__init__(args)
		
#
# Main function
#
def main():

	# Look for data directory
	try:
		if sys.platform == "darwin":
			from AppKit import NSSearchPathForDirectoriesInDomains
			ddp = NSSearchPathForDirectoriesInDomains(14, 1, True)
			appdata_res = resource.ref(ddp[0])
			data_res_name = application_name
		elif sys.platform == "win32":
			appdata_res = resource.ref(os.environ['APPDATA'])
			data_res_name = application_name
		else:
			raise LookupError("UNIX like application data directory")
	except BaseException:
		appdata_res = resource.ref(os.environ["HOME"])
		data_res_name = ".{}".format(application_name)
	data_res = appdata_res.ref(data_res_name)
	
	# Create printer factory
	printer_fact = printer.PrinterFactory()
	
	# Execute command
	state_res = data_res.ref("engine.json")
	
	try:
	
		messages = properties.load(__file__, "messages")
		
		# Parse arguments
		def argparse_command(cmd_name):
			cmd_fn_name = "command_execute_{}".format(cmd_name)
			if cmd_fn_name in globals():
				return globals()[cmd_fn_name]
			else:
				msg = messages["error"]["unrecognized_command"]
				raise argparse.ArgumentTypeError(msg.format(cmd_name))
				
		parser = argparse.ArgumentParser(
			prog=application_name,
			description=messages["application"]["description"]
		)
		parser.add_argument(
			"command",
			metavar="command",
			type=argparse_command,
			nargs=1,
			help=messages["argument"]["command"]
		)
		parser.add_argument(
			"arguments",
			metavar="args",
			nargs=argparse.REMAINDER,
			help=messages["argument"]["args"]
		)
		parser.add_argument(
			"-e",
			required=False,
			action="store_true",
			default=False,
			dest="exceptions",
			help=messages["argument"]["exceptions"]
		)
		parser.add_argument(
			"-v",
			required=False,
			action="store_true",
			default=False,
			dest="verbose",
			help=messages["argument"]["verbose"]
		)
		args = parser.parse_args(sys.argv[1:len(sys.argv)])
		
		# Update printer factory level
		if args.verbose:
			printer_fact.level = 1
		else:
			printer_fact.level = 0
		
		# Execute the command
		args.command[0](eng, printer_fact, messages, args.arguments)
		return 0
		
	except CommandError as err:
	
		# Print error output
		pr = eng.printer(sys.stderr)
		err_msg = "{}".format(err)
		if args.exceptions:
			err_msg = "{}:\n{}".format(err_msg, traceback.format_exc())
		pr.append(err_msg, "red", "bright")
		pr.print()
		return 1
		
	finally:
	
		eng.store()
		
#
# Command COMMANDS
#
def command_execute_commands(eng, printer_fact, messages, arguments):

	pr = printer_fact.printer(sys.stdout)
	
	# Calculate description position
	desc_pos = 0
	for cmd_name in messages["command"]:
		desc_pos = max(desc_pos, len(cmd_name))
			
	# Print command descriptions
	new_line = ""
	for cmd_name, cmd_desc in messages["command"].items():
		cmd_name_ljust = cmd_name.ljust(desc_pos)
		pr.append("{}{}  {}".format(new_line, cmd_name_ljust, cmd_desc))
		new_line = "\n"
	pr.print()
	
#
# Execute a command for an engine call
#
def command_execute_engine_call(eng, eng_fn, arguments):

	event_queue = EventQueue()
	eng = engine.Engine(state_res, event_queue)

