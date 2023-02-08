
import os

def run(sh_path,data_path,grid_level):
    if os.path.exists(sh_path) and os.path.exists(data_path) and grid_level in [1,2,3]:
        cmd="{} {} {}".format(sh_path,data_path,grid_level)
        os.system(cmd)
    else:
        print("check os.path.exists(sh_path) and os.path.exists(data_path) and grid_level in [1,2,3]")
        print(os.path.exists(sh_path) , os.path.exists(data_path) , grid_level in [1,2,3])
