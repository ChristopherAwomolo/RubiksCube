import os
import glob

base_drive_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
training_data_dir = os.path.join(base_drive_dir, 'training')
testing_data_dir = os.path.join(base_drive_dir, 'testing')
print(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"full pictures", "v4-7-test"))
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
training_file_list = glob.glob(os.path.join(training_data_dir, '*png'))
print(training_file_list)