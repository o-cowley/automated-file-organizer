from tkinter import Tk
import os
import unittest as ut

import fileOrganizer



test_window: Tk = None

# INIT or RE-INIT test_window for new tests
def init_window(): 
    global test_window

    if test_window != None:
        test_window.destroy()
        test_window = None
    
    test_window = fileOrganizer.get_window_for_test()

def destroy_window(): 
    global test_window

    if test_window != None:
        test_window.destroy()
        test_window = None
    
class Test_Test_Methods(ut.TestCase):
    global test_window

    def tearDown(self) -> None:
        super().tearDown()
        destroy_window()

    def test_window_init(self):
        print("Testing test module window initialization", end='\n')

        self.assertIsNone(test_window)
        init_window()
        self.assertIsNotNone(test_window)

        print("Testing test module window initialization -- SUCCESS", end='\n')
       

    def test_window_destroy(self):
        print("Testing test module window destroy", end='\n')

        init_window()
        self.assertIsNotNone(test_window)
        destroy_window()
        self.assertIsNone(test_window)

        print("Testing test module window destroy -- SUCCESS", end='\n')
    


class Test_NAME(ut.TestCase):
    global test_window

    def setUp(self) -> None:
        super().setUp()
        init_window()

    def tearDown(self) -> None:
        super().tearDown()
        destroy_window()

    def test_window_init(self):
        print ("Testing window initialization", end='\n')

        self.assertIsNotNone(test_window)

        print ("Testing window initialization -- SUCCESS", end='\n')

    def test_initial_settings(self):
        print ("Testing all initial settings are empty", end='\n')

        self.assertEqual(len(fileOrganizer.dir_by_name), 0)
        self.assertEqual(len(fileOrganizer.dir_by_type), 0)

        self.assertEqual(fileOrganizer.source_dir, "")
        self.assertEqual(fileOrganizer.callback, "")

        self.assertFalse(fileOrganizer.monitoring)
        self.assertIsNone(fileOrganizer.observer)

        print ("Testing all initial settings are empty -- SUCCESS", end='\n')


    def test_load(self):
        print ("Test loading settings from file")

        cwd = os.getcwd()
        with open('settings.txt', 'w') as file:
            file.write(f'type*abc*{cwd}\n')
            file.write(f'type*def*{cwd}\n')
            file.write(f'type*ghi*{cwd}\n')

            file.write(f'keyword*jkl*{cwd}\n')
            file.write(f'keyword*mno*{cwd}\n')
            file.write(f'keyword*pqr*{cwd}\n')

        test_window.winfo_children()[0].winfo_children()[-2].invoke()
        list_type = fileOrganizer.dir_by_type
        list_name = fileOrganizer.dir_by_name
        self.assertEqual(list_type['abc'], cwd)
        self.assertEqual(list_type['def'], cwd)
        self.assertEqual(list_type['ghi'], cwd)

        self.assertEqual(list_name['jkl'], cwd)
        self.assertEqual(list_name['mno'], cwd)
        self.assertEqual(list_name['pqr'], cwd)

        print ("Test loading settings from file -- SUCCESS", end='\n')
           

    def test_save(self):
        print("Test saving loaded settings to file")

        cwd = os.getcwd()
        # Establish test values
        dir_name = {
            'abc' : cwd, 
            'def' : cwd, 
            'ghi' : cwd
            }
        dir_type = {
            'jkl' : cwd, 
            'mno' : cwd, 
            'pqr' : cwd
            }
        # Insert test values into directories
        fileOrganizer.dir_by_name = dir_name
        fileOrganizer.dir_by_type = dir_type
        # Write directories to file
        test_window.winfo_children()[0].winfo_children()[-1].invoke()

        # Clear directories
        fileOrganizer.dir_by_name = {}
        fileOrganizer.dir_by_name = {}

        # Load from file (Load function tested seperately)
        test_window.winfo_children()[0].winfo_children()[-2].invoke()

        # Assert equality
        self.assertDictEqual(dir_name, fileOrganizer.dir_by_name)
        self.assertDictEqual(dir_type, fileOrganizer.dir_by_type)

        print("Test saving loaded settings to file -- SUCCESS", end='\n')




    















if __name__ == '__main__':
    suite = ut.TestSuite()
    suite.addTest(ut.makeSuite(Test_Test_Methods))
    suite.addTest(ut.makeSuite(Test_NAME))
    ut.TextTestRunner(verbosity=2).run(suite)




# Functions to test:
# 
# loadSettings -- DONE
# saveSettings -- DONE
# moveFile
# makeUnique
# trigger_organize
# monitor
# *jump_mouse*
# add_new_filetype
# add_new_key
# add_element_type
# add_element_name
# delete_by_type
# delete_by_key
# get_file_location
# get_window_for_test -- DONE
# 
# Classes to test:
# 
# MoveHandler
# Window -- DONE-ish
# 
