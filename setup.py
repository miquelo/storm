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

setup(
	name="storm",
	version="0.1.0",
	
	author="STORM Team",
	author_email="miquel.ferran.gonzalez@gmail.com",
	
	packages=find_packages("packages"),
	namespace_packages=[
		"storm"
	],
	package_dir={
		"": "packages"
	},
	test_suite="testsuite.storm",
	
	url="http://pypi.python.org/pypi/storm_0.1.0/",
	
	license="LICENSE.txt",
	description="Management tool for containerized ecosystems.",
	long_description=open("README.md").read()
)

