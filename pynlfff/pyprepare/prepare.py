# coding=utf-8
import subprocess
import sys
import os
import re
import shutil
import multiprocessing
from .prepare_base import PrepareWorker


# ------全局控制------------------------------------------------
def main_control():
    print("开始运行")
    config_dict = get_config()
    if config_dict:
        print(config_dict)
        data_root = config_dict["data_root"]
        # "/home/zzr/data/sharp_upload_1/num_0001_0999/num_0001_0099/datalist.txt"
        data_job_list_path = os.path.join(data_root, "datalist.txt")
        if os.path.exists(data_job_list_path):
            job_list = find_joblist_from_datalist(data_job_list_path)
        else:
            job_list = find_joblist_from_dir(data_root)
        print("job num {}".format(len(job_list)))
        # app_root = config_dict["clinff_root"]
        save_path = config_dict["save_root"]
        work_num = config_dict["work_num"]
        # runspace_root=config_dict["runspace_root"]
        # grid_level=config_dict["grid_level"]
        run_result = manager_mult_pro(data_root, job_list, save_path,work_num)
        print("运行结果{}".format(run_result))
    else:
        print("参数或配置出现错误")
    return True


# -------外部接口--------------------------------------------
# 获取主程序运行根目录和数据存储目录并返回


def get_config():
    if len(sys.argv) < 4:
        print("请输入6个参数：")
        result = False
    else:
        # clinff_root = sys.argv[1]  # c主程序根目录
        data_root = sys.argv[1]  # 数据根目录
        save_root = sys.argv[2]  # 文件保存根目录
        work_num = sys.argv[3]  # 同时运行任务，0所有核心全部用上 (0,1)所有核心的几分之几  >=1 用设置的核心  其他为1  

        # runspace_root = sys.argv[5]  # 运行空间，如果是obs，需要先拷贝运行空间再运算，再复制最终空间
        # grid_level=sys.argv[6] # 运行层级 0预处理  123层 4质量控制
        # if os.path.exists(data_root) and os.path.exists(save_root) :
        result = dict(data_root=data_root, save_root=save_root,work_num=work_num)
        # else:
        #     print("输入路径不存在")
        #     result = False
    return result


# ------总体控制-----------------------------------------
# 从根目录找到任务文件
# /home/zzr/data/sharp_upload_1/num_0001_0999/num_0001_0099/datalist.txt
def find_joblist_from_datalist(datalist_file_path):
    with open(datalist_file_path, "r") as f:  # 设置文件对象
        list_data = f.read()  # 可以是随便对文件的操作
    # print(list_data) # 一整个字符串类型
    # print(re.split(r'Br.fits\n|Bt.fits\n|Bp.fits\n', list_data))
    three_list = re.split(r'.Br.fits\n|.Bt.fits\n|.Bp.fits\n', list_data)
    one_list = sorted(list(set(three_list)))  # 去重+排序
    print(one_list)
    job_list = one_list
    return job_list


def find_joblist_from_dir(data_root):
    file_list = os.listdir(data_root)
    new_list = list()
    for f_name in file_list:
        a1 = f_name.replace(".Bt.fits", "")
        a2 = a1.replace(".Bp.fits", "")
        a3 = a2.replace(".Br.fits", "")
        new_list.append(a3)
    one_list = sorted(list(set(new_list)))  # 去重+排序
    print(one_list)
    return one_list  # ['hmi.sharp_cea_720s.998.20111027_093600_TAI.']


# 创建多线程生成任务
def manager_mult_pro(data_root, job_list, save_path,work_num):
    # "/home/zzr/project/linff/linff-main/deploy/space/log"
    log_path = os.path.join(save_path, "todo0.log.txt")
    work_num = get_work_num(work_num)
    with open(log_path, 'a+') as f:
        job_len = len(job_list)
        line = "============================================================\n{}\n{}\nwork_num:{}\n".format(job_list,job_len,work_num)
        f.write(line)
        
    pool = multiprocessing.Pool(processes=work_num)
    for job in job_list:
        pool.apply_async(func=manager_one_job, args=(
            data_root, job,save_path), callback=setcallback_write_log)
    pool.close()
    pool.join()
    print("全部运行结束")
    return True

# 同时运行任务，0所有核心全部用上 (0,1)所有核心的几分之几  >=1 用设置的核心  其他为1 
def get_work_num(work_num):
    # from multiprocessing import cpu_count
    # print("CPU的核数为：{}".format(multiprocessing.cpu_count()))
    # print(type(cpu_count()))
    work_num=float(work_num)
    if work_num >=1:
        real_work_num=int(work_num)
    elif (0 < work_num and work_num < 1):
        all_cpu=multiprocessing.cpu_count()
        real_work_num=int(all_cpu*work_num)
    elif work_num == 0:
        all_cpu=multiprocessing.cpu_count()
        real_work_num = int(all_cpu-1)
    else:
        real_work_num = 1
    return real_work_num


# 任务结束写日志
# 设置回调函数
def setcallback_write_log(x):
    log_path = x[2]
    with open(log_path, 'a+') as f:
        line = str(x[0]) + str(x[1]) + "\n"
        f.write(line)
    with open(log_path.replace("todo0.log.txt","todo1.txt"), 'a+') as f:
        line = str(x[0]) + "\n"
        f.write(line)

# def quality_is_ok(file_path):
#     """检测文件degree角度是否大于30，大于30或者文件为空则返回False，否则为True，要保证文件存在

#     Args:
#         file_path ([type]): [description]

#     Returns:
#         [type]: [description]
#     """
#     with open(file_path, 'r')as f:
#         file_data = f.read()
#     # print(file_data)
#     pattern = r'Angle.*?Degree'  # 模式字符串
#     string = file_data  #要匹配的字符串
#     match = re.findall(pattern,string)
#     # print(match)
#     p = r'\d+\.?\d+'
#     nums = re.findall(p,str(match))
#     if len(nums) == 0:
#         result=False
#     else:
#         result = True
#         for num in nums:
#             if float(num) > 30:
#                 result_n = False
#             else:
#                 result_n = True
#             result = result and result_n
#     return result

# ------局部具体任务-----------------------------------------
# 单个任务控制者
def manager_one_job(data_root, job, save_path):
    # grid_level=str(grid_level)
    # num_quality = run_one_quality(job,save_path)
    # if "4" in grid_level:  # 质量控制
    #     num_quality = run_one_quality(job,save_path)
    # if "0" in grid_level:  # 预处理
    result = run_one_0(data_root, job,save_path)
    # if "1" in grid_level or "2" in grid_level or "3" in grid_level: # 计算
    #     result = run_one_123(data_root, job, app_root, save_path,runspace_root,grid_level)
    
    
    # "/home/zzr/project/linff/linff-main/deploy/space/log"
    log_path = os.path.join(save_path, "todo0.log.txt")
    result = [job, result, log_path]

    return result  # ,log_path
    # return job,result

# def run_one_quality(job, save_path):
#     """检测该任务质量是否通过
#     3质量3通过
#     2质量2通过，且没有质量3
#     1质量1通过且没有质量23
#     4没有质量文件,
#     5没有质量文件，但是有pre文件
#     False质量未通过删除文件夹

#     Returns:
#         [type]: [description]
#     """
#     job_name_list = job.split(".")
#     num = int(job_name_list[2])
#     num_level_1 = num//1000
#     num_level_2 = (num//100) % 10
#     this_dir = "num_{}{}00_{}{}99".format(
#         num_level_1, num_level_2, num_level_1, num_level_2)
#     job_save_path = os.path.join(save_path, this_dir, job)
#     p_jq3 = os.path.join(job_save_path,"NLFFFquality3.log")
#     p_jq2 = os.path.join(job_save_path,"NLFFFquality2.log")
#     p_jq1 = os.path.join(job_save_path,"NLFFFquality1.log")

#     if os.path.exists(p_jq3):
#         q3=quality_is_ok(p_jq3)
#         if q3:
#             result=3
#         else:
#             shutil.rmtree(job_save_path)
#             result=False
#     elif os.path.exists(p_jq2):
#         q2=quality_is_ok(p_jq2)
#         if q2:
#             result=2
#         else:
#             shutil.rmtree(job_save_path)
#             result=False
#     elif os.path.exists(p_jq1):
#         q1=quality_is_ok(p_jq1)
#         if q1:
#             result=1
#         else:
#             shutil.rmtree(job_save_path)
#             result=False
#     # elif check_have_pre(job, save_path):
#     #     result = 5
#     else:
#         shutil.rmtree(job_save_path)
#         result = 4 
#     return result

# # def check_have_pre(job,save_path):
    
#     return True

def run_one_0(data_root, job,save_path):
    print("0")
    # num_quality = run_one_quality(job,save_path)
    # if num_quality is False or num_quality == 4:
    job_save_path = make_job_workspace_dir(job,save_path)
    run_one_pre_result = run_one_pre(data_root, job, job_save_path)
    # job_save_path_remote = make_job_workspace_dir(job, save_path)
    # result = run_move_to_remote(run_one_pre_result,job_save_path_remote)
    # else:
    # result = True
    return run_one_pre_result


# def run_one_123(data_root, job, app_root, save_path,runspace_root,grid_level):
#     print("123") # 跑123 前面必须有跑过0
#     remote_job_save_path = make_job_workspace_dir(job, save_path)
#     remote_done_flag_file = os.path.join(remote_job_save_path, "done.txt")
#     if os.path.exists(remote_done_flag_file):
#         result = True
#     else:
#         job_save_path = make_job_workspace_dir(job, runspace_root)
#         com_c_path = os.path.join(app_root, "multigrid.sh")
#         com_c_exist = os.path.isfile(com_c_path)
#         if  com_c_exist:
#             result = run_one_comp(app_path=com_c_path, work_path=job_save_path,grid_level=grid_level)
#         else:
#             result = False
#             error_msg = "{} :运行脚本不存在或运行失败\n".format(job)
#             print(error_msg)
#             err_path = os.path.join(save_path, "run_err_log.txt")
#             with open(err_path, "a+") as f:
#                 f.write("{}:{}".format(job, error_msg))
#         if result:
#             result = run_one_clean(job_save_path)
#             if result:
#                 result = run_move_to_remote(job_save_path,remote_job_save_path)


def run_move_to_remote(from_dir,to_dir):
    # shutil.move("oldpos","newpos")
    try:
        if os.path.normcase(from_dir) == os.path.normcase(to_dir):
            result = True
        else:
            shutil.rmtree(to_dir)
            shutil.move(from_dir,to_dir)
            result = True
    except BaseException as e:
        print(e)
        result = False
    return result


# 根据任务文件生成文件夹和pre预处理
def run_one_pre(data_root, job, job_save_path):
    p_raw_path = os.path.join(data_root, job+".Bp.fits")
    t_raw_path = os.path.join(data_root, job+".Bt.fits")
    r_raw_path = os.path.join(data_root, job+".Br.fits")
    # print(p_raw_path)
    # print(os.path.isfile(p_raw_path))
    if os.path.isfile(p_raw_path) and os.path.isfile(t_raw_path) and os.path.isfile(r_raw_path):

        # job_save_path=make_job_workspace_dir(job,save_path)
        # print(job_save_path)
        try:
            pre_worker = PrepareWorker()
            pre_result = pre_worker.prepare_from_fits_Bprt(
                p_raw_path, t_raw_path, r_raw_path, job_save_path)
            result = pre_result
        except BaseException as e:
            error_msg = "{}预处理失败：{}".format(job, e)
            print(error_msg)
            err_path = os.path.join(job_save_path, "todo0.err.log.txt")
            with open(err_path, "a+") as f:
                f.write(error_msg)
            result = False
    return result


def make_job_workspace_dir(job, save_path):
    job_name_list = job.split(".")
    num = int(job_name_list[2])
    num_level_1 = num//1000
    num_level_2 = (num//100) % 10
    this_dir = "num_{}{}00_{}{}99".format(
        num_level_1, num_level_2, num_level_1, num_level_2)
    job_save_path = os.path.join(save_path, this_dir, job)
    if not os.path.exists(job_save_path):
        try:
            run_result = os.makedirs(job_save_path)
            if run_result is None:
                result = job_save_path
        except BaseException as e:
            error_msg = "{} ERROR: {}".format(job, e)
            print(error_msg)
            err_path = os.path.join(save_path, "todo0.err.log.txt")
            with open(err_path, "a+") as f:
                f.write("{}:{}".format(job, error_msg))
            result = False
    else:
        result = job_save_path
    return result

# 进入预处理执行主程序


# def run_one_comp(app_path, work_path, grid_level):
#     # app_path=app_path  # "/home/zzr/project/linff/linff-main/clinff/multigrid.sh"
#     # work_path=work_path #"/home/zzr/project/linff/temp/py2/a6"
#     # cmd_str="{} {}".format(app_path,work_path)
#     # # cmd_str="sssssss"
#     # cmd_tmp_log = subprocess.run([app_path,work_path],stdout=PIPE,stderr=STDOUT,) # https://blog.csdn.net/daduryi/article/details/81299999
#     # print(cmd_tmp_log)
#     # app_path="ls"
#     run_result = False
#     print("start run {}".format(work_path))
#     log_path = os.path.join(work_path, "run.log")
#     with open(log_path, 'w') as f:
#         # https://blog.csdn.net/daduryi/article/details/81299999
#         cmd_proc = subprocess.run(
#             [app_path, work_path,grid_level], stdout=f, stderr=subprocess.STDOUT)
#         # f.write(cmd_tmp_log.read()) # https://zhuanlan.zhihu.com/p/117495961
#         if cmd_proc.returncode == 0:
#             run_result = True
#     print("end run {}".format(work_path))
#     return run_result


# # 删除其他文件
# def run_one_clean(work_path):
#     return True  # 先不删除
#     remove_datalist = ["B0.bin"]
#     try:
#         for rm_file in remove_datalist:
#             rm_path = os.path.join(work_path, rm_file)
#             if os.path.isfile(rm_path):
#                 os.remove(rm_path)
#         result = True
#     except BaseException as e:
#         print("{} ERROR {} ".format(work_path, e))
#         result = False
#     return result


# -------主运行部分------------------------------------------
if __name__ == "__main__":
    main_control()
