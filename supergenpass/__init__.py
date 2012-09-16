# SuperGenPass module
# Copyright (C) 2012  Vianney le Clément <vleclement@gmail.com>
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

# Some code/inspiration is taken from the following GPLv3+ projects:
# - SuperGenPass password generator
#   Copyright (c) 2009 Michael Gorven
#   http://michael.gorven.za.net/blog/2009/06/18/supergenpass-cellphones-command-line
# - Android SuperGenPass utility
#   Copyright (C) 2010 Steve Pomeroy
#   http://staticfree.info/projects/sgp/

import os.path
import re
import json
import base64
import hashlib
import urllib.parse


# Directory with data files
data_dir = os.path.join(os.path.dirname(__file__), 'data')


# Rules for a valid password
# (from http://supergenpass.com/about/#PasswordComplexity):
# * Consist of alphanumerics (A-Z, a-z, 0-9)
# * Always start with a lowercase letter of the alphabet
# * Always contain at least one uppercase letter of the alphabet
# * Always contain at least one numeral
# * Can be any length from 4 to 24 characters (default: 10)
_valid_pass = \
    re.compile(r"""^[a-z]                          # start with lowercase
                   [a-zA-Z0-9]*                    # stuff
                   (?:(?:[A-Z][a-zA-Z0-9]*[0-9])|  # uppercase stuff number OR
                   (?:[0-9][a-zA-Z0-9]*[A-Z]))     # number stuff uppercase
                   [a-zA-Z0-9]*$""",               # stuff
               re.VERBOSE)


def generate(master, domain, length=10, algorithm='md5'):
    """Derive a SuperGenPass password from a master password and a domain name.

    The domain name will be used as is. Use strip_domain to preprocess a URL.

    Arguments:
    master -- the master password
    domain -- the domain name
    length -- length of the desired password
    algorithm -- hash algorithm to use

    """
    password = master + ":" + domain
    count = 0
    while count < 10 or not _valid_pass.match(password[:length]):
        password = hashlib.new(algorithm, password.encode('utf-8')).digest()
        password = base64.b64encode(password, b'98').decode('ascii')
        password = password.replace('=', 'A')
        count += 1
    return password[:length]


# Set of TLDs from SuperGenPass script
with open(os.path.join(data_dir, 'tldlist.json')) as f:
    _toplevel_domains = set(json.load(f))


# Matcher for an IPv4 address
_ip_address = re.compile(r"^[0-9]{1,3}(?:\.[0-9]{1,3}){3}$")


def strip_domain(domain):
    """Strip a domain name/url to its base domain name. Return the stripped
    domain name or None if not a domain name or url."""
    domain = domain.lower()
    if '/' in domain or ':' in domain:
        domain = urllib.parse.urlparse(domain).netloc
    if _ip_address.match(domain):
        return domain
    parts = domain.split('.')
    if len(parts) < 2:
        return None
    elif len(parts) >= 3 and '.'.join(parts[-2:]) in _toplevel_domains:
        return '.'.join(parts[-3:])
    else:
        return '.'.join(parts[-2:])
