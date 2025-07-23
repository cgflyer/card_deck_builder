#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   GIMP - The GNU Image Manipulation Program
#   Copyright (C) 1995 Spencer Kimball and Peter Mattis
#
#   gimp-tutorial-plug-in.py
#   sample plug-in to illustrate the Python plug-in writing tutorial
#   Copyright (C) 2023 Jacob Boerema
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi

from gi.repository import GLib

class MyFirstPlugin (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ "jb-plug-in-first-try" ]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")

        procedure.set_menu_label("My first Python plug-in")
        procedure.add_menu_path('<Image>/Filters/Tutorial/')

        procedure.set_documentation("My first Python plug-in tryout",
                                    "My first Python 3 plug-in for GIMP 3.0",
                                    name)
        procedure.set_attribution("Your name", "Your name", "2023")

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, run_data):
        Gimp.message("Hello world!")
        # do what you want to do, then, in case of success, return:
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(MyFirstPlugin.__gtype__, sys.argv)
