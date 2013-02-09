# SuperGenPass GTK User Interface
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

import os.path
import hashlib
from gi.repository import Gtk, Gdk, GLib
from . import *


class GtkUI:

    """Gtk User Interface for SuperGenPass."""

    def __init__(self, args):
        """Initialize the GUI.

        Arguments:
        args -- arguments given on the command line

        """
        # load custom style
        css = Gtk.CssProvider()
        css.load_from_path(os.path.join(data_dir, 'style.css'))
        screen = Gdk.Screen.get_default()
        ctx = Gtk.StyleContext()
        ctx.add_provider_for_screen(screen, css,
                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        # load ui file
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(data_dir, 'main.ui'))
        # initialize members
        self.password = ''
        self.window = builder.get_object('main')
        self.f_domain = builder.get_object('domain')
        self.f_master = builder.get_object('master')
        self.f_confirm = builder.get_object('confirm')
        self.f_method = builder.get_object('method')
        self.f_password = builder.get_object('password')
        self.f_show_password = builder.get_object('show_password')
        self.f_pin = builder.get_object('pin')
        self.f_length = builder.get_object('length')
        self.f_pinlength = builder.get_object('pinlength')
        self.f_algorithm = builder.get_object('algorithm')
        self.f_salt = builder.get_object('salt')
        self.f_apply = builder.get_object('apply')
        # setup options
        self.method = 1 if args.pin else 0
        self.f_method.set_current_page(self.method)
        self.f_length.set_value(args.length)
        self.f_pinlength.set_value(args.pinlength)
        index = 0
        for a in hashlib.algorithms_available:
            if a.islower() or a.lower() not in hashlib.algorithms_available:
                self.f_algorithm.append_text(a)
                if a in (args.algorithm, args.algorithm.lower()):
                    self.f_algorithm.set_active(index)
                index += 1
        self.f_salt.set_text(args.salt, -1)
        # try to get domain from clipboard
        domain = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).wait_for_text()
        if domain:
            domain = strip_domain(domain)
        if not domain:
            domain = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()
            if domain:
                domain = strip_domain(domain)
        if domain:
            self.f_domain.set_text(domain)
            self.f_master.grab_focus()
        else:
            self.f_domain.grab_focus()
        # connect signals
        builder.connect_signals(self)

    def run(self):
        '''Launch the GUI.'''
        self.window.show_all()
        Gtk.main()

    def update_password(self):
        if self.method == 0:  # Password
            if self.f_show_password.get_active():
                self.f_password.set_label(self.password)
            else:
                self.f_password.set_label("•" * int(self.f_length.get_value())
                                          if self.password else "")
        else:  # PIN
            self.f_pin.set_label(self.password)
        self.f_apply.set_sensitive(bool(self.password))

    def on_cancel(self, *args):
        Gtk.main_quit()

    def on_method_changed(self, notebook, page, page_num):
        self.method = page_num
        self.on_changed()

    def on_changed(self, *args):
        domain = self.f_domain.get_text()
        master = self.f_master.get_text()
        confirm = self.f_confirm.get_text()
        if not confirm:
            confirm = master
        ctx = self.f_confirm.get_style_context()
        if master != confirm:
            ctx.add_class('invalid')
        else:
            ctx.remove_class('invalid')
        if domain and master and master == confirm:
            master = master + self.f_salt.get_text()
            if self.method == 0:  # Password
                self.password = generate(master, domain,
                                         int(self.f_length.get_value()),
                                         self.f_algorithm.get_active_text())
            else:  # PIN
                self.password = generate_pin(master, domain,
                                             int(self.f_pinlength.get_value()))
        else:
            self.password = ""
        self.update_password()

    def on_show_password_toggled(self, checkbox):
        self.update_password()

    def on_options_toggled(self, *args):
        self.window.resize(self.window.get_size()[0], 1)

    def on_apply(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.password, len(self.password))
        clipboard.store()
        GLib.timeout_add_seconds(120, self.on_timeout)
        self.window.hide()

    def on_timeout(self):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        if clipboard.wait_for_text() == self.password:
            clipboard.set_text("", 0)
            clipboard.store()
        Gtk.main_quit()
        return False
