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

from storm.module import properties
from storm.module import util

import json
import os.path
import argparse
import sys
import traceback

application_name = os.path.basename(sys.argv[0])

#
# Command error
#
class CommandError(Exception):

	def __init__(self, args):
	
		super().__init__(args)

#
# Directory argument parsing
#		
def argparse_directory(path):

	messages = properties.load(__file__, "messages")
	
	if not os.path.exists(path):
		msg = messages["error"]["dir_does_not_exists"].format(path)
		raise argparse.ArgumentTypeError(msg)
	if not os.path.isdir(path):
		msg = messages["error"]["not_a_dir"].format(path)
		raise argparse.ArgumentTypeError(msg)
		
	if os.path.isabs(path):
		return path
	return os.path.abspath(path)
		
#
# Main function
#
def main():

	# Look for data directory
	try:
		if sys.platform == "darwin":
			from AppKit import NSSearchPathForDirectoriesInDomains
			ddp = NSSearchPathForDirectoriesInDomains(14, 1, True)
			data_dir = os.path.join(ddp[0], application_name)
		elif sys.platform == "win32":
			data_dir = os.environ['APPDATA']
			data_dir = os.path.join(data_dir, application_name)
		else:
			raise Exception("Unknown operating system")
	except BaseException:
		home_dir = os.environ["HOME"]
		data_dir = os.path.join(home_dir, ".{}".format(application_name))
		
	if not os.path.exists(data_dir):
		os.mkdir(data_dir)
		
	# Execute command
	eng = engine.Engine(data_dir)
	
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
		
		# Update printer level
		if args.verbose:
			eng.printer_level = 1
		else:
			eng.printer_level = 0
			
		# Execute the command
		args.command[0](eng, args.arguments)
		return 0
		
	except CommandError as err:
	
		# Print error output
		pr = eng.printer(sys.stderr)
		err_msg = "{}".format(err)
		if args.exceptions:
			err_msg = "{}:\n{}".format(err_msg, traceback.format_exc())
		pr.print(err_msg, 0, "red", "bright")
		return 1
		
	finally:
	
		# Store engine configuration
		eng.store()
		
#
# Command COMMANDS
#
def command_execute_commands(eng, arguments):

	messages = properties.load(__file__, "messages")
	pr = eng.printer(sys.stdout)
	
	# Calculate description position
	desc_pos = 0
	for group_name in messages["command_group"]:
		for cmd_name in messages["command_group_{}".format(group_name)]:
			desc_pos = max(desc_pos, len(cmd_name))
			
	# Print command descriptions
	for group_name, group_desc in messages["command_group"].items():
		pr.print("{}:".format(group_desc))
		command_group_name = "command_group_{}".format(group_name)
		for cmd_name, cmd_desc in messages[command_group_name].items():
			pr.print("  {}  {}".format(cmd_name.ljust(desc_pos), cmd_desc))
			
#
# Command PLATFORMS
#
def command_execute_platforms(eng, arguments):

	# Parse arguments
	parser = command_parser("general", "platforms")
	parser.parse_args(arguments)
	
	pr = eng.printer(sys.stdout)
	for plat_name, plat_data in eng.platforms().items():
		pr.print("{} ({})".format(plat_name, plat_data["provider"]))
		
#
# Command LAYOUTS
#
def command_execute_layouts(eng, arguments):

	# Parse arguments
	parser = command_parser("general", "layouts")
	parser.parse_args(arguments)
	
	pr = eng.printer(sys.stdout)
	for lay_name, lay_data in eng.layouts().items():
		pr.print("{} at {}".format(lay_name, lay_data["directory"]))

#
# Command REGISTER
#
def command_execute_register(eng, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("register")
	parser.add_argument(
		"provider",
		metavar="provider",
		type=str,
		nargs=1,
		help=messages["argument"]["register.provider"]
	)
	parser.add_argument(
		"config_file",
		metavar="config_file",
		type=argparse.FileType("r"),
		nargs="*",
		help=messages["argument"]["register.config_file"]
	)
	args = parser.parse_args(arguments)
	
	try:
		config = config_collect(args.config_file)
		eng.register(args.platform_name[0], args.provider[0], config)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command DISMISS
#
def command_execute_dismiss(eng, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("dismiss")
	parser.add_argument(
		"-d",
		required=False,
		action="store_true",
		default=False,
		dest="destroy",
		help=messages["argument"]["dismiss.destroy"]
	)
	args = parser.parse_args(arguments)
		
	try:
		eng.dismiss(args.platform_name[0], args.destroy)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command STOCK
#
def command_execute_stock(eng, arguments):

	# Parse arguments
	parser = command_parser_platform("stock")
	parser.parse_args(arguments)
	
#
# Command OFFER
#
def command_execute_offer(eng, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("offer")
	parser.add_argument(
		"source_dir",
		metavar="source_dir",
		type=argparse_directory,
		nargs=1,
		help=messages["argument"]["offer.source_dir"]
	)
	parser.add_argument(
		"config_file",
		metavar="config_file",
		type=argparse.FileType("r"),
		nargs="*",
		help=messages["argument"]["offer.config_file"]
	)
	args = parser.parse_args(arguments)
	
	try:
		eng.offer(
			args.platform_name[0],
			args.source_dir[0],
			config_collect(args.config_file)
		)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command RETIRE
#
def command_execute_retire(eng, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("retire")
	parser.add_argument(
		"source_dir",
		metavar="source_dir",
		type=argparse_directory,
		nargs=1,
		help=messages["argument"]["retire.source_dir"]
	)
	args = parser.parse_args(arguments)
	
	try:
		eng.retire(args.platform_name[0], args.image_name[0])
	except BaseException as err:
		raise CommandError(err)
		
#
# Command BIND
#
def command_execute_bind(eng, arguments):

	messages = properties.load(__file__, "messages")
		
	# Parse arguments
	parser = command_parser_layout("bind")
	parser.add_argument(
		"bound_dir",
		metavar="directory",
		type=argparse_directory,
		nargs=1,
		help=messages["argument"]["bind.directory"]
	)
	parser.add_argument(
		"config_file",
		metavar="config_file",
		type=argparse.FileType("r"),
		nargs="*",
		help=messages["argument"]["bind.config_file"]
	)
	args = parser.parse_args(arguments)
	
	try:
		config = config_collect(args.config_file)
		eng.bind(args.layout_name[0], args.bound_dir[0], config)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command LEAVE
#
def command_execute_leave(eng, arguments):
	
	messages = properties.load(__file__, "messages")
	
	# Parse arguments
	parser = command_parser_layout("leave")
	parser.add_argument(
		"-d",
		required=False,
		action="store_true",
		default=False,
		dest="destroy",
		help=messages["argument"]["leave.destroy"]
	)
	args = parser.parse_args(arguments)
	
	try:
		eng.leave(args.layout_name[0], args.destroy)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command STATE
#
def command_execute_state(eng, arguments):

	# Parse arguments
	parser = command_parser_layout("state")
	parser.parse_args(arguments)
	
#
# Command REFRESH
#
def command_execute_refresh(eng, arguments):

	# Parse arguments
	parser = command_parser_layout("refresh")
	parser.parse_args(arguments)
	
#
# Create parser for command
#
def command_parser(group_name, name):

	messages = properties.load(__file__, "messages")
	
	return argparse.ArgumentParser(
		prog="{} {}".format(application_name, name),
		description=messages["command_group_{}".format(group_name)][name]
	)

#
# Create parser for platform command
#
def command_parser_platform(name):

	messages = properties.load(__file__, "messages")
	
	parser = command_parser("platform", name)
	parser.add_argument(
		"platform_name",
		metavar="platform",
		type=str,
		nargs=1,
		help=messages["argument"]["platform"]
	)
	return parser
	
#
# Create parser for layout command
#
def command_parser_layout(name):

	messages = properties.load(__file__, "messages")
	
	def argparse_layout_name(layout_name):
		return layout_name
		
	parser = command_parser("layout", name)
	parser.add_argument(
		"layout_name",
		metavar="layout",
		type=argparse_layout_name,
		nargs=1,
		help=messages["argument"]["layout"]
	)
	return parser
	
#
# Collect configuration from files
#
def config_collect(args_config_file):

	config = {}
	for config_file in args_config_file:
		util.merge_dict(config, json.loads(config_file.read()))
	return config

