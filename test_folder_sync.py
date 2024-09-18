import logging
import os
import shutil
import unittest

from folder_sync import FolderSynchronizer


class TestFolderSynchronizer(unittest.TestCase):
    '''Tests the correct functionality of the FolderSynchronizer class defined in folder_sync.py'''

    def setUp(self):
        '''Initialization of test environment. Create mock directories and instances of the class to test'''
        
        self.source = "test_source"
        self.replica = "test_replica"
        self.interval = 60
        self.log_file = "test_log_file.log"
        # create test dirs
        os.makedirs(self.source, exist_ok=True)
        os.makedirs(self.replica, exist_ok=True)
        logging.getLogger().handlers.clear() # clears previous loggers to have a clean slate output
        # initialize the class with test args
        self.synchronizer = FolderSynchronizer(self.source, self.replica, self.interval, self.log_file)


    def tearDown(self):
        '''Helper to remove the test dirs and file and close the logger at the end of testings'''

        self.synchronizer.close_logger()
        # remove test dirs and log file
        shutil.rmtree(self.source, ignore_errors=True)
        shutil.rmtree(self.replica, ignore_errors=True)
        os.path.exists(self.log_file)


    def test_file_creation(self):
        '''Simulates a file creation and checks if exists'''

        with open(os.path.join(self.source, "test_file.txt"), "w") as file:
            file.write("test content")
        self.synchronizer.sync_folders()
        self.assertTrue(os.path.exists(os.path.join(self.replica, "test_file.txt")))

    def test_file_udpate(self):
        '''Checks if file content is updated'''

        # creates a mock file with same content in both dirs
        with open(os.path.join(self.source, "test_file.txt"), "w") as file:
            file.write("content")
        with open(os.path.join(self.replica, "test_file.txt"), "w") as file:
            file.write("content")
        
        # updates the file content on the source
        with open(os.path.join(self.source, "test_file.txt"), "w") as file:
            file.write("new content")

        # launch the script and check if content is updated
        self.synchronizer.sync_folders()
        with open(os.path.join(self.replica, "test_file.txt"), "r") as file:
            content = file.read()
        self.assertEqual(content, "new content")


    def test_delete_excess_content(self):
        '''Checks if excess content in replica folder is deleted'''

        # create same file in source and replica, plus a mock file and folder in replica
        with open(os.path.join(self.source, "test_file.txt"), "w") as file:
            file.write("content1")
        with open(os.path.join(self.replica, "test_file.txt"), "w") as file:
            file.write("content1")
        with open(os.path.join(self.replica, "test_file2.txt"), "w") as file:
            file.write("content2")
        os.makedirs(os.path.join(self.replica, "test_dir"), exist_ok=True)

        # remove mock file in source
        os.remove(os.path.join(self.source, "test_file.txt"))

        # launch script and checks that files are removed
        self.synchronizer.sync_folders()
        self.assertFalse(os.path.exists(os.path.join(self.replica, "test_file.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.replica, "test_file2.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.replica, "test_dir")))

if __name__ == "__main__":
    unittest.main()
