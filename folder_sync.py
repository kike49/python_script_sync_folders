import argparse
import hashlib
import logging
import os
import shutil
import time


class FolderSynchronizer:
    """Class to group the methods to synchronize two folders"""

    def __init__(self, source, replica, interval, log_file):
        self.source = source
        self.replica = replica
        self.interval = interval
        self.log_file = log_file
        self.logger = None  # assigned in setup_logger
        self.file_handler = None  # assigned in setup_logger
        self.setup_logger()  # calls the method


    def setup_logger(self):
        """Sets the structure of the log output for the script. Writes logs in file and in console with the use of logging. Executes on initialization only"""
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # removes the handlers to avoid duplicated logs on console/file
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # logger file
        self.file_handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

        # console logs
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)


    def close_logger(self):
        '''Closes the logger file properly after its use. Executes only after sync loop is interrupted'''

        if self.file_handler:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)


    @staticmethod
    def calculate_md5(file_path):
        '''Gets the MD5 hash of a given file'''

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunck in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunck)
        return hash_md5.hexdigest()
    

    def sync_folders(self):
        '''Runs the operations to sync the files and directories between the folders'''
        
        self.logger.info("Starting synchronization between folders")
        self.logger.info("Checking latest content in source folder...")
        # sync content in source to replica
        for root, dirs, files in os.walk(self.source):
            replica_root = os.path.join(self.replica, os.path.relpath(root, self.source))
            replica_root = os.path.normpath(replica_root)
            # create directories
            for d in dirs:
                replica_dir = os.path.join(replica_root, d)
                if not os.path.exists(replica_dir):
                    os.makedirs(replica_dir)
                    self.logger.info(f"Created directory in replica folder: '{replica_dir}'")
            # create/update files
            for f in files:
                source_file = os.path.join(root, f)
                replica_file = os.path.join(replica_root, f)
                # if file does not exists or content is different
                if not os.path.exists(replica_file) or self.calculate_md5(source_file) != self.calculate_md5(replica_file):
                    shutil.copy2(source_file, replica_file)
                    self.logger.info(f"Copied file: '{source_file}' from source folder to replica folder: '{replica_file}'")
        self.logger.info("Source folder content checked")

        self.logger.info("Checking excess content in replica folder...")
        # remove files in replica that does not exist in source
        for root, dirs, files in os.walk(self.replica):
            source_root = os.path.join(self.source, os.path.relpath(root, self.replica))
            source_root = os.path.normpath(source_root)
            # directories
            for d in dirs:
                source_dir = os.path.join(source_root, d)
                replica_dir = os.path.join(root, d)
                if not os.path.exists(source_dir):
                    shutil.rmtree(replica_dir)
                    self.logger.info(f"Removed directory in replica folder: '{replica_dir}'")
            # files
            for f in files:
                source_file = os.path.join(source_root, f)
                replica_file = os.path.join(root, f)
                if not os.path.exists(source_file):
                    os.remove(replica_file)
                    self.logger.info(f"File removed from replica folder: '{replica_file}'")
        self.logger.info("Replica folder content excess checked")

        self.logger.info(f"Synchronization completed, restarting in {self.interval} seconds")


def main():
    '''Main block to parse the script with its arguments and run the synchronization loop'''

    parser = argparse.ArgumentParser(description="Synchronize content in two folders")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Sync interval in seconds")
    parser.add_argument("log_file", help="Log file path for details")
    args = parser.parse_args()

    folder_synchronizer = FolderSynchronizer(args.source, args.replica, args.interval, args.log_file)

    try:
        while True:
            folder_synchronizer.sync_folders()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        folder_synchronizer.logger.info("Synchronization stopped by the user")
    finally:
        folder_synchronizer.close_logger()
                

if __name__ == "__main__":
    main()
