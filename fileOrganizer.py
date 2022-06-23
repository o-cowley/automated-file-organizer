from os import mkdir, scandir, rename
from os.path import splitext, exists, join
from shutil import move
import string
from time import sleep

import logging
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# The source directory, ie. the Downloads folder, that will be watched for changes to organize
# source_dir = "/Users/olivercowley/Downloads"
source_dir = ""

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

monitoring = False





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


#  THIS IS THE SAME AS IN THE MOVE HANDLER, JUST USING FOR CUSTOM TRIGGER OF ORGANIZATION
def trigger_organize():
    if(source_dir != ""):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                was_found = False
                for key in dir_by_name:    
                    if str(key) in name.lower():
                        moveFile(dir_by_name[key], entry, name)
                        logging.info("Moved document file: " + name)
                        was_found = True
                if(was_found == False):
                    for key in dir_by_type:    
                        if name.endswith(str(key)):
                            moveFile(dir_by_type[key], entry, name)
                            logging.info("Moved document file: " + name)

def monitor(button: Button):
    global source_dir
    if (source_dir != ""):
        showinfo(message="You dont have a directory to monitor yet!")
    else:
        global monitoring
        monitoring = False if monitoring else True
        button.config(fg= 'GREEN' if monitoring else 'RED')

class Window(Frame):

    def __init__(self, master=NONE):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        self.master.title("GUI")
        self.pack(fill=BOTH, expand=0)

        source_frame = Frame(self, relief=RAISED, borderwidth=4)
        source_frame.pack(fill=X)
        
        organizing_location = Label(source_frame, text=f'This is the location you are organizing: {source_dir}', fg='BLUE')
        organizing_location.pack(side=LEFT)


        organize_button = Button(source_frame, text='Click me to organize the folder', command=trigger_organize)
        organize_button.pack(side=RIGHT)

        global monitoring
        monitor_button = Button(source_frame, text='Monitoring?',fg='green' if monitoring else 'red', command=lambda: monitor(monitor_button))
        monitor_button.pack(side=RIGHT)



        
        type_frame = Frame(self, relief=SUNKEN, borderwidth=1)
        
        Label(self, text='Sorted by file type:', fg='#B76E79').pack()
        for entry in dir_by_type:
            add_element_type(type_frame, str(entry), str(dir_by_type[entry]))

        type_frame.pack(fill=X)


        name_frame = Frame(self, relief=SUNKEN, borderwidth=1)

        Label(self, text='Sorted by keywords in filename:', fg='#B76E79').pack()
        for entry in dir_by_name:
            add_element_name(name_frame, str(entry), str(dir_by_name[entry]))
        
        name_frame.pack(fill=X)

        Button(self, text="Click here to change file we are organizing", command=lambda: getFileLocation(self, organizing_location)).pack(side=LEFT)
        Button(self, text="Add new type", command=lambda: add_new_filetype(type_frame)).pack(side=RIGHT)
        Button(self, text="Add new keyword", command=lambda: add_new_key(name_frame)).pack(side=RIGHT)
        Button(self, text="LOG DIR BY TYPE", command=lambda: print(dir_by_type)).pack(side=LEFT)
        Button(self, text="LOG DIR BY KEY", command=lambda: print(dir_by_name)).pack(side=LEFT)

        # quitButton = Button(self, text="Talk to me", command=self.showText)
        # quitButton.grid(row=0, column=0, sticky=E)

        # entry = Entry(self)
        # entry.grid(row=1, column = 1)


        # doSomething = Button(self, text="Show me the entry", command=lambda: self.reactToEntry(entry.get()))
        # doSomething.grid(row=1, column=0)

        # findFile = Button(self, text='Find a file',font =
        #        ('calibri', 10, 'bold', 'underline'),
        #         foreground = 'red', command=getFileLocation)
        # findFile.grid(row=2, column=0)

    def clearTextSpot(self):
        slave = self.grid_slaves(row=0, column=1)
        if(len(slave) > 0):
            slave[0].grid_forget()


    def showText(self):
        self.clearTextSpot()
        text = Label(self, text="Hey there....")
        text.grid(row=0, column = 1)

    def reactToEntry(self, toPut):
        self.clearTextSpot()
        text = Label(self, text=toPut)
        text.grid(row=0, column = 1, sticky=W)

        # new_dir = "/Users/olivercowley/Desktop/Organized " + toPut
        # mkdir(new_dir)
        # self.master.destroy()


def add_new_filetype(frame: Frame):
    new_filetype = askstring(title="Add this file type", prompt="Enter a new file type to organize")

    filename = askdirectory(
        title= 'Pick a folder to put it in',
        initialdir='/'
    )
    
    add_element_type(frame, new_filetype, filename)

def add_new_key(frame: Frame):
    new_key = askstring(title="Add a new key", prompt="Enter a new keyword to sort by")

    filename = askdirectory(
        title= 'Pick a folder to put it in',
        initialdir='/'
    )
    
    add_element_name(frame, new_key, filename)



def add_element_type(frame: Frame, fileType: string, filename: string):
    new_frame = Frame(frame)
    Label(new_frame, text=f'FileType: {fileType}', width= 15, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Label(new_frame, text=f'Moved to file: {filename}', padx=5, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Button(new_frame, text="Delete", command=lambda: delete_by_type(new_frame, fileType)).pack(side=RIGHT)
    dir_by_type[fileType] = filename
    new_frame.pack(fill=X)


def add_element_name(frame: Frame, keyword: string, filename: string):
    new_frame = Frame(frame)
    Label(new_frame, text=f'KeyWord: {keyword}', width=15, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Label(new_frame, text=f'Moved to file: {filename}', padx=5, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Button(new_frame, text="Delete", command=lambda: delete_by_key(new_frame, keyword)).pack(side=RIGHT)
    dir_by_name[keyword] = filename
    new_frame.pack(fill=X)


def delete_by_type(frame: Frame, element: string):
    dir_by_type.pop(element)
    frame.destroy()

def delete_by_key(frame: Frame, element: string):
    dir_by_name.pop(element)
    frame.destroy()



def getFileLocation(self, label_to_change: Label):
    filename = askdirectory(
        title= 'Pick a folder to organize',
        initialdir='/'
    )

    global source_dir
    source_dir = filename

    #  THIS CHANGES THE LABEL TEXT AFTER IT HAS BEEN CREATED
    label_to_change.config(text = 'This is the location: ' + source_dir)
    

window = Tk()

Window(window)

window.mainloop()
