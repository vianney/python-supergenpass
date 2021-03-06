==============================================
 SuperGenPass Python module and GTK interface
==============================================

This project is a Python 3.x implementation of the SuperGenPass_ bookmarklet,
designed to be compatible with the `Android SuperGenPass utility`_.
It provides a module to be used in other programs, a command-line interface and
a GTK 3 interface.

Compared with the original SuperGenPass_ bookmarklet, it has a number of
additional features:

* customizable hashing algorithm and password length,
* optional salt appended to the master password,
* PIN generation based on HOTP.

.. _SuperGenPass: http://www.supergenpass.com/
.. _Android SuperGenPass utility: http://staticfree.info/projects/sgp/


Installation
=============

Setup is handled by ``distutils``. To install the module and interface, do::

    python setup.py install

The module and the CLI do not require any extra module. The GTK interface
requires GTK+ 3 and PyGObject_.

.. _PyGObject: https://live.gnome.org/PyGObject


Usage
======

As a Python module
-------------------

The module is named ``supergenpass``. The three main methods are:

* ``generate(master, domain)``: derive a SuperGenPass password,
* ``generate_pin(master, domain)``: generate a PIN,
* ``strip_domain(domain)``: strip a domain name/URL to its base domain name.

Use Python's ``help`` function for more information.


As a standalone program
------------------------

You can launch the CLI using ``supergenpass`` in your shell. Use with ``-h``
to get the full list of accepted arguments.

To launch the GTK interface, use ``supergenpass -g``. The domain textbox will
be populated with the clipboard's content if a URL or domain name is
recognized. The derived password will be copied to the clipboard when clicking
on the OK button. If the password is still in the clipboard after 2 minutes,
it will be cleared.

The default options may be altered in ``~/.config/supergenpass.ini`` (for
user-specific configuration) or ``/etc/supergenpass.ini`` (for system-wide
configuration). See ``supergenpass -h`` for more information.


Author, license and acknowledgements
=====================================

Copyright (C) 2012-2013  Vianney le Clément de Saint-Marcq <vleclement AT gmail · com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Some code/inspiration is taken from the following GPLv3+ projects:

* | SuperGenPass password generator
  | Copyright (c) 2009 Michael Gorven
  | http://michael.gorven.za.net/blog/2009/06/18/supergenpass-cellphones-command-line
* | Android SuperGenPass utility
  | Copyright (C) 2010 Steve Pomeroy
  | http://staticfree.info/projects/sgp/

SuperGenPass icon, (C) 2010 by Steve Pomeroy, used under a `Creative Commons
Attribution-ShareAlike license`_

.. _Creative Commons Attribution-ShareAlike license:
    http://creativecommons.org/licenses/by-sa/3.0/
