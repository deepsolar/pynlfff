
import pandas as pd
import os
import shutil


from prepare_base import PrepareWorker

import multiprocessing
import pandas as pd
import sys


### demo test ###
def demo_fun_use_Bptr(p_raw_path,t_raw_path,r_raw_path,sroot):
    # config
    # p_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bp.fits"
    # t_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bt.fits"
    # r_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Br.fits"
    # sroot=r"/public1/home/sc81826/temp/out"
    # create object
    os.makedirs(sroot,exist_ok=True)
    shutil.copyfile(p_raw_path,sroot+"/Bp.fits")
    shutil.copyfile(r_raw_path,sroot+"/Br.fits")
    shutil.copyfile(t_raw_path,sroot+"/Bt.fits")
    pre_worker = PrepareWorker()
    # pre
    pre_worker.prepare_from_fits_Bprt(p_raw_path,t_raw_path,r_raw_path,sroot)
    # print("finish demo_fun_use_Bptr_local")



def deal_one(sample):

    bp=job_root+sample["bp"]
    bt=job_root+sample["bt"]
    br=job_root+sample["br"]
    HARP_NUM=sample["HARP_NUM"]
    HARPNUM_TREC=sample["HARPNUM_TREC"]
    save_p=os.path.join(save_root,str(HARP_NUM),"hmi.sharp_cea_720s.{}".format(HARPNUM_TREC))
    demo_fun_use_Bptr(p_raw_path=bp,t_raw_path=bt,r_raw_path=br,sroot=save_p)




# 假设这是你的任务处理函数
# def deal_one(sample):
#     # 处理任务的代码
#     pass

# # 假设这是你的任务列表
# jobscsv = pd.DataFrame(...)  # 假设这里是你的任务数据

# 定义处理任务的函数
def process_job(jobid):
    sample = jobscsv.loc[jobid]
    try:
        deal_one(sample)
        return jobid, True  # 处理成功
    except Exception as e:
        print(f"Error processing job {jobid}: {e}")
        return jobid, False  # 处理失败

if __name__ == "__main__":
    
    job_path="/home/bingxing2/home/scx6069/zzr/data/nlfff_append/run1/nlfff_need_append_202404160610.csv"
    # /home/bingxing2/home/scx6069/zzr/data/nlfff_append/run2
    
    # i=4
    
    # 脚本名称是 sys.argv[0]
    i = sys.argv[1]

    print(i)
    job_path=job_path+f'.part_{i}.csv'
    
    job_root="/home/bingxing2/home/scx6069/zzr/data/nlfff_append/content/jsoc1.stanford.edu"
    save_root="/home/bingxing2/home/scx6069/zzr/data/nlfff_append/product"
    jobscsv=pd.read_csv(job_path)

    this_id_list = list(range(len(jobscsv)))
    pool = multiprocessing.Pool(processes=100)  # 创建进程池，最多同时运行100个进程
    results = pool.map(process_job, this_id_list)  # 并发处理任务列表
    pool.close()
    pool.join()

    # 处理处理成功和失败的任务
    success = [jobid for jobid, status in results if status]
    failure = [jobid for jobid, status in results if not status]
    with open(job_path+"s.log","w+") as f:
        f.write(str(success))
    with open(job_path+"f.log","w+") as f:
        f.write(str(failure))

    print(f"Successfully processed {len(success)} jobs.")
    print(f"Failed to process {len(failure)} jobs.")

