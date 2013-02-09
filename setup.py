#!/usr/bin/env python3
# SuperGenPass setup script
# Copyright (C) 2012-2013  Vianney le Clément de Saint-Marcq <vleclement@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name="supergenpass",
      version="0.1",
      description="SuperGenPass Python module and GTK interface",
      author="Vianney le Clément de Saint-Marcq",
      author_email="vleclement@gmail.com",
      url="https://bitbucket.org/vianney/supergenpass",
      license="GPLv3+",
      packages=['supergenpass'],
      package_data={'supergenpass': ['data/*']},
      scripts=['scripts/supergenpass'],
      data_files=[('share/pixmaps', ['data/supergenpass.png']),
                  ('share/applications', ['data/supergenpass.desktop'])],
     )
