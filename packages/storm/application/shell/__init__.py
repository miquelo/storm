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
import os
import queue
import sys
import threading
import traceback

application_name = "storm"
messages = properties.load(__file__, "messages")

#
# Event queue
#
class EventQueue:

	def __init__(self):
	
		self.__queue = queue.Queue()
		self.__closed = False
		
	def __iter__(self):
	
		while not self.__closed:
			yield self.__queue.get()
		
	def dispatch(self, task, name, value):
	
		self.__queue.put(( task, name, value ))
		
	def close(self):
	
		self.__closed = True
		
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
	
	try:
	
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
		
		# Create printer factory
		printer_fact = printer.PrinterFactory(1 if args.verbose else 0)
		
		# Execute the command
		args.command[0](data_res, printer_fact, args.arguments)
		return 0
		
	except CommandError as err:
	
		# Print error output
		pr = printer_fact.printer(sys.stderr)
		err_msg = "{}".format(err)
		if args.exceptions:
			err_msg = "{}:\n{}".format(err_msg, traceback.format_exc())
		pr.append(err_msg, "red", "bright")
		pr.print()
		return 1
		
#
# Command COMMANDS
#
def command_execute_commands(data_res, printer_fact, arguments):

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
# Command PLATFORMS
#
def command_execute_platforms(data_res, printer_fact, arguments):

	# Parse arguments
	parser = command_parser("platforms")
	parser.parse_args(arguments)
	
	# Shared resources
	pr = printer_fact.printer(sys.stdout)
	
	# Init function
	def init_fn(eng):
	
		return eng.platforms()
		
	# Event function
	def event_fn(eng, task, name, value):
	
		if name == "platform-entry":
			plat_name = value["name"]
			style = None if value["available"] else "dim"
			plat_prov = value["provider"]
			pr.append("{} ({})".format(plat_name, plat_prov), None, style)
			pr.print()
			
	command_engine_execute(data_res, init_fn, event_fn)
	
#
# Command REGISTER
#
def command_execute_register(data_res, printer_fact, arguments):

	# Parse arguments
	parser = command_parser("register")
	parser.add_argument(
		"platform_name",
		metavar="platform",
		type=str,
		nargs=1,
		help=messages["argument"]["platform"]
	)
	parser.add_argument(
		"provider",
		metavar="provider",
		type=str,
		nargs=1,
		help=messages["argument"]["register.provider"]
	)
	parser.add_argument(
		"props_res",
		metavar="props_res",
		type=argparse_resource,
		nargs="*",
		help=messages["argument"]["register.props_res"]
	)
	args = parser.parse_args(arguments)
	
	# Init function
	def init_fn(eng):
	
		name = args.platform_name[0]
		prov = args.provider[0]
		props = props_collect(args.props_res)
		return eng.register(name, prov, props)
		
	# Event function
	def event_fn(eng, task, name, value):
	
		pass
		
	command_engine_execute(data_res, init_fn, event_fn)
	
#
# Command DISMISS
#
def command_execute_dismiss(data_res, printer_fact, arguments):

	# Parse arguments
	parser = command_parser("dismiss")
	parser.add_argument(
		"platform_name",
		metavar="platform",
		type=str,
		nargs=1,
		help=messages["argument"]["platform"]
	)
	parser.add_argument(
		"-d",
		required=False,
		action="store_true",
		default=False,
		dest="destroy",
		help=messages["argument"]["dismiss.destroy"]
	)
	args = parser.parse_args(arguments)
	
	# Init function
	def init_fn(eng):
	
		name = args.platform_name[0]
		return eng.dismiss(name, args.destroy)
		
	# Event function
	def event_fn(eng, task, name, value):
	
		pass
		
	command_engine_execute(data_res, init_fn, event_fn)
	
#
# Create parser for command
#
def command_parser(cmd_name):

	return argparse.ArgumentParser(
		prog="{} {}".format(application_name, cmd_name),
		description=messages["command"][cmd_name]
	)
	
#
# Execute engine command function
#
def command_engine_execute(data_res, init_fn, event_fn):
	
	try:
		state_res = data_res.ref("engine.json")
		queue = EventQueue()
		eng = engine.Engine(state_res, queue, sys.stdout, sys.stderr)
		task = init_fn(eng)
		
		for event in queue:
			event_fn(eng, event[0], event[1], event[2])
			if event[1] == "finished":
				queue.close()
		return task.result()
	except KeyboardInterrupt:
		task.cancel()
		return None
	except BaseException as err:
		raise CommandError(err)
	finally:
		eng.store()
		
#
# Resource argument parsing
#		
def argparse_resource(uri):

	res = resource.ref(uri)
	
	if res.exists():
		return res
	else:
		msg = messages["error"]["invalid_resource_id"].format(uri)
		raise argparse.ArgumentTypeError(msg)
		
#
# Collect properties from files
#
def props_collect(args_props_res):

	props = {}
	for props_res in args_props_res:
		props_file = props_res.open("r")
		props_in = jsons.read(props_file)
		if props_in is None or not props_in.isdict():
			raise Exception("Properties must be a dictionary")
		util.merge_dict(props, props_in.value())
		props_file.close()
	return props

