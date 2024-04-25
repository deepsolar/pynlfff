
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
    if not os.path.exists(grid_path):
        return result
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
        result_num=92
        # 缺失
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
        # 异常角度
        result_num=91
        if len(nums) == 0:
            result = False
        else:
            result = True
            for num in nums:
                try:
                    num=float(num)
                except BaseException as e:
                    print(e)
                    print(num)
                if num > 30:
                    result_n = False
                else:
                    result_n = True
                result = result and result_n
                result_num=num
    result = [result,result_num]
    return result


def run_sh(job_p,cudai,runlog):
    finall_run_result=[True,]
    try:
        runlog_csv=runlog+".archive.csv"
        # cmd = "/usr/bin/taskset -c {0} {1} {2}  {3} >> {4} ".format(cpus_use, run_sh, work_path, level, log_path)
        log_path=os.path.join(job_p,"run.log")
        grid_list=[1,2,3]
        for grid in grid_list:
            nxyz=get_size_from_grid(os.path.join(job_p,"grid{}.ini".format(grid)))
            if nxyz is False:# or nxyz[0]*nxyz[1]*nxyz[2]>1200*480*630:
                continue
            
            if os.path.exists(os.path.join(job_p,"done{}.txt".format(grid))):
                q_f = os.path.join(job_p, "NLFFFquality{}.log".format(grid))
                if os.path.exists(q_f):
                    qflag_result_list = quality_is_ok(q_f)
                    
                with open(runlog_csv,"a+") as f:
                    logthis="{},{},{},{},{},{},{}\n".format(
                        job_p,
                        grid,
                        nxyz[0],
                        nxyz[1],
                        nxyz[2],
                        qflag_result_list[0],
                        qflag_result_list[1],
                    )
                    f.write(logthis)
                continue
            
            # max_now=1200*480*630
            # max_now=1024*408*536
            max_now=800*320*420
            if nxyz[0]*nxyz[1]*nxyz[2]>max_now and grid >1:
                continue
            
            
            cmd = "{0} {1} {2} {3} >> {4} ".format(runonesh, job_p, cudai,grid, log_path)

            returncode = os.system(cmd)  # TAG  subprocess.Popen Will block

            if returncode == 0:
                # pass
                run_result_str = "need check now"
                q_f = os.path.join(job_p, "NLFFFquality{}.log".format(1))
                if os.path.exists(q_f):
                    qflag_result_list = quality_is_ok(q_f)
                    run_result_str = "q:{}".format(qflag_result_list)
                    with open(runlog_csv,"a+") as f:
                        logthis="{},{},{},{},{},{},{}\n".format(
                            job_p,
                            grid,
                            nxyz[0],
                            nxyz[1],
                            nxyz[2],
                            qflag_result_list[0],
                            qflag_result_list[1],
                        )
                        f.write(logthis)
                    
                run_result=[grid,True,run_result_str]
            else:
                print("{}{}".format(cmd, returncode))
                # print(returncode)
                run_result = [grid,False,"returncode not 0"]
            finall_run_result.append(run_result)
            
            if not os.path.exists(runlog.replace("run.log", "run.flag")):
                time.sleep(20)
                while os.path.exists(runlog.replace("run.log", "run.flag.wait")):
                    print("wait\n")
                    time.sleep(20)
                if not os.path.exists(runlog.replace("run.log", "run.flag")):
                    print("stop")
                    break
            
    except BaseException as e:
        print("{}{}".format(job_p, e))
        # print()
        finall_run_result = [False,str(e)]
    return finall_run_result

    
    
    
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
    
    run_result=run_sh(job_p,cudai,runlog)
    
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
            time.sleep(20)
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


