# detect module

Importnat notes:
This is designed to check all mounted volumes meaning inherit LVM may cause duplicates.

To detect only sd\*, we can substite the check in the detect function with something similar to:

    pattern = “/dev/sd[a-z]
    fnmatch(x.split()[0],pattern)


### _class_ detect.detect_and_write()
Bases: `object`


#### check_min_disk_space()
Check for Viable volumes to write


#### detect()
Detect Volumes in the system with local attributes


#### execute_and_time(num)
Execute the DD command and print the execution time
:param string vol: volume path
:param int num: suffix to the config[“files_prefix”] to append


#### write()
Define which volume to write to and how many files to run
