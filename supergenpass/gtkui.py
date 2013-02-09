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

import math
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
        self.masterhash = None
        self.shapes = []
        self.window = builder.get_object('main')
        self.f_domain = builder.get_object('domain')
        self.f_master = builder.get_object('master')
        self.f_confirm = builder.get_object('confirm')
        self.f_visualhash = builder.get_object('visualhash')
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
        # Compute visual hash
        if master:
            masterhash = hashlib.sha1(master.encode()).digest()
        else:
            masterhash = None
        if masterhash != self.masterhash:
            self.masterhash = masterhash
            self.f_visualhash.queue_draw()
        # Check confirmed password
        if not confirm:
            confirm = master
        ctx = self.f_confirm.get_style_context()
        if master != confirm:
            ctx.add_class('invalid')
        else:
            ctx.remove_class('invalid')
        # Generate password
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

    def on_draw_visualhash(self, widget, cr):
        if not self.masterhash:
            return False

        radius = 8  # radius of the shapes defined below
        spacing = 2  # spacing between shapes
        shapewidth = radius * 2 + spacing  # width of a shape
        nwidth = 4  # width of canvas in shapes

        # Generate shapes based on radius 8
        if not self.shapes:
            # Circle
            cr.arc(0, 0, radius, 0, 2 * math.pi)
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Square
            cr.rectangle(-radius, -radius, radius, radius)
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Star
            cr.move_to(0, -8.475681)
            cr.line_to(1.893601, -2.597389)
            cr.line_to(8.069343, -2.612960)
            cr.line_to(3.063910, 1.004453)
            cr.line_to(4.987128, 6.873122)
            cr.line_to(0, 3.230514)
            cr.line_to(-4.987129, 6.873122)
            cr.rel_line_to(1.923218, -5.868669)
            cr.rel_line_to(-5.005433, -3.617414)
            cr.rel_line_to(6.175743, 0.015571)
            cr.close_path()
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Triangle
            cr.move_to(-radius, radius)
            cr.line_to(radius, radius)
            cr.line_to(0, -radius)
            cr.close_path()
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Plus
            cr.move_to(2.084458, -2.117061)
            cr.rel_line_to(5.865234, 0)
            cr.rel_line_to(0, 4.296875)
            cr.rel_line_to(-5.865234, 0)
            cr.rel_line_to(0, 5.865234)
            cr.rel_line_to(-4.296875, 0)
            cr.rel_line_to(0, -5.865234)
            cr.rel_line_to(-5.865234, 0)
            cr.rel_line_to(0, -4.296875)
            cr.rel_line_to(5.865234, 0)
            cr.rel_line_to(0, -5.875977)
            cr.rel_line_to(4.296875, 0)
            cr.close_path()
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # X
            cr.move_to(3.723963, 0.060475)
            cr.line_to(8.083338, 4.419850)
            cr.line_to(4.438807, 8.064382)
            cr.line_to(0.079432, 3.705007)
            cr.line_to(-4.279943, 8.064382)
            cr.line_to(-7.924475, 4.419850)
            cr.rel_line_to(4.359375, -4.359375)
            cr.rel_line_to(-4.359375, -4.359375)
            cr.rel_line_to(3.644531, -3.644531)
            cr.rel_line_to(4.359375, 4.359375)
            cr.rel_line_to(4.359375, -4.371094)
            cr.rel_line_to(3.644531, 3.644531)
            cr.close_path()
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Diamond
            cr.move_to(0, -radius)
            cr.line_to(radius, 0)
            cr.line_to(0, radius)
            cr.line_to(-radius, 0)
            cr.close_path()
            self.shapes.append(cr.copy_path())
            cr.new_path()
            # Small circle
            cr.arc(0, 0, radius/2, 0, 2 * math.pi)
            self.shapes.append(cr.copy_path())
            cr.new_path()

        # Setup cairo context
        scale = min(widget.get_allocated_width() / (nwidth * shapewidth),
                    widget.get_allocated_height() / (nwidth * shapewidth))
        cr.scale(scale, scale)
        cr.translate(shapewidth / 2, shapewidth / 2)

        # Draw the hash
        it = iter(self.masterhash)
        for dat1, dat2 in zip(it, it):
            dat = dat1 | dat2 << 8
            symbol = dat & 0x7
            x = (dat >> 3 & 0x7) / 7 * (nwidth - 1) * shapewidth
            y = (dat >> 6 & 0x7) / 7 * (nwidth - 1) * shapewidth
            r = (dat >> 9 & 0x3) / 3
            g = (dat >> 11 & 0x3) / 3
            b = (dat >> 13 & 0x3) / 3
            cr.set_source_rgb(r, g, b)
            cr.save()
            cr.translate(x, y)
            cr.append_path(self.shapes[symbol])
            cr.fill()
            cr.restore()
        return False
