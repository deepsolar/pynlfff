
import pandas as pd
import os
import shutil
import sys
import time
import re

job_root="/home/bingxing2/home/scx6069/zzr/data/nlfff_append/product"
# /home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/run/runone.sh /home/bingxing2/home/scx6069/zzr/nlfff/product/demo_01 1
runonesh="/home/bingxing2/home/scx6069/zzr/pynlfff/pynlfff/cnlfff/wiegelmann_nlfff/run/runone.sh"


def get_size_from_grid(grid_path):
    """
    get size from grid, which is just read grid.ini and re
    :param grid_path:
    :return: list like [nx, ny, nz] or read fail is False
    """
    result = False
    with open(grid_path, "r") as f:
        l = f.read()
        l = re.split('[\n|\t]', l)
        l = list(filter(None, l))
        if len(l) >= 6:
            nx = int(l[1])
            ny = int(l[3])
            nz = int(l[5])
            result = [nx, ny, nz]
    # print(result)
    return result
    

def quality_is_ok(file_path):
    """Check whether the file degree angle is greater than 30, 
    greater than 30, or the file is empty, return False, 
    otherwise True, to ensure that the file exists

    Args:
        file_path ([type]): [description]

    Returns:
        [type]: [description]
    """
    if not os.path.exists(file_path):
        result = False
    else:
        with open(file_path, 'r')as f:
            file_data = f.read()
        # print(file_data)
        pattern = r'Angle.*?Degree'  # Pattern String
        string = file_data  # String to match
        match = re.findall(pattern, string)
        # print(match)
        p = r'\d+\.?\d+'
        nums = re.findall(p, str(match))
        if len(nums) == 0:
            result = False
        else:
            result = True
            result_num=91
            for num in nums:
                if float(num) > 30:
                    result_n = False
                else:
                    result_n = True
                result = result and result_n
                result_num=num
        result = [result,result_num]
    return result


def run_sh(job_p,cudai):
    try:
        # cmd = "/usr/bin/taskset -c {0} {1} {2}  {3} >> {4} ".format(cpus_use, run_sh, work_path, level, log_path)
        log_path=os.path.join(job_p,"run.log")
        grid=1
        cmd = "{0} {1} {2} {3} >> {4} ".format(runonesh, job_p, cudai,grid, log_path)

        returncode = os.system(cmd)  # TAG  subprocess.Popen Will block

        if returncode == 0:
            # pass
            run_result1 = "need check now"
            q_f = os.path.join(job_p, "NLFFFquality{}.log".format(1))
            if os.path.exists(q_f):
                run_result1 = quality_is_ok(q_f)
                run_result1 = "q:{}".format(run_result1)
            # else:
            #     self.run_job_qfail_remove(job)
            #     run_result = False
            run_result=[True,run_result1]
        else:
            print("{}{}".format(cmd, returncode))
            # print(returncode)
            run_result = [False,"returncode not 0"]
    except BaseException as e:
        print("{}{}".format(job_p, e))
        # print()
        run_result = [False,str(e)]
    return run_result

    
    
    
def do_one(job_p,cudai,runlog):
    try:
        if os.path.exists(runlog):
            with open(runlog,"r") as f:
                alldone=f.read().split("\n")
        else:
            alldone=[]
    except BaseException as e:
        print(e)
        alldone=[]
    if job_p in alldone:
        return [True,"finish before"]
    
    run_result=run_sh(job_p,cudai)
    
    if run_result[0] is True:
        with open(runlog,"a+") as f:
            f.write("{}\n".format(job_p))
    return run_result
    
    

def deal_one(sample,cudai,runlog):

    # bp=job_root+sample["bp"]
    # bt=job_root+sample["bt"]
    # br=job_root+sample["br"]
    HARP_NUM=sample["HARP_NUM"]
    HARPNUM_TREC=sample["HARPNUM_TREC"]
    job_p=os.path.join(job_root,str(HARP_NUM),"hmi.sharp_cea_720s.{}".format(HARPNUM_TREC))
    try:
        result = do_one(job_p,cudai,runlog)
        # result=[True,HARPNUM_TREC]
    except BaseException as e:
        print(e)
        result=[False,"{},{}".format(HARPNUM_TREC,str(e))]
    return result





if __name__ == "__main__":
    
    job_path="/home/bingxing2/home/scx6069/zzr/data/nlfff_append/run2/nlfff_need_append_202404160610.csv"
    
    # jobi=4
    jobi = sys.argv[1]
    # cudai 0 1 2 3
    cudai=sys.argv[2]

    print(jobi)
    job_path=job_path+f'.part_{jobi}.csv'
    
    jobscsv=pd.read_csv(job_path)

    this_id_list = list(range(len(jobscsv)))
    
    with open(job_path+"run.flag","a+") as f:
        f.write("{}\n".format(time.time()))
    
    runlog=job_path+"run.log"
    test=5
    for jobid in this_id_list:
        sample = jobscsv.loc[jobid]
        result=deal_one(sample,cudai,runlog)
        HARPNUM_TREC=sample["HARPNUM_TREC"]
        print("{};{}\n".format(HARPNUM_TREC,result))
        if result[0] is True:
            with open(job_path+"s.log","a+") as f:
                f.write("{};{}\n".format(HARPNUM_TREC,result))
        else:
            with open(job_path+"f.log","a+") as f:
                f.write("{};{}\n".format(HARPNUM_TREC,result))
        
        if not os.path.exists(job_path+"run.flag"):
            
            while os.path.exists(job_path+"run.flag.wait"):
                print("wait\n")
                time.sleep(20)
            if not os.path.exists(job_path+"run.flag"):
                print("stop")
                break
        
        # test-=1
        # if test<=0:
        
        #     break
    
    
    print("end")
    # print(f"Successfully processed {len(success)} jobs.")
    # print(f"Failed to process {len(failure)} jobs.")


