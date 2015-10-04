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
from storm.module import resource
from storm.module import util

import json
import argparse
import os
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
# Resource argument parsing
#		
def argparse_resource(uri):

	messages = properties.load(__file__, "messages")
	
	try:
		return resource.ref(uri)
	except:
		msg = messages["error"]["invalid_resource_id"].format(uri)
		raise argparse.ArgumentTypeError(msg)
	
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
		
	# Execute command
	eng = engine.Engine(data_res.ref("engine.json"))
	
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
		pr.append(err_msg, "red", "bright")
		pr.print()
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
		pr.append("{}:".format(group_desc))
		command_group_name = "command_group_{}".format(group_name)
		for cmd_name, cmd_desc in messages[command_group_name].items():
			pr.append("\n  {}  {}".format(cmd_name.ljust(desc_pos), cmd_desc))
		pr.print()
		
#
# Command PLATFORMS
#
def command_execute_platforms(eng, arguments):

	# Parse arguments
	parser = command_parser("general", "platforms")
	parser.parse_args(arguments)
	
	pr = eng.printer(sys.stdout)
	for plat_name, plat_data in eng.platforms().items():
		pr.append("{} ({})".format(plat_name, plat_data["provider"]))
	pr.print()
		
#
# Command LAYOUTS
#
def command_execute_layouts(eng, arguments):

	# Parse arguments
	parser = command_parser("general", "layouts")
	parser.parse_args(arguments)
	
	pr = eng.printer(sys.stdout)
	for lay_name, lay_data in eng.layouts().items():
		pr.append("{} at {}".format(lay_name, lay_data["resource"]))
	pr.print()

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
		"props_res",
		metavar="props_res",
		type=argparse_resource,
		nargs="*",
		help=messages["argument"]["register.props_res"]
	)
	args = parser.parse_args(arguments)
	
	try:
		props = props_collect(args.props_res)
		eng.register(args.platform_name[0], args.provider[0], props)
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
		"image_res",
		metavar="image_res",
		type=argparse_resource,
		nargs=1,
		help=messages["argument"]["offer.image_res"]
	)
	parser.add_argument(
		"props_res",
		metavar="props_res",
		type=argparse_resource,
		nargs="*",
		help=messages["argument"]["offer.props_res"]
	)
	args = parser.parse_args(arguments)
	
	try:
		eng.offer(
			args.platform_name[0],
			args.image_res[0],
			props_collect(args.props_res)
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
		"image_res",
		metavar="image_res",
		type=argparse_resource,
		nargs=1,
		help=messages["argument"]["retire.image_res"]
	)
	args = parser.parse_args(arguments)
	
	try:
		eng.retire(args.platform_name[0], args.image_res[0])
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
		"layout_res",
		metavar="layout_res",
		type=argparse_resource,
		nargs=1,
		help=messages["argument"]["bind.layout_res"]
	)
	parser.add_argument(
		"props_res",
		metavar="props_res",
		type=argparse_resource,
		nargs="*",
		help=messages["argument"]["bind.props_res"]
	)
	args = parser.parse_args(arguments)
	
	try:
		props = props_collect(args.props_res)
		eng.bind(args.layout_name[0], args.layout_res[0], props)
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
# Collect properties from files
#
def props_collect(args_props_res):

	props = {}
	for props_res in args_props_res:
		props_file = props_res.open("r")
		util.merge_dict(props, json.loads(props_file.read()))
		props_file.close()
	return props

