#
# addtorrentdialog.py
#
# Copyright (C) 2007 Andrew Resch <andrewresch@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#
#


import pygtk
pygtk.require('2.0')
import gtk, gtk.glade
import gettext
import gobject
import base64
import os

import pkg_resources
import listview
from TorrentParser import TorrentInfo

AddTorrentWindow = None

class AddTorrentDialog():
    def __init__(self):
    	print "AddTorrent"
        self.glade = gtk.glade.XML("add_torrent_dialog.glade")
        self.dialog = self.glade.get_widget("dialog_add_torrent")
        self.dialog.connect("delete-event", self._on_delete_event)   
        self.glade.signal_autoconnect({
            "on_button_file_clicked": self._on_button_file_clicked,
            "on_button_cancel_clicked": self._on_button_cancel_clicked,
            "on_button_add_clicked": self._on_button_add_clicked,
        })
        self.torrent_liststore = gtk.ListStore(str, str, str)
        #download?, path, filesize, sequence number, inconsistent?
        self.files_treestore = gtk.TreeStore(bool, str, gobject.TYPE_UINT64,
                                        gobject.TYPE_INT64, bool, str)
        self.files_treestore.set_sort_column_id(1, gtk.SORT_ASCENDING)

        # Holds the files info
        self.files = {}
        self.infos = {}
        self.core_config = {}
        self.options = {}

        self.previous_selected_torrent = None


        self.listview_torrents = self.glade.get_widget("listview_torrents")
        self.listview_files = self.glade.get_widget("listview_files")

        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Torrent", render, text=1)
        self.listview_torrents.append_column(column)

        render = gtk.CellRendererToggle()
        render.connect("toggled", self._on_file_toggled)
        column = gtk.TreeViewColumn(None, render, active=0, inconsistent=4)
        self.listview_files.append_column(column)

        column = gtk.TreeViewColumn("Filename")
        render = gtk.CellRendererPixbuf()
        column.pack_start(render, False)
        column.add_attribute(render, "stock-id", 5)
        render = gtk.CellRendererText()
        render.set_property("editable", True)
       # render.connect("edited", self._on_filename_edited)
        column.pack_start(render, True)
        column.add_attribute(render, "text", 1)
        column.set_expand(True)
        self.listview_files.append_column(column)

        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Size")
        column.pack_start(render)
        column.set_cell_data_func(render, listview.cell_data_size, 2)
        self.listview_files.append_column(column)

        self.listview_torrents.set_model(self.torrent_liststore)
        self.listview_files.set_model(self.files_treestore)

        self.listview_files.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.listview_torrents.get_selection().connect("changed", self._on_torrent_changed)

        # Get default config values from the core

        self.core_config = {}
        self.dialog.show()

    def add_from_files(self, filenames):
        import os.path
        new_row = None

        for filename in filenames:
            # Convert the path to unicode
            filename = unicode(filename)

            # Get the torrent data from the torrent file
            
            try:
            	info = TorrentInfo(filename)
            except:
            	MainWindow.printError("Not a valid torrent")
            	return
            if info.info_hash in self.files:
            	print "duplicate torrent?"
                #log.debug("Trying to add a duplicate torrent!")
                #dialogs.ErrorDialog(_("Duplicate Torrent"), _("You cannot add the same torrent twice."), self.dialog).run()
                continue

            name = "%s (%s)" % (info.name, os.path.split(filename)[-1])
            new_row = self.torrent_liststore.append(
                [info.info_hash, info.name, filename])
            self.files[info.info_hash] = info.files
            self.infos[info.info_hash] = info.filedata
            self.listview_torrents.get_selection().select_iter(new_row)

            #self.set_default_options()
            #self.save_torrent_options(new_row)

        (model, row) = self.listview_torrents.get_selection().get_selected()
        if not row and new_row:
            self.listview_torrents.get_selection().select_iter(new_row)


    def _on_delete_event(self,widget=None,other=None):
    	global AddTorrentWindow
    	AddTorrentWindow = None
    	print "deleted"
    	
    def _on_button_file_clicked(self,widget):
        # Setup the filechooserdialog
        chooser = gtk.FileChooserDialog(("Choose a .torrent file"), None,  gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        chooser.set_transient_for(self.dialog)
        chooser.set_select_multiple(True)
        chooser.set_property("skip-taskbar-hint", True)

        # Add .torrent and * file filters
        file_filter = gtk.FileFilter()
        file_filter.set_name(("Torrent files"))
        file_filter.add_pattern("*." + "torrent")
        chooser.add_filter(file_filter)
        file_filter = gtk.FileFilter()
        file_filter.set_name(("All files"))
        file_filter.add_pattern("*")
        chooser.add_filter(file_filter)
        
        self.config = {"default_load_path":None}
        if self.config["default_load_path"] is not None:
        	chooser.set_current_folder(self.config["default_load_path"])

        # Run the dialog
        response = chooser.run()

        if response == gtk.RESPONSE_OK:
            result = chooser.get_filenames()
            self.config["default_load_path"] = chooser.get_current_folder()
        else:
            chooser.destroy()
            return
        chooser.destroy()
        self.add_from_files(result)
        
    def _on_button_add_clicked(self,widget):
    	print "add"
    	self.save_torrent_options()
    	(model, row) = self.listview_torrents.get_selection().get_selected()
    	row = self.torrent_liststore.get_iter_first()
        while row != None:
            torrent_id = self.torrent_liststore.get_value(row, 0)
            filename = self.torrent_liststore.get_value(row, 2)
            file_priorities = self.get_file_priorities(torrent_id)
            row = self.torrent_liststore.iter_next(row)
            MainWindow.caller(filename,file_priorities)
        MainWindow.Sync(None)
        self._on_delete_event()
        self.dialog.destroy()

   

    def _on_button_cancel_clicked(self,widget):
    	self.dialog.destroy()
    	self._on_delete_event()

    def _on_torrent_changed(self, treeselection):
    	print "changed"
        (model, row) = treeselection.get_selected()
        if row is None or not model.iter_is_valid(row):
            self.files_treestore.clear()
            self.previous_selected_torrent = None
            return

        if model[row][0] not in self.files:
            self.files_treestore.clear()
            self.previous_selected_torrent = None
            return

        # Save the previous torrents options
        self.save_torrent_options()
        # Update files list
        files_list = self.files[model.get_value(row, 0)]
        self.prepare_file_store(files_list)
        self.previous_selected_torrent = row
    
    def save_torrent_options(self, row=None):
        # Keeps the torrent options dictionary up-to-date with what the user has
        # selected.
        if row is None:
            if self.previous_selected_torrent and self.torrent_liststore.iter_is_valid(self.previous_selected_torrent):
                row = self.previous_selected_torrent
            else:
                return
        torrent_id = self.torrent_liststore.get_value(row, 0)
        # Save the file priorities
        files_priorities = self.build_priorities(
                                self.files_treestore.get_iter_first(), {})
        if len(files_priorities) > 0:
            for i, file_dict in enumerate(self.files[torrent_id]):
                file_dict["download"] = files_priorities[i]

    def prepare_file_store(self, files):
        self.listview_files.set_model(None)
        self.files_treestore.clear()
        split_files = { }
        i = 0
        for file in files:
            self.prepare_file(file, file["path"], i, file["download"], split_files)
            i += 1
        self.add_files(None, split_files)
        self.listview_files.set_model(self.files_treestore)
        self.listview_files.expand_row("0", False)

    def prepare_file(self, file, file_name, file_num, download, files_storage):
        first_slash_index = file_name.find(os.path.sep)
        if first_slash_index == -1:
            files_storage[file_name] = (file_num, file, download)
        else:
            file_name_chunk = file_name[:first_slash_index+1]
            if file_name_chunk not in files_storage:
                files_storage[file_name_chunk] = { }
            self.prepare_file(file, file_name[first_slash_index+1:],
                              file_num, download, files_storage[file_name_chunk])

    def add_files(self, parent_iter, split_files):
        ret = 0
        for key,value in split_files.iteritems():
            if key.endswith(os.path.sep):
                chunk_iter = self.files_treestore.append(parent_iter,
                                [True, key, 0, -1, False, gtk.STOCK_DIRECTORY])
                chunk_size = self.add_files(chunk_iter, value)
                self.files_treestore.set(chunk_iter, 2, chunk_size)
                ret += chunk_size
            else:
                self.files_treestore.append(parent_iter, [value[2], key,
                                        value[1]["size"], value[0], False, gtk.STOCK_FILE])

                if parent_iter and self.files_treestore.iter_has_child(parent_iter):
                    # Iterate through the children and see what we should label the
                    # folder, download true, download false or inconsistent.
                    itr = self.files_treestore.iter_children(parent_iter)
                    download = []
                    download_value = False
                    inconsistent = False
                    while itr:
                        download.append(self.files_treestore.get_value(itr, 0))
                        itr = self.files_treestore.iter_next(itr)

                    if sum(download) == len(download):
                        download_value = True
                    elif sum(download) == 0:
                        download_value = False
                    else:
                        inconsistent = True

                    self.files_treestore.set_value(parent_iter, 0, download_value)
                    self.files_treestore.set_value(parent_iter, 4, inconsistent)
                ret += value[1]["size"]
        return ret

    def build_priorities(self, iter, priorities):
        while iter is not None:
            if self.files_treestore.iter_has_child(iter):
                self.build_priorities(self.files_treestore.iter_children(iter),
                                          priorities)
            elif not self.files_treestore.get_value(iter, 1).endswith(os.path.sep):
                priorities[self.files_treestore.get_value(iter, 3)] = self.files_treestore.get_value(iter, 0)
            iter = self.files_treestore.iter_next(iter)
        return priorities

    def get_file_priorities(self, torrent_id):
        # A list of priorities
        files_list = []
        for file_dict in self.files[torrent_id]:
            if not file_dict["download"]:
                files_list.append(0)
            else:
                files_list.append(1)
        return files_list

    def _on_file_toggled(self, render, path):
    	print "file_toggled"
        # Check to see if we can change file priorities
        (model, row) = self.listview_torrents.get_selection().get_selected()
        print path
        (model, paths) = self.listview_files.get_selection().get_selected_rows()
        if len(paths) > 1:
            for path in paths:
                row = model.get_iter(path)
                self.toggle_iter(row)
        else:
            row = model.get_iter(path)
            self.toggle_iter(row)
        self.update_treeview_toggles(self.files_treestore.get_iter_first())
		
    def toggle_iter(self, iter, toggle_to=None):
        if toggle_to is None:
            toggle_to = not self.files_treestore.get_value(iter, 0)
        self.files_treestore.set_value(iter, 0, toggle_to)
        if self.files_treestore.iter_has_child(iter):
            child = self.files_treestore.iter_children(iter)
            while child is not None:
                self.toggle_iter(child, toggle_to)
                child = self.files_treestore.iter_next(child)
   
    def update_treeview_toggles(self, iter):
        TOGGLE_INCONSISTENT = -1
        this_level_toggle = None
        while iter is not None:
            if self.files_treestore.iter_has_child(iter):
                toggle = self.update_treeview_toggles(
                        self.files_treestore.iter_children(iter))
                if toggle == TOGGLE_INCONSISTENT:
                    self.files_treestore.set_value(iter, 4, True)
                else:
                    self.files_treestore.set_value(iter, 0, toggle)
                    #set inconsistent to false
                    self.files_treestore.set_value(iter, 4, False)
            else:
                toggle = self.files_treestore.get_value(iter, 0)
            if this_level_toggle is None:
                this_level_toggle = toggle
            elif this_level_toggle != toggle:
                this_level_toggle = TOGGLE_INCONSISTENT
            iter = self.files_treestore.iter_next(iter)
        return this_level_toggle

