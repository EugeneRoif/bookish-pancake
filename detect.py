"""
This is designed to check all mounted volumes meaning inherit LVM may cause duplicates.

To detect only sd*, we can substite the check in the detect function with something similar to:
    pattern = "/dev/sd[a-z]
    fnmatch(x.split()[0],pattern)
"""

import concurrent.futures
import shutil
import subprocess
import time

MIN_MB_SPACE = 10_240
FILES_SIZE_IN_MB = 100
NUM_OF_DD_PROC = 4
MEGABYTE = 1_048_576
PREFIX = "Data_"

config = {
    'mounts_path': '/proc/mounts',
    'local_filesystems': ["ext4", "xfs", "ext2", "ext3", "btrfs", "vfat"],
    'min_mb_space': MIN_MB_SPACE,
    'files_size_in_mb': FILES_SIZE_IN_MB,
    'num_of_dd_proc': NUM_OF_DD_PROC,
    'files_prefix': "PREFIX",
    'output_device': "/dev/urandom",
    'chunk_size': MEGABYTE
}

run = {
    'local_mounts': [],
    'qualified_volumes': []
}


class DetectAndWrite:
    @staticmethod
    def execute_and_time(volume_path, num):
        """Execute the DD command and print the execution time
            :param string volume_path: volume path
            :param int num: suffix to the config["files_prefix"] to append
            """
        start = time.perf_counter()
        subprocess.run(
            [
                "dd", f'if={config["output_device"]}',
                f'of={volume_path}/{config["files_prefix"]}{num}',
                f'bs={config["chunk_size"]}',
                f'count={config["files_size_in_mb"]}',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        end = time.perf_counter()
        print(f'{volume_path}/{config["files_prefix"]}{num} took: {end - start} seconds to complete')

    @staticmethod
    def detect():
        """Detect Volumes in the system with local attributes"""

        with open(config["mounts_path"]) as f:
            mounts = f.readlines()
            run["local_mounts"] = [x.strip().split()[1] for x in mounts if x.split()[2] in config["local_filesystems"]]

    @staticmethod
    def check_min_disk_space():
        """Check for Viable volumes to write"""
        run["qualified_volumes"] = \
            [x for x in run["local_mounts"] if shutil.disk_usage(x).free / MEGABYTE > config["min_mb_space"]]

    @staticmethod
    def write():
        """Define which volume to write to and how many files to run"""
        for vol in run["qualified_volumes"]:
            with concurrent.futures.ThreadPoolExecutor(max_workers=config["num_of_dd_proc"]) as executor:
                for index in range(config["num_of_dd_proc"]):
                    executor.submit(DetectAndWrite.execute_and_time, vol, index)


if __name__ == "__main__":
    DetectAndWrite.detect()
    DetectAndWrite.check_min_disk_space()
    DetectAndWrite.write()
