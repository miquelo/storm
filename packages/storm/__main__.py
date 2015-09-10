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

from storm import application
from storm import properties
from storm import util

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
# Main function
#
def main():

	# Look for data directory
	if sys.platform == "darwin":
		from AppKit import NSSearchPathForDirectoriesInDomains
		ddp = NSSearchPathForDirectoriesInDomains(14, 1, True)
		datadir = os.path.join(ddp[0], application_name)
	elif sys.platform == "win32":
		appdatadir = os.environ['APPDATA']
		datadir = os.path.join(appdatadir, application_name)
	else:
		homedir = os.environ["HOME"]
		datadir = os.path.join(homedir, ".{}".format(application_name))
		
	if not os.path.exists(datadir):
		os.mkdir(datadir)
		
	# Execute command
	app = application.Application(datadir)
	
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
			app.printer_level = 1
		else:
			app.printer_level = 0
			
		# Execute the command
		args.command[0](app, args.arguments)
		return 0
		
	except CommandError as err:
	
		# Print error output
		pr = app.printer(sys.stderr)
		err_msg = "{}".format(err)
		if args.exceptions:
			err_msg = "{}:\n{}".format(err_msg, traceback.format_exc())
		pr.print(err_msg, 0, "red", "bright")
		return 1
		
	finally:
	
		# Store application configuration
		app.store()
		
#
# Command COMMANDS
#
def command_execute_commands(app, arguments):

	messages = properties.load(__file__, "messages")
	pr = app.printer(sys.stdout)
	
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
def command_execute_platforms(app, arguments):

	# Parse arguments
	parser = command_parser("general", "platforms")
	parser.parse_args(arguments)
	
	pr = app.printer(sys.stdout)
	for plat_name, plat_def in app.platforms().items():
		pr.print("{} ({})".format(plat_name, plat_def["provider"]))
		
#
# Command DOMAINS
#
def command_execute_domains(app, arguments):

	# Parse arguments
	parser = command_parser("general", "domains")
	parser.parse_args(arguments)

#
# Command REGISTER
#
def command_execute_register(app, arguments):

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
		app.register(args.platform_name[0], args.provider[0], config)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command DISMISS
#
def command_execute_dismiss(app, arguments):

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
		app.dismiss(args.platform_name[0], args.destroy)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command STOCK
#
def command_execute_stock(app, arguments):

	# Parse arguments
	parser = command_parser_platform("stock")
	parser.parse_args(arguments)
	
#
# Command BIND
#
def command_execute_bind(app, arguments):
	
	# Parse arguments
	parser = command_parser_domain("bind")
	parser.parse_args(arguments)
	
#
# Command LEAVE
#
def command_execute_leave(app, arguments):
	
	# Parse arguments
	parser = command_parser_domain("leave")
	parser.parse_args(arguments)
	
#
# Command STATE
#
def command_execute_state(app, arguments):

	# Parse arguments
	parser = command_parser_domain("state")
	parser.parse_args(arguments)
	
#
# Command REFRESH
#
def command_execute_refresh(app, arguments):

	# Parse arguments
	parser = command_parser_domain("refresh")
	parser.parse_args(arguments)
	
#
# Command OFFER
#
def command_execute_offer(app, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("offer")
	parser.add_argument(
		"image_name",
		metavar="image_name",
		type=str,
		nargs=1,
		help=messages["argument"]["offer.image_name"]
	)
	parser.add_argument(
		"source_dir",
		metavar="source_dir",
		type=str,
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
		app.offer(
			args.platform_name[0],
			args.image_name[0],
			args.source_dir[0],
			config_collect(args.config_file)
		)
	except BaseException as err:
		raise CommandError(err)
		
#
# Command RETIRE
#
def command_execute_retire(app, arguments):

	messages = properties.load(__file__, "messages")

	# Parse arguments
	parser = command_parser_platform("retire")
	parser.add_argument(
		"image_name",
		metavar="image_name",
		type=str,
		nargs=1,
		help=messages["argument"]["retire.image_name"]
	)
	args = parser.parse_args(arguments)
	
	try:
		app.retire(args.platform_name[0], args.image_name[0])
	except BaseException as err:
		raise CommandError(err)
	
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
# Create parser for domain command
#
def command_parser_domain(name):

	messages = properties.load(__file__, "messages")
	
	def argparse_domain_name(domain_name):
		return domain_name
		
	parser = command_parser("domain", name)
	parser.add_argument(
		"domain_name",
		metavar="domain",
		type=argparse_domain_name,
		nargs=1,
		help=messages["argument"]["domain"]
	)
	return parser
	
#
# Collect configuration from files
#
def config_collect(args_config_file):

	config = {}
	for config_file in args_config_file:
		util.merge_dict(config, json.dumps( open(config_file, "r").read()))
	return config

