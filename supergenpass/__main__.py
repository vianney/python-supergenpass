# SuperGenPass executable
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

import os
import os.path
import sys
import argparse
import configparser
import getpass
import hashlib
from . import *


# Load default options
config_filename = __package__ + ".ini"
config_system = os.path.join('/etc', config_filename)
if 'XDG_CONFIG_HOME' in os.environ and os.environ['XDG_CONFIG_HOME']:
    config_user = os.path.join(os.environ['XDG_CONFIG_HOME'], config_filename)
else:
    config_user = os.path.expanduser(os.path.join('~', '.config',
                                                  config_filename))

config = configparser.ConfigParser()
config.read_dict({__package__: {'length': '10',
                                'pinlength': 4,
                                'algorithm': 'md5',
                                'salt': ''}})
config.read([config_system, config_user])
config = config[__package__]


# Parse arguments
def type_length(arg):
    arg = int(arg)
    if arg < 4:
        raise argparse.ArgumentTypeError("length must be at least 4")
    return arg


def type_pinlength(arg):
    arg = int(arg)
    if arg < 3 or arg > 8:
        raise argparse.ArgumentTypeError("PIN length must be between 3 and 8")
    return arg


def type_algorithm(arg):
    if arg not in hashlib.algorithms_available:
        raise argparse.ArgumentTypeError("hash algorithm {} is not available"
                                         .format(arg))
    return arg


parser = argparse.ArgumentParser()
parser.description = "Derive a SuperGenPass password from a master password " \
                     "and a domain name."
parser.add_argument("domain", nargs='?', help="domain name")
parser.add_argument("-p", "--pin", action='store_true',
                    help="generate a PIN instead of a password")
group = parser.add_mutually_exclusive_group()
group.add_argument("-n", "--nostrip", action='store_false', dest='strip',
                   help="use domain name as is without stripping")
group.add_argument("-g", "--graphical", action='store_true',
                   help="launch graphical user interface")
group = parser.add_argument_group("generator options")
group.description = "These options define how the password will be " \
                    "generated. The default options may be set in " + \
                    config_user + " or " + config_system + ". Options are " \
                    "set under the [" + __package__ + "] section, keys are " \
                    "the long arguments names."
group.add_argument("-l", "--length", type=type_length,
                   default=int(config['length']),
                   help="length of the generated password (default: "
                        "%(default)s)")
group.add_argument("-L", "--pinlength", type=type_pinlength,
                   default=int(config['pinlength']),
                   help="length of the generated PIN (default: %(default)s)")
group.add_argument("-a", "--algorithm", type=type_algorithm,
                   default=config['algorithm'],
                   help="hash algorithm (default: %(default)s)")
group.add_argument("-s", "--salt", default=config['salt'],
                   help="salt to append to the master password")
args = parser.parse_args()


# Do real work
if args.graphical:
    from . import gtkui
    gtkui.GtkUI(args).run()
else:
    try:
        if args.domain:
            domain = args.domain
        else:
            domain = input("Domain name: ")
        if args.strip:
            domain = strip_domain(domain)
        if not domain:
            if args.domain:
                parser.error("invalid domain name")
            else:
                print("Invalid domain name", file=sys.stderr)
                sys.exit(1)
        master = getpass.getpass("Master password: ") + args.salt
        if args.pin:
            print(generate_pin(master, domain, args.pinlength))
        else:
            print(generate(master, domain, args.length, args.algorithm))
    except KeyboardInterrupt:
        print()
