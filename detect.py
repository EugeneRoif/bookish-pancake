"""
Importnat notes:
This is designed to check all mounted volumes meaning inherit LVM may cause duplicates.

To detect only sd*, we can substite the check in the detect function with something similar to:
    pattern = "/dev/sd[a-z]
    fnmatch(x.split()[0],pattern)
"""

import os
import shutil
import subprocess
import time
import threading

config = {
    'mounts_path' : '/proc/mounts',
    'local_filesystems' : ["ext4", "xfs", "ext2", "ext3", "btrfs", "vfat"],
    'min_mb_space' : 10240,
    'files_size_in_mb' : 100,
    'num_of_dd_proc' : 4,
    'files_prefix' : "Data_",
    'output_device' : "/dev/urandom",
    'chunk_size' : 1048576
    }

run = {
        'local_mounts' : [],
        'qualified_volumes' : []
}

class detect_and_write:
    def execute_and_time(vol, num):
            """Execute the DD command and print the execution time
            :param string vol: volume path
            :param int num: suffix to the config["files_prefix"] to append
            """
            start = time.perf_counter()
            subprocess.run(["dd", f'if={config["output_device"]}', f'of={vol}/{config["files_prefix"]}{num}', f'bs={config["chunk_size"]}', f'count={config["files_size_in_mb"]}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            end = time.perf_counter()
            print(f'{vol}/{config["files_prefix"]}{num} took: {end - start} seconds to complete')

    def detect():
        """Detect Volumes in the system with local attributes"""

        with open(config["mounts_path"]) as f:
            mounts = f.readlines()
            run["local_mounts"] = [x.strip().split()[1] for x in mounts if x.split()[2] in config["local_filesystems"]]

    def check_min_disk_space():
        """Check for Viable volumes to write"""

        run["qualified_volumes"] = [x for x in run["local_mounts"] if (shutil.disk_usage(x).free)/1024/1024 > config["min_mb_space"]]

    def write():
        """Define which volume to write to and how many files to run"""

        for vol in run["qualified_volumes"]:
            for i in range(0, config["num_of_dd_proc"]):
                th = threading.Thread(target=detect_and_write.execute_and_time, args=(vol, i))
                th.start()
            th.join()

if __name__ == "__main__":
        detect_and_write.detect()
        detect_and_write.check_min_disk_space()
        detect_and_write.write()
