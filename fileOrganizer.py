from os import mkdir, scandir, rename
from os.path import splitext, exists, join
from shutil import move
import string
from time import sleep

# TODO: make sure that this is documented and recorded somewhere
import pyautogui as pa

import logging
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# The source directory, ie. the Downloads folder, that will be watched for changes to organize
# source_dir = "/Users/olivercowley/Downloads"
source_dir: string = ""

# Dictionary arranged by key phrases or words with destination based on assumed content if the key is found
dir_by_name = {}
    # "intel": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded INTEL"
    

# Dictionary sorted by file type with intended destination for the given type
dir_by_type = {}
    # ".pdf": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded PDFs",
    # ".html": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded HTML",
    # ".jpg": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded Images",
    # ".svg": "/Users/olivercowley/Desktop/Organized Downloads/Downloaded Images"
    


# This variable represents the current status of the organizer, if True then ongoing monitoring is happening, 
# False means the user must trigger the organization
monitoring: bool = False

# Observer variable to allow for global access for starting and stopping the automated organization 
observer: Observer = None

# TODO: make this clearer and document this -- also need a way to ensure multiple wiggle handlers are not started at the same time (a boolean guard should be enough)
callback: str = ""

# Loads organization rules from a settings file located in the same directory as the script
# 
#   Informs users if there is not a settings file yet. Otherwise parses the file and inputs the 
#   rules in to the organizer, updating the gui accordingly. If the rule already exists then it is
#   ignored, and if the filepath provided does not exist, the user is required to select one
# 
#   @param  Frame  type_frame   Frame that contains all of the file type rules
#   @param  Frame  key_frame    Frame that contains all of the keyword rules
# 
def loadSettings(type_frame: Frame, key_frame: Frame):
    if exists('settings.txt'):
        with open('settings.txt', 'r') as file:
            for line in list(file):
                curr = line.strip().split('*')
                if curr[0] == 'type':
                    if curr[1] not in dir_by_type:
                        if exists(curr[2]):
                            add_element_type(type_frame, curr[1], curr[2])
                        else:
                            showinfo(message=f'The saved directory doesn\'t exist, please pick a directory for type {curr[1]}.')
                            file_path = ''
                            while file_path == '':
                                file_path = askdirectory(
                                    title= 'Pick a folder to put it in',
                                    initialdir='/'
                                )
                            add_element_type(type_frame, curr[1], file_path)
                elif curr[0] == 'keyword':
                    if curr[1] not in dir_by_name:
                        if exists(curr[2]):
                            add_element_name(key_frame, curr[1], curr[2])
                        else:
                            showinfo(message=f'The saved directory doesn\'t exist, please pick a directory for keyword {curr[1]}.')
                            file_path = ''
                            while file_path == '':
                                file_path = askdirectory(
                                    title= 'Pick a folder to put it in',
                                    initialdir='/'
                                )
                            add_element_name(key_frame, curr[1], file_path)
    else:
        showinfo(message='Sorry, you don\'t have a settings file yet!\n Add some organization rules and hit save to set one up.')            


# Saves organization rules to a settings file, creates a new one if it does not already exist
# 
#   Formats the file according to the rules required to load the settings next time the organizer is run
# 
def saveSettings():
    with open('settings.txt', 'w') as file:
        for key in dir_by_type:
            file.write(f'type*{key}*{dir_by_type[key]}\n')
        for key in dir_by_name:
            file.write(f'keyword*{key}*{dir_by_name[key]}\n')
        
        


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
                was_found = False
                for key in dir_by_name:    
                    if str(key) in name.lower():
                        moveFile(dir_by_name[key], entry, name)
                        # logging.info("Moved document file: " + name)
                        was_found = True
                if(was_found == False):
                    for key in dir_by_type:    
                        if name.lower().endswith(str(key)):
                            moveFile(dir_by_type[key], entry, name)
                            # logging.info("Moved document file: " + name)




# Manually triggered version of the function to organize source_dir
# 
#   The function scans for key pharses first as content is considered more important than file type. If no key
#       phrases are detected then it sorts the files by type. If neither are found then file is left in downloads
# 
def trigger_organize():
    if(source_dir != ""):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                was_found = False
                for key in dir_by_name:    
                    if str(key) in name.lower():
                        moveFile(dir_by_name[key], entry, name)
                        # logging.info("Moved document file: " + name)
                        was_found = True
                if(was_found == False):
                    for key in dir_by_type:    
                        if name.lower().endswith(str(key)):
                            moveFile(dir_by_type[key], entry, name)
                            # logging.info("Moved document file: " + name)

# Toggles between automatic observing/organization and manually triggered optimization
# 
#   Does not switch to automatic monitoring unless a directory has been selected. Changes
#   the colour of the button text according to if the monitoring is happening(green) or not(red)
# 
#   @param  Button  button    the button used to toggle with the text that needs the colour changed
# 
def monitor(button: Button):
    global source_dir
    if (source_dir == ""):
        showinfo(message="You dont have a directory selected to monitor yet!")
    else:
        global monitoring
        global observer
        if monitoring:
            observer.stop()
            observer.join()
            observer = None
        else:
            observer = Observer()
            observer.schedule(MoveHandler(), source_dir, recursive=False)
            observer.start()
        monitoring = False if monitoring else True
        button.config(fg= 'GREEN' if monitoring else 'RED')


# TODO: Annotate this function
# This function triggers the mouse wiggling once and then schedules another wiggle for some time afterwards, the name of the 'after' callback is assigned to the
#  global var callback so that it can be used to cancel when the cancel button is pressed 

# A guard will need to be implemented since you can schedule multiple wiggle cycles currently -- the free parking is no longer necessary in this way since after_cancel can clear the scheduled callback
#  consequently the positions and those checks arent actually needed, the boolean guard would be enough as we are flipping it with a cancel button or perhaps the init button is a toggle like the observer has


def jump_mouse(free_parking: Label, window: Tk):
    counter = 0
    xPos, yPos = pa.position()

    print(pa.position())
    pa.moveRel(200, 0)
    print(pa.position())

    pa.press('shift')
        
    pa.moveRel(-200, 0)
    print(pa.position())
    # sleep(2)
    counter += 1

    current_x = pa.position()[0] - free_parking.winfo_rootx()
    current_y = pa.position()[1] - free_parking.winfo_rooty()

    global callback
    if(counter == 10 or (current_x > 0 and current_x < free_parking.winfo_width() and current_y > 0 and current_y < free_parking.winfo_height()) ):
        print('Done done done')
        window.after_cancel(callback)
        
    else:
        
        callback = window.after(2000, jump_mouse, free_parking, window)
        



# Window class that takes in a frame and initializes all settings and characteristics of the GUI
# 
#   Initializes and places all elements within the root frame before the Window is launched
# 
#   @param  Frame   Frame   The frame that is going to be initialized
# 
class Window(Frame):

    # Automatically run initialization function that triggers all other  
    # 
    #   @param  string  master      master Frame, set to NONE as this is the top level window
    #  
    def __init__(self, master=NONE):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    # Custom init function that creates and packs all elements of the visible window
    # 
    #   Initializes all elements including assigning event handler functions based on hard coded
    #   types and keywords
    # 
    #   @param  Window  self    Top level window of the GUI, will always be the main Frame 
    # 
    # 
    def init_window(self):

        

        #  Iitializes enclosing Frame for the GUI
        self.master.title("Automated File Organizer")
        self.pack(fill=BOTH, expand=0)

        # Creates Frame to hold Main information: Source directory, manual/automatic organization button and status display, and trigger to do a manual organize of the folder
        source_frame = Frame(self, relief=RAISED, borderwidth=4)
        source_frame.pack(fill=X)
        
        # Label to display the location that is being organized (and possible monitored based on status)
        organizing_location = Label(source_frame, text=f'This is the location you are organizing: {source_dir}', fg='BLUE')
        organizing_location.pack(side=LEFT)

        # Manual organization trigger
        organize_button = Button(source_frame, text='Organize folder', command=trigger_organize)
        organize_button.pack(side=RIGHT)

        # Button that displays the status of automatic(green)/manual(red) organization based on text colour, on click toggles between thw two
        global monitoring
        monitor_button = Button(source_frame, text='Monitoring?',fg='green' if monitoring else 'red', command=lambda: monitor(monitor_button))
        monitor_button.pack(side=RIGHT)



        # TODO: document and clean this up, too much lamda stuff that is just raw calling functions, compartmentalize the functions and make it cleaner for things to be started and stopped
        #  ALSO, make sure that the toggle or cancel clears all things, guard the cancel button (or make toggle instead) as after_cancel throws error if there isn't a valid after TO cancel
        move_mouse = Button(source_frame, text='Move the Mouse to the right', command=lambda: jump_mouse(organizing_location, window))
        move_mouse.pack(side=RIGHT)

        global callback
        cancel_move = Button(source_frame, text='Cancel mouse wiggle', command=lambda: window.after_cancel(callback))
        cancel_move.pack(side=RIGHT)
        

        # Frame setup for display of the various filetypes and keywords that are being checked for organization

        # Setup frame to display the types we are organizing
        type_frame = Frame(self, relief=SUNKEN, borderwidth=1)
        
        Label(self, text='Sorted by file type:', fg='#B76E79').pack()
        for entry in dir_by_type:
            add_element_type(type_frame, str(entry), str(dir_by_type[entry]))

        type_frame.pack(fill=X)

        # Setup frame to display the keywords we are checking for organizing 
        name_frame = Frame(self, relief=SUNKEN, borderwidth=1)

        Label(self, text='Sorted by keywords in filename:', fg='#B76E79').pack()
        for entry in dir_by_name:
            add_element_name(name_frame, str(entry), str(dir_by_name[entry]))
        
        name_frame.pack(fill=X)


        # Initialize the menubar
        menubar = Menu(self.master)

        menu_options = Menu(menubar, tearoff=0)
        menu_options.add_command(label="Hide Settings", command=lambda: self.master.withdraw())
        menu_options.add_command(label="Show Settings", command=lambda: self.master.deiconify())
        menu_options.add_separator()
        menu_options.add_command(label="Change file we are organizing", command=lambda: getFileLocation(self, organizing_location))
        menu_options.add_command(label="Add new type", command=lambda: add_new_filetype(type_frame))
        menu_options.add_command(label="Add new keyword", command=lambda: add_new_key(name_frame))
        menubar.add_cascade(label='Controls', menu=menu_options)

        menu_log = Menu(menubar, tearoff=0)
        menu_log.add_command(label="Print type dictionary", command=lambda: print(dir_by_type))
        menu_log.add_command(label="Print keyword dictionary", command=lambda: print(dir_by_name))
        
        menubar.add_cascade(label='Dev Tools', menu=menu_log)

        self.master.config(menu=menubar)

        # Load and save buttons for settings file

        Button(self, text="Load Saved Settings", command=lambda: loadSettings(type_frame, name_frame)).pack(side=LEFT)
        Button(self, text="Save Settings", command=saveSettings).pack(side=RIGHT)



# Prompts user to enter a filetype to be included in the organization
# 
#   Popups prompt for the new filetype followed by the filepath of the folder to put the files of that type in
#   If any of the prompts are canceled by the user, nothing is added to the gui or the directories and the function
#   immediately returns
# 
#   @param  Frame  frame    Parent frame that holds keyword/filepath entries
# 
def add_new_filetype(frame: Frame):
    new_filetype = ''
    while new_filetype == '':
        new_filetype = askstring(title="Add this file type", prompt="Enter a new file type to organize")
    
    if new_filetype is None:
        return

    
    filename = askdirectory(
        title= 'Pick a folder to put it in',
        initialdir='/'
    )
    if filename == '':
        return

    add_element_type(frame, new_filetype, filename)


# Prompts user to enter a keyword to be included in the organization
# 
#   Popups prompt for the new keyword followed by the filepath of the folder to put the files with they keyword in to.
#   If any of the prompts are canceled by the user, nothing is added to the gui or the directories and the function
#   immediately returns
# 
#   @param  Frame  frame    Parent frame that holds keyword/filepath entries
# 
def add_new_key(frame: Frame):
    new_key = ''
    while new_key == '':
        new_key = askstring(title="Add a new key", prompt="Enter a new keyword to sort by")

    if new_key is None:
        return

    
    filename = askdirectory(
        title= 'Pick a folder to put it in',
        initialdir='/'
    )
    if filename == '':
        return
    
    add_element_name(frame, new_key, filename)


# Adds a frame to the gui that represents an element from the filetype dictionary
# 
#   Adds all the required labels and buttons to the frame and registers the event handler
#   for the button to trigger deletion when pressed. Also adds the element to the dir_by_type
#   dictionary.
# 
#   @param  Frame   frame       parent frame to hold this element
#   @param  string  filetype    name of the filetype to be added
#   @param  string  filepath    filepath that a file with the given keyword should be moved to
# 
# 
def add_element_type(frame: Frame, fileType: string, filepath: string):
    new_frame = Frame(frame)
    Label(new_frame, text=f'FileType: {fileType}', width= 15, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Label(new_frame, text=f'Moved to file: {filepath}', padx=5, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Button(new_frame, text="Delete", command=lambda: delete_by_type(new_frame, fileType)).pack(side=RIGHT)
    dir_by_type[fileType] = filepath
    new_frame.pack(fill=X)


# Adds a frame to the gui that represents an element from the keyword dictionary
# 
#   Adds all the required labels and buttons to the frame and registers the event handler
#   for the button to trigger deletion when pressed. Also adds the element to the dir_by_name
#   dictionary.
# 
#   @param  Frame   frame       parent frame to hold this element
#   @param  string  keyword     name of the keyword to be added
#   @param  string  filepath    filepath that a file with the given keyword should be moved to
# 
# 
def add_element_name(frame: Frame, keyword: string, filepath: string):
    new_frame = Frame(frame)
    Label(new_frame, text=f'KeyWord: {keyword}', width=15, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Label(new_frame, text=f'Moved to file: {filepath}', padx=5, pady=5, anchor=W, bd=5).pack(side=LEFT)
    Button(new_frame, text="Delete", command=lambda: delete_by_key(new_frame, keyword)).pack(side=RIGHT)
    dir_by_name[keyword] = filepath
    new_frame.pack(fill=X)

# Removes an entry from the filetype dictionary and removes its associated frame from the gui
# 
#   @param  Frame   frame       frame that contains the info and button for this entry
#   @param  string  element     key value for the given entry in the dir_by_type
# 
# 
def delete_by_type(frame: Frame, element: string):
    dir_by_type.pop(element)
    frame.destroy()

# Removes an entry from the keyword dictionary and removes its associated frame from the gui
# 
#   @param  Frame   frame       frame that contains the info and button for this entry
#   @param  string  element     key value for the given entry in the dir_by_name
# 
# 
def delete_by_key(frame: Frame, element: string):
    dir_by_name.pop(element)
    frame.destroy()



# Prompt user for a new source directory and update global variables/labels to reflect change
# 
#   Allows user to select any directory in the computer through the file select dialog
# 
#   @param          self    containing frame -- UNUSED
#   @param  Label   label   Label displaying the source directory
# 
#   
def getFileLocation(self, label_to_change: Label):
    
    # Prompt user to select a new directory
    filename = askdirectory(
        title= 'Pick a folder to organize',
        initialdir='/'
    )

    global source_dir
    source_dir = filename


    #  Change text on label to new source directory 
    label_to_change.config(text = 'This is the location: ' + source_dir)

    showinfo(message="If you currently have monitoring turned on, please turn off and on again to update monitored directory")


# TODO: document this function--it is to get a window so that it can be tested--INCLUDE BLOCK FOR RUN MODE
def get_window_for_test():
    window = Tk()
    
    Window(window)

    window.resizable(False, False)

    return window



# Main

if __name__ == "__main__":
    window = Tk()
    
    # This is the code to implement the console logging of the files when they are moved, not necessary beyond as a dev tool
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    Window(window)

    window.resizable(False, False)

    window.mainloop()



# THIS IS THE CODE TO UNCOMMENT FOR AUTOMATIC MONITORING (CAREFUL ABOUT SOURCE DIR SETTINGS BEFORE DOING SO)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO,
#                         format='%(asctime)s - %(message)s',
#                         datefmt='%Y-%m-%d %H:%M:%S')
#     path = source_dir
#     event_handler = MoveHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=False)
#     observer.start()
#     try:
#         while True:
#             sleep(10)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()

