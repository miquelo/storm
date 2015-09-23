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

from setuptools import setup, find_packages

import configparser
import os.path

def message_get(name):

	path = "packages/storm/application"
	props = configparser.ConfigParser()
	moduledir = os.path.abspath(__file__)
	propsdir = os.path.join(os.path.dirname(moduledir), path)
	props.read(os.path.join(propsdir, "messages.ini"))
	return props["application"][name]

setup(
	name="storm",
	version="0.1.0",
	
	author="STORM Team",
	author_email="miquel.ferran.gonzalez@gmail.com",
	
	packages=find_packages("packages", "testsuite"),
	namespace_packages=[
		"storm",
		"storm.provider",
		"storm.provider.resource"
	],
	package_dir={
		"": "packages",
		"": "testsuite"
	},
	extras_require={
		"color": [
			"colorama>=0.3.3"
		]
	},
	test_suite="storm",
	
	entry_points={
		"console_scripts": [
			"storm=storm.application.command:main"
		]
	},
	url="http://pypi.python.org/pypi/storm_0.1.0/",
	
	license="LICENSE.txt",
	description=message_get("description"),
	long_description=open("README.md").read()
)

