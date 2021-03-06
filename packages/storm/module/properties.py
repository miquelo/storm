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

import os.path
import configparser

last = configparser.ConfigParser()

def load(basedir, name):

	moduledir = os.path.abspath(basedir)
	propsfilename = "{}.ini".format(name)
	last.read(os.path.join(os.path.dirname(moduledir), propsfilename))
	return last
