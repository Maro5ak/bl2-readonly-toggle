import os
import re
from tkinter import *
from tkinter.ttk import Treeview, Scrollbar
import keyboard
import winsound
from stat import S_IREAD, S_IWRITE


class InvalidSaveDirectory(Exception):
    pass


class InvalidSaveFile(Exception):
    pass


class Window:
    def __init__(self, root):
        self.toggle_hotkey = 'f7'
        self.user_select_enable = False

        self.save_files = SaveFiles()

        keyboard.on_press(self.hotkey_press)
        root.bind('<KeyPress>', self.hotkey_record)

        self.menubar = Menu(root)
        root.config(menu=self.menubar)

        self.file_menu = Menu(root, tearoff=False)
        self.file_menu.add_command(label='Hotkey', command=self.hotkey_select)
        self.menubar.add_cascade(label='Hotkey', menu=self.file_menu)

        self.columns = ['ID', 'file_name']
        self.file_tree = Treeview(root, columns=self.columns, show='headings')
        self.scrollbar = Scrollbar(root, orient=VERTICAL, command=self.file_tree.yview)

        self.tree_view_init()

        self.counter = 0
        for save_file in self.save_files.directory_list:
            self.file_tree.insert('', END, values=(self.counter, save_file))
            self.counter += 1

    def tree_view_init(self):
        self.file_tree.heading('ID', text='ID')
        self.file_tree.column('ID', minwidth=5, width=20)
        self.file_tree.heading('file_name', text='File Name')

        self.file_tree.configure(yscrollcommand=self.scrollbar.set)
        self.file_tree.pack(expand=TRUE, fill=BOTH, side='left')
        self.scrollbar.pack(expand=TRUE, fill=Y)
        self.file_tree.bind('<<TreeviewSelect>>', self.item_selected)

    def item_selected(self, event):
        for selected_item in self.file_tree.selection():
            item = self.file_tree.item(selected_item)
            self.save_files.savefile = item["values"][1]
            message = f'Current save - {self.save_files.savefile}'
            self.save_files.create_absolute_path()
            root.title(message)

    def hotkey_record(self, event):
        if self.user_select_enable:
            self.timeout(True)
            self.toggle_hotkey = event.keysym
            self.user_select_enable = False

    def timeout(self, press=None):
        if not press and self.user_select_enable:
            self.user_select_enable = False

    def hotkey_select(self):
        self.user_select_enable = True
        root.after(5000, lambda: self.timeout(False))

    def hotkey_press(self, event):
        if self.toggle_hotkey.lower() == event.name:
            self.save_files.toggle_readonly()


class SaveFiles:
    def __init__(self):
        self.read_frequency = 500
        self.write_frequency = 200
        self.duration = 200
        self.readonly_toggle = False
        self.savefile_directory = ""
        self.savefile = ""
        self.savefile_absolute_path = ""
        self.directory_list = []
        self.attempt_find_savefiles()

    def create_absolute_path(self):
        self.savefile_absolute_path = rf"{self.savefile_directory}\{self.savefile}"

    def attempt_find_savefiles(self):
        if self.savefile_directory == "":
            self.path_to_savefiles()

        regex = r"^[\w]+\.sav$"
        re.compile(regex)
        self.directory_list = [file for file in os.listdir(self.savefile_directory) if re.match(regex, file)]

    def path_to_savefiles(self):
        user_home = os.path.expanduser('~')
        bl2_default = r"\Documents\My Games\Borderlands 2\WillowGame\SaveData" + "\\"
        self.savefile_directory = user_home + bl2_default
        dir_list = os.listdir(self.savefile_directory)
        if len(dir_list) != 1:
            raise InvalidSaveDirectory('Ambiguous savefile directory')

        self.savefile_directory += dir_list[0]
        self.make_all_writable()

    # if you forget to change it, for some reason
    def make_all_writable(self):
        for savefile in self.directory_list:
            path = self.savefile_directory + '\\' + savefile
            os.chmod(path, S_IWRITE)
    def toggle_readonly(self):
        if self.savefile_absolute_path == "":
            raise InvalidSaveFile('No save file provided!')
        if self.readonly_toggle:
            os.chmod(self.savefile_absolute_path, S_IREAD)
            winsound.Beep(self.read_frequency, self.duration)
        else:
            os.chmod(self.savefile_absolute_path, S_IWRITE)
            winsound.Beep(self.write_frequency, self.duration)
        self.readonly_toggle = not self.readonly_toggle


# TODO: User can specify their directory
root = Tk()
root.title('Borderlands 2 ReadOnly Toggle')
root.geometry('500x300')
window = Window(root)
root.mainloop()
