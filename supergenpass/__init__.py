# SuperGenPass module
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

# Some code/inspiration is taken from the following GPLv3+ projects:
# - SuperGenPass password generator
#   Copyright (c) 2009 Michael Gorven
#   http://michael.gorven.za.net/blog/2009/06/18/supergenpass-cellphones-command-line
# - Android SuperGenPass utility
#   Copyright (C) 2010 Steve Pomeroy
#   http://staticfree.info/projects/sgp/

import os.path
import re
import itertools
import json
import base64
import hashlib
import hmac
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


def hotp(key, counter, length=6):
    """Generate an HMAC-based One-Time Password (HOTP), following RFC 4226.

    Arguments:
    key -- the key (bytes object)
    counter -- the moving part (bytes object)
    length -- number of digits in the output

    """
    # Step 1: HMAC-SHA-1
    hs = hmac.new(key, counter, digestmod=hashlib.sha1).digest()
    # Step 2: Dynamic Truncation
    assert len(hs) == 20
    offset = hs[19] & 0xf
    p = int.from_bytes(hs[offset:offset+4], byteorder='big')
    snum = p & 0x7fffffff
    # Step 3: output
    d = snum % (10 ** length)
    return ("{:0" + str(length) + "d}").format(d)


# Set of blacklisted PINs from Android app
_pin_blacklist = {"90210",
                  "8675309",  # Jenny
                  "1004",  # 10-4
                  # in this document, these were shown to be the least
                  # commonly used. Now they won't be used at all.
                  # http://www.datagenetics.com/blog/september32012/index.html
                  "8068", "8093", "9629", "6835", "7637", "0738", "8398",
                  "6793", "9480", "8957", "0859", "7394", "6827", "6093",
                  "7063", "8196", "9539", "0439", "8438", "9047", "8557"}


# from itertools recipes
def _pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


# from itertools recipes
def _grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def _bad_pin(pin):
    """Return True if pin is a bad PIN."""
    # Special case for 4-digits PINs (which are quite common)
    if len(pin) == 4:
        # 19xx pins look like years, so might as well ditch them.
        if pin[:2] == "19" or (pin[:2] == "20" and int(pin[2:]) < 30):
            return True
        # 1515
        if pin[:2] == pin[2:]:
            return True
    # Find case where all digits are in pairs (e.g., 1122, 3300447722)
    if len(pin) % 2 == 0:
        for a, b in _grouper(2, pin):
            if a != b:
                break
        else:
            return True
    # Avoid a numerical run (e.g., 123456, 0000, 9876, 2468)
    diff = None
    for a, b in _pairwise(int(c) for c in pin):
        if diff is not None and diff != b - a:
            break
        diff = b - a
    else:
        return True
    # Avoid partial numerical run (e.g., 3000, 5553)
    consecutive = 0
    for a, b in _pairwise(pin):
        if a == b:
            consecutive += 1
        else:
            consecutive = 0
        if consecutive >= 2:
            return True
    # Filter ou special numbers
    return pin in _pin_blacklist


def generate_pin(master, domain, length=4):
    """Derive a Personal Identification Number (PIN) from a master password and
    a domain name.

    The domain name will be used as is. Use strip_domain to preprocess a URL.

    Arguments:
    master -- the master password
    domain -- the domain name
    length -- length of the desired PIN

    """
    master = master.encode('utf-8')
    domain = domain.encode('utf-8')
    pin = hotp(master, domain, length)
    run = 0
    while _bad_pin(pin) and run < 100:
        suffix = " " + str(run)
        pin = hotp(master, domain + suffix.encode('utf-8'), length)
        run += 1
    return pin


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
