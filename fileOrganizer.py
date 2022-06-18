from os import mkdir, scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from tkinter import *

class Window(Frame):

    def __init__(self, master=NONE):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("GUI")
        self.pack(fill=BOTH, expand=1)

        quitButton = Button(self, text="Talk to me", command=self.showText)
        quitButton.grid(row=0, column=0, sticky=E)

        entry = Entry(self)
        entry.grid(row=1, column = 1)

        doSomething = Button(self, text="Show me the entry", command=lambda: self.reactToEntry(entry.get()))
        doSomething.grid(row=1, column=0)

    def clearTextSpot(self):
        slave = self.grid_slaves(row=0, column=1)
        if(len(slave) > 0):
            slave[0].grid_forget()


    def showText(self):
        self.clearTextSpot()
        text = Label(self, text="Hey there good lookin!")
        text.grid(row=0, column = 1)

    def reactToEntry(self, toPut):
        self.clearTextSpot()
        text = Label(self, text=toPut)
        text.grid(row=0, column = 1, sticky=W)

        # new_dir = "/Users/olivercowley/Desktop/Organized " + toPut
        # mkdir(new_dir)
        # self.master.destroy()

window = Tk()

Window(window)

window.mainloop()


# The source directory, ie. the Downloads folder, that will be watched for changes to organize
source_dir = "/Users/olivercowley/Downloads"

# Dictionary arranged by key phrases or words with destination based on assumed content if the key is found
dir_by_name = {
    "intel": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded INTEL"
    }

# Dictionary sorted by file type with intended destination for the given type
dir_by_type = {
    ".pdf": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded PDFs",
    ".html": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded HTML",
    ".jpg": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded Images",
    ".svg": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded Images"
    }

# Moves the file from entry to dir/name or obtains a unique version of dir/name and then moves
# 
#   @param  string  dir     enclosing directory of the destination file
#   @param  string  entry   filepath of the file that is to be moved
#   @param  string  name    name of the file to be moved
# 
def moveFile(dir, entry, name):
    if exists(f'{dir}/{name}'):
        unique_name = makeUnique(dir, name)
        oldName = join(dir, name)
        newName = join(dir, unique_name)
        rename(oldName, newName)
    move(entry, dir)

# Generates a unique version of the intended file path to be moved to
# 
#   Appends a number to the end of the intended filepath, incremented by one from the same named file already 
#   contained in the destination folder 
# 
#   @param  string  dest    enclosing directory of the destination file
#   @param  string  name    name of the file to be moved
# 
#   @return string  a string representing the intended filepath to be moved to
# 
def makeUnique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f'{dest}/{name}'):
        name = f'{filename}({str(counter)}){extension}'
        counter += 1
    return name

# Handler class that is intialized to pass as an eventHandler for the observer
# 
#   @param  FileSystemEvenHandler   Event handler object that allows the overriding of the on_modified function
#   
class MoveHandler(FileSystemEventHandler):

    # Required function that is called whenever a change is detected by the observer
    # 
    #   The function scans for key pharses first as content is considered more important than file type. If no key
    #   phrases are detected then it sorts the files by type. If neither are found then file is left in downloads
    # 
    #   @param  Event           event   Event object -- not used
    #   @param  MoveHandler     self    MoveHandler object 
    #  
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                for key in dir_by_name:    
                    if str(key) in name.lower():
                        moveFile(dir_by_name[key], entry, name)
                        logging.info("Moved document file: " + name)
                        return
                for key in dir_by_type:    
                    if name.endswith(str(key)):
                        moveFile(dir_by_type[key], entry, name)
                        logging.info("Moved document file: " + name)
                        return


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO,
#                         format='%(asctime)s - %(message)s',
#                         datefmt='%Y-%m-%d %H:%M:%S')
#     path = source_dir
#     event_handler = MoveHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=True)
#     observer.start()
#     try:
#         while True:
#             sleep(10)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()
