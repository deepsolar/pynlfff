import os
import re


def write_set_to_path(raw_set,raw_path,need_root=False):
    for i in raw_set:
        if not need_root:
            i=i.split("/")[-1]
        with open(raw_path,"a+") as f:
            f.write(str(i)+"\n")


def check_quality_from_log(file_path):
    """
    Detect whether the file degree angle is greater than 30,
    greater than 30 or the file is empty, return False,
    otherwise True
    :param file_path: NLFFFquality3.log path
    :return:
    """
    result = False
    if os.path.exists(file_path):
        with open(file_path, 'r')as f:
            file_data = f.read()
        # print(file_data)
        pattern = r'Angle.*?Degree'
        match = re.findall(pattern, file_data)
        # print(match)
        p = r'\d+\.?\d+'
        nums = re.findall(p, str(match))
        if len(nums) == 0:
            result = False
        else:
            result = True
            for num in nums:
                if float(num) > 30.0:
                    result_n = False
                else:
                    result_n = True
                result = result and result_n  # ensure every value is ok
    return result





def clean_to_one_step(raw_path):
    init_set=set(['allboundaries3.dat', 'allboundaries1.dat', 'grid3.ini', 'boundary.ini', 'mask2.dat', 'mask3.dat', 'grid2.ini', 'grid1.ini', 'mask1.dat', 'allboundaries2.dat','run.log'])
    dict_set=set(next(os.walk(raw_path))[2])
    rmf=dict_set-init_set
    result=[]
    for rmo in rmf:
        rp=os.path.join(raw_path,rmo)
        if os.path.isfile(rp):
            # print(rp)
            result.append(rp)
    return result
            
# clean_to_one("/home/ma-user/work/pro/num_1800_1899/hmi.sharp_cea_720s.1834.20120708_044800_TAI")


def run_root_path(path_root,log_root,clean_to_one=False):
    # path_root="/home/ma-user/work/pro/archive-202209/grid2.done"
    todo1=os.path.join(log_root,"todo1.txt")
    todo2=os.path.join(log_root,"todo2.txt")
    todo3=os.path.join(log_root,"todo3.txt")
    done3=os.path.join(log_root,"done3.txt")
    clean1=os.path.join(log_root,"clean1.txt")
    cleanp=os.path.join(log_root,"clean1.sh")
    all_l=os.walk(path_root)

    set_1_todo=set()
    set_2_todo=set()
    set_3_todo=set()
    clean_to_1_todo=set()
    set_3_done=set()


    for one_l in all_l:
        this_path=one_l[0]
        this_file_list=one_l[2]
        this_file_count=len(this_file_list)
        if this_file_count>10:
            # print(one_l)
            # pass
            if "NLFFFquality3.log" in this_file_list:
                if check_quality_from_log(os.path.join(this_path,"NLFFFquality3.log")):
                    set_3_done.add(this_path)
                else:
                    clean_to_1_todo.add(this_path)
            elif "NLFFFquality2.log" in this_file_list:
                if check_quality_from_log(os.path.join(this_path,"NLFFFquality2.log")):
                    if "grid.ini" in this_file_list:
                        if os.path.getmtime(os.path.join(this_path,"grid.ini"))<os.path.getmtime(os.path.join(this_path,"NLFFFquality2.log")):
                            set_3_todo.add(this_path)
                        else:
                            clean_to_1_todo.add(this_path)
                    else:
                        clean_to_1_todo.add(this_path)
                else:
                    clean_to_1_todo.add(this_path)
            elif "NLFFFquality1.log" in this_file_list:
                if check_quality_from_log(os.path.join(this_path,"NLFFFquality1.log")):
                    if "grid.ini" in this_file_list:
                        if os.path.getmtime(os.path.join(this_path,"grid.ini"))<os.path.getmtime(os.path.join(this_path,"NLFFFquality1.log")):
                            set_2_todo.add(this_path)
                        else:
                            clean_to_1_todo.add(this_path)
                    else:
                        clean_to_1_todo.add(this_path)
                else:
                    clean_to_1_todo.add(this_path) 
            else:
                clean_to_1_todo.add(this_path) 

        elif this_file_count==10 and "grid3.ini" in this_file_list:
            # print(one_l)
            set_1_todo.add(this_path)
    clean_sh=set()
    if clean_to_one:
        
        for job in clean_to_1_todo:
            c_result = clean_to_one_step(job)
            # for c in c_result:
            clean_sh= clean_sh | set(c_result)


    
    write_set_to_path(set_1_todo,todo1)
    write_set_to_path(clean_to_1_todo,clean1)
    write_set_to_path(set_2_todo,todo2)
    write_set_to_path(set_3_todo,todo3)
    write_set_to_path(set_3_done,done3,True)
    write_set_to_path(clean_sh,cleanp,True)

if __name__=="__main__":
    run_root_path(
        "/home/ma-user/work/pro/archive-202209/grid2.done",
        "/home/ma-user/work/pro/log/new",
        True
    )


