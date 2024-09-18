# Folder synchronization script

This Python file and its corresponding test file synchronize one way two folders in a periodic interval set by the user. Content and structure of the first folder (source) will be replacing the existing content of the second folder (replica), keeping the logs of the operations occurred on a file. 

User needs to input the path to the folders and log file plus the periodic interval to set the synchronization. To run the script and test follow these steps:

## To run the script

`python folder_sync.py source_folder_path replica_folder_path number_of_seconds log_file_path`

## To run the tests

`python -m unittest test_folder_sync.py`
