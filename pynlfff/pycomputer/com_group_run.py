# coding=utf-8
# 固定进程占用固定核心，任务队列在更新
import os
import sys
import multiprocessing
import psutil
import time
import re
from multiprocessing import managers
import socket


# import fcntl
# from multiprocessing.managers import BaseManager
# from multiprocessing import Manager

def quality_is_ok(file_path):
    """检测文件degree角度是否大于30，大于30或者文件为空则返回False，否则为True，要保证文件存在

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
        pattern = r'Angle.*?Degree'  # 模式字符串
        string = file_data  # 要匹配的字符串
        match = re.findall(pattern, string)
        # print(match)
        p = r'\d+\.?\d+'
        nums = re.findall(p, str(match))
        if len(nums) == 0:
            result = False
        else:
            result = True
            for num in nums:
                if float(num) > 30:
                    result_n = False
                else:
                    result_n = True
                result = result and result_n
    return result


class QueueManager(managers.BaseManager):

    def __init__(self, model="client", server_config_path="config.ini",server_port=5019):

        self.model = model  # "server" "client"
        if self.model == "server":
            self.init_server_queue()
        self.config_path = server_config_path
        self.this_address = None
        self.port = server_port
        self.get_address()
        # address=('127.0.0.1', 5000), authkey=b'abc', serializer='pickle',ctx=None
        authkey = None
        # authkey=b'\xb5Z\xa5\x08)\xfa\xbf\xfd\xdc\xf8`\x9b\x99\x99\x91-_\x1a\xe8vI\r\x8f\xd4=\r\xb2\x00\x07\x98n!'
        # authkey = b'\xc9\xd8\xb4\xb7\xc54.\x95\xcf\x08\xc3\x93&\xa6\xfb_<\x9fdl\\\xcc\xba\xe1\x0f\xb1U~\xcbF\xcbl'# None #b'i\xe4\xbf\\W\x18\xf8\x12\xba\xbd@!Y\xd1\xf0\x00\xdd\x92\x8f\xe1\x175\xd8\xfe$\xc4\\1\xc5<\x83\x07' #None #b'010'
        authkey = b"1001"
        serializer = 'pickle'
        ctx = None
        print(self.this_address)
        super().__init__(address=self.this_address, authkey=authkey, serializer=serializer, ctx=ctx)

        self.start_run()

    def init_server_queue(self):
        # 发送任务队列
        manager = multiprocessing.Manager()
        # 父进程创建Queue，并传给各个子进程：
        self.queue_todo1 = manager.Queue()
        # 12需要做的任务队列
        self.queue_todo2 = manager.Queue()
        self.queue_todo3 = manager.Queue()
        self.queue_todo4 = manager.Queue()

    def get_address(self):
        if self.model == "server":
            self.get_address_server()
        elif self.model == "client":
            self.get_address_client()

    def get_address_server(self):
        address_ip = "127.0.0.1"
        try:
            address_ip = socket.gethostbyname(socket.gethostname())
        except BaseException as e:
            print(e)
        self.this_address = (str(address_ip), self.port)
        # if os.path.exists(self.config_path):
        with open(self.config_path, "w+") as f:
            f.write(address_ip)

    def get_address_client(self):
        address_ip = "127.0.0.1"
        if os.path.exists(self.config_path):
            with open(self.config_path, "r+") as f:
                address_ip = f.read()
        self.this_address = (str(address_ip), self.port)

    def start_run(self):
        if self.model == "server":
            self.start_run_server()
        elif self.model == "client":
            self.start_run_client()

    # @staticmethod
    def return_queue_todo1(self):
        # global 用于函数内部，修改全局变量的值
        # global queue_todo1
        return self.queue_todo1

    # @staticmethod
    def return_queue_todo2(self):
        # global 用于函数内部，修改全局变量的值
        # global queue_todo2
        return self.queue_todo2

    # @staticmethod
    def return_queue_todo3(self):
        # global 用于函数内部，修改全局变量的值
        # global queue_todo3
        return self.queue_todo3

    # @staticmethod
    def return_queue_todo4(self):
        # global 用于函数内部，修改全局变量的值
        # global queue_todo4
        return self.queue_todo4

    def start_run_server(self):
        # 将两个Queue注册到网络上，callable参数关联Queue对象
        # ！win10中callale不对lambda匿名函数做处理
        self.register('get_queue_todo1', callable=self.return_queue_todo1)
        self.register('get_queue_todo2', callable=self.return_queue_todo2)
        self.register('get_queue_todo3', callable=self.return_queue_todo3)
        self.register('get_queue_todo4', callable=self.return_queue_todo4)
        # 绑定端口5000，这5000怎么来的？两个文件中的端口一样就行！，设置验证码abc
        # 通过QueueManager将Queue暴露出去
        self.start()

    def start_run_client(self):
        self.register('get_queue_todo1')
        self.register('get_queue_todo2')
        self.register('get_queue_todo3')
        self.register('get_queue_todo4')
        self.connect()


class linff_sim():
    def __init__(self, root_path, shs, shp,mode="server"):
        self.root_path = root_path  # r"C:\Users\Zander\PycharmProjects\pythonProjec2t\raw_eg"
        self.root_path_q2sucess=os.path.join(self.root_path,"q2sucess")
        self.root_path_q3sucess=os.path.join(self.root_path,"q3sucess")

        if not os.path.exists(self.root_path_q2sucess):
            os.makedirs(self.root_path_q2sucess)
        if not os.path.exists(self.root_path_q3sucess):
            os.makedirs(self.root_path_q3sucess)
        self.job_1_fail = os.path.join(self.root_path, "fail1.txt")
        self.server_config = os.path.join(self.root_path, "server.txt")
        # os.remove("/home/zzr/project/linff/linff-main/deploy/save_dir/num_0000_0099/server.txt")
        if not os.path.exists(self.server_config):
            self.run_flag_file = os.path.join(self.root_path,
                                              "server_is_run.flag.{}.{}".format(socket.gethostname(), time.time()))
        else:
            self.run_flag_file = os.path.join(self.root_path,
                                              "worker_is_run.flag.{}.{}".format(socket.gethostname(), time.time()))
        print(self.run_flag_file)
        self.shp = shp
        self.shs = shs
        manager = multiprocessing.Manager()
        # 父进程创建Queue，并传给各个子进程：
        # q = manager.Queue()
        # 12需要做的任务队列
        # self.q12_job = multiprocessing.Queue()
        # self.cpu_list_free = manager.list()
        self.cpu_list_in_use = manager.list()
        # self.is_edit_job_lock = manager.Lock()
        self.is_get_cpu_lock = manager.Lock()
        self.lock_level_2 = manager.Value("i", 0)
        self.level_2_min = 3
        self.lock_level_3 = manager.Value("i", 0)
        self.level_3_min = 3
        # self.lock_level_3.value=4
        if mode=="server":
            self.with_server = True
        else:
            self.with_server = False
        self.init_job_queue()

    def init_job_queue(self):
        try:
            # try:
            #     self.server_print_status()
            # except BaseException as e:
            #     print(e)
            if not os.path.exists(self.server_config):# or self.with_server:
                self.with_server = True
                manager = QueueManager("server", self.server_config)  # address=('127.0.0.1', 5000), authkey=b'abc')
            else:
                manager = QueueManager("client", self.server_config)
            self.job_todo1_queue = manager.get_queue_todo1()
            self.job_todo2_queue = manager.get_queue_todo2()
            self.job_todo3_queue = manager.get_queue_todo3()
            self.job_todo4_queue = manager.get_queue_todo4()
            self.job_todon_queue_list = [self.job_todo1_queue, self.job_todo2_queue, self.job_todo3_queue,
                                         self.job_todo4_queue]
        except BaseException as e:
            print("init_job_queue error:")
            print(e)

    def server_distribute_job_queue(self, numb):
        self.job_1_todo = os.path.join(self.root_path, "todo1.txt")
        self.job_2_todo = os.path.join(self.root_path, "todo2.txt")
        self.job_3_todo = os.path.join(self.root_path, "todo3.txt")
        self.job_4_todo = os.path.join(self.root_path, "todo4.txt")
        self.job_n_todo = [self.job_1_todo, self.job_2_todo, self.job_3_todo, self.job_4_todo]
        self.__file_if_not_exist_creat_12(self.job_1_todo)
        self.__file_if_not_exist_creat(self.job_2_todo)
        self.__file_if_not_exist_creat(self.job_3_todo)
        self.__file_if_not_exist_creat(self.job_4_todo)
        while self.is_run_now():
            try:
                for i in range(3):
                    if os.path.exists(self.job_n_todo[i]):
                        with open(self.job_n_todo[i], "r+") as f:
                            # f.readlines()
                            this_lines = f.read().splitlines()
                        for job in this_lines:
                            if job.startswith("hmi"):
                                self.job_todon_queue_list[i].put(job)
                        # os.remove(self.job_n_todo[i])
                        os.rename(self.job_n_todo[i], "{}.{}".format(self.job_n_todo[i], time.time()))
                self.server_print_status()
            except BaseException as e:
                print(e)
                self.init_job_queue()
            time.sleep(10 * 60)

    def get_level_lock(self, level):
        if level == 2:
            self.lock_level_2.value = self.lock_level_2.value + 1
        if level == 3:
            self.lock_level_3.value = self.lock_level_3.value + 1

    def release_level_lock(self, level):
        if level == 2:
            self.lock_level_2.value = self.lock_level_2.value - 1
        if level == 3:
            self.lock_level_3.value = self.lock_level_3.value - 1

    def check_level_no_lock(self, level):
        """没有锁住返回真

        Args:
            level (_type_): _description_

        Returns:
            _type_: _description_
        """
        if level == 2:
            if self.lock_level_2.value == -1:  # 任务都完成
                return True
            elif self.lock_level_2.value > self.level_2_min:
                return True
            else:
                return False
        elif level == 3:
            if self.lock_level_3.value == -1:  # 任务都完成
                return True
            elif self.lock_level_3.value > self.level_3_min:
                return True
            else:
                return False

    def server_print_status(self):
        for i in range(4):
            joblist = []
            qz = int(self.job_todon_queue_list[i].qsize())
            for j in range(qz):
            #     # if not self.job_todon_queue_list[i].empty():
            #     #     job = self.job_todon_queue_list[i].get()
            #     #     joblist.append(job)
            #     #     self.job_todon_queue_list[i].put(job)
                try:
                    job = self.job_todon_queue_list[i].get_nowait()
                    joblist.append(job)
                    self.job_todon_queue_list[i].put(job)
                except BaseException as e:
                    print(e)

            f_path = "{}.status.{}".format(self.job_n_todo[i], time.time())
            with open(f_path, "w+") as f:
                f.write("{}\n{}".format(qz,joblist))

    def client_keep_job_queue(self, numb):
        if numb == 0:
            return False
        self.job_1_todo = os.path.join(self.root_path, "todo1.txt")
        self.job_2_todo = os.path.join(self.root_path, "todo2.txt")
        self.job_3_todo = os.path.join(self.root_path, "todo3.txt")
        self.job_4_todo = os.path.join(self.root_path, "todo4.txt")
        self.job_n_todo = [self.job_1_todo, self.job_2_todo, self.job_3_todo, self.job_4_todo]
        # self.__file_if_not_exist_creat_12(self.job_1_todo)
        # self.__file_if_not_exist_creat(self.job_2_todo)
        # self.__file_if_not_exist_creat(self.job_3_todo)
        # self.__file_if_not_exist_creat(self.job_4_todo)
        while self.is_run_now():
            try:
                for i in range(3):
                    if os.path.exists(self.job_n_todo[i]):
                        with open(self.job_n_todo[i], "r+") as f:
                            # f.readlines()
                            this_lines = f.read().splitlines()
                        for job in this_lines:
                            if job.startswith("hmi"):
                                self.job_todon_queue_list[i].put(job)
                        # os.remove(self.job_n_todo[i])
                        os.rename(self.job_n_todo[i], "{}.{}".format(self.job_n_todo[i], time.time()))
                self.server_print_status()
            except BaseException as e:
                print(e)
                self.init_job_queue()
            time.sleep(20 * 60 + 3)

    # 总控制
    def main_control(self):
        print("start control")
        with open(self.run_flag_file, "a+") as f:
            f.write(str(time.localtime()))
        # self.__file_if_not_exist_creat(self.run_flag_get_cpu)

        self.__file_if_not_exist_creat(self.job_1_fail)

        self.run_pool()
        return True

    def run_pool(self):
        print("star pool")
        r1 = 6
        r2 = 5
        r3 = 10
        rf = 0
        # work_num = 1 + r1 + r2 + r3 + rf  # self.singal_num_process + self.parallel_num_process
        # print(work_num)
        # 4 4 20
        # q=multiprocessing.Process(target=self.run_job_n, args=(1, 1,))
        # p = [0, 1]
        # p[0] = multiprocessing.Process(target=self.run_job_n, args=(1, 1,))
        # p[0].start()
        # p[0].join()
        # pool = multiprocessing.Pool(processes=work_num)
        # print(self.singal_cpu_list)
        if self.with_server:
            q = multiprocessing.Process(target=self.server_distribute_job_queue, args=(1,))
            # pool.apply_async(func=self.server_distribute_job_queue, args=(1,))
        else:
            # pool.apply_async(func=self.client_keep_job_queue, args=(1,))
            q = multiprocessing.Process(target=self.client_keep_job_queue, args=(0,))
        job = []
        for r3_num in range(r3):
            # pool.apply_async(func=self.run_job_n, args=(1, r1_num,))  # TAG (scpu_num,)逗号一定要有，否则不执行
            j = multiprocessing.Process(target=self.run_job_n, args=(3, r3_num,))
            job.append(j)
        for r1_num in range(r1):
            # pool.apply_async(func=self.run_job_n, args=(1, r1_num,))  # TAG (scpu_num,)逗号一定要有，否则不执行
            j = multiprocessing.Process(target=self.run_job_n, args=(1, r1_num,))
            job.append(j)
        for r2_num in range(r2):
            # pool.apply_async(func=self.run_job_n, args=(1, r1_num,))  # TAG (scpu_num,)逗号一定要有，否则不执行
            j = multiprocessing.Process(target=self.run_job_n, args=(2, r2_num,))
            job.append(j)

        # for r2_num in range(r2):
        #     pool.apply_async(func=self.run_job_n, args=(2, r2_num,))  # TAG (scpu_num,)逗号一定要有，否则不执行
        # for r3_num in range(r3):
        #     pool.apply_async(func=self.run_job_n, args=(3, r3_num,))  # TAG (scpu_num,)逗号一定要有，否则不执行
        for rf_num in range(rf):
            # pool.apply_async(func=self.run_job_free_fix, args=(rf_num + 1, rf_num,))
            j = multiprocessing.Process(target=self.run_job_free_fix, args=(1, rf_num,))
            job.append(j)
        # pool.close()
        # pool.join()
        q.start()
        for jq in job:
            jq.start()
        q.join()
        for jq in job:
            jq.join()

    def append_job_to_file(self, level, value):
        j = level - 1
        job = value
        try:
            self.job_todon_queue_list[j].put(job)
        except BaseException as e:
            print("appendjoberror")
            print(e)
            self.init_job_queue()
        print("job {}".format(job))
        return job

    def get_job(self, level, idn):
        j = level - 1
        job = None
        try:
            if idn > 6:
                if level == 1:
                    t1 = 0
                    while (not self.check_level_no_lock(2))  or t1 > 50:
                        time.sleep(5)
                        t1 = t1 + 1
                    t1 = 0
                    while (not self.check_level_no_lock(3))  or t1 > 50:
                        time.sleep(5)
                        t1 = t1 + 1
            if not self.job_todon_queue_list[j].empty():
                job = self.job_todon_queue_list[j].get()
            else:
                if level == 2:
                    self.lock_level_2.value = -1
                elif level == 3:
                    self.lock_level_3.value = -1
        except BaseException as e:
            print("getjoberror")
            print(e)
            self.init_job_queue()
        print("job {}".format(job))
        return job

    def run_job_n(self, level, id1):
        print("run job {}:{}\n".format(level, id1))

        while self.is_run_now():
            job = self.get_job(level, id1)
            if job is not None:
                # print("==========")
                need_cpu = self.get_need_cpu_num_by_grid(job, level)
                cpu_list = self.get_free_cpu_list(need_cpu)
                run_result = self.run_job_base(job, cpu_list, level)
                if run_result is "ing":
                    print("ing")
                elif run_result is True:
                    self.append_job_to_file(level + 1, job)
                    if level==2:
                        q2flagsucess=os.path.join(self.root_path_q2sucess,"{}.sucess".format(job))
                        with open(q2flagsucess,"w+") as f:
                            f.write("{}".format(time.time()))
                    elif level==3:
                        q3flagsucess=os.path.join(self.root_path_q3sucess,"{}.sucess".format(job))
                        with open(q3flagsucess,"w+") as f:
                            f.write("{}".format(time.time()))
                else:
                    self.append_job_to_file(1, job)
            else:
                time.sleep(5)

    def run_job_free_fix(self, level, idf):
        print("run job f:{}\n".format(idf))
        while self.is_run_now():
            this_level = level  # idf+1
            # done1 = "{}.done".format(self.job_1_todo)
            # if os.path.exists(done1):
            #     this_level = 2
            #     done2 = "{}.done".format(self.job_2_todo)
            #     if os.path.exists(done2):
            #         this_level = 3
            job = self.get_job(level, 0)
            if job is None:
                time.sleep(10)
                continue
            time.sleep(50)
            all_1 = self.get_free_cpu_list_base()
            time.sleep(50)
            all_2 = self.get_free_cpu_list_base()

            cpu_list = list((set(all_1) & set(all_2)) - set(self.cpu_list_in_use))
            if len(cpu_list) > 3:
                for cpu in cpu_list:
                    self.cpu_list_in_use.append(cpu)

                job = self.get_job(this_level, idf)
                run_result = self.run_job_base(job, cpu_list, this_level)
                if run_result is "ing":
                    print("ing")
                elif run_result is True:
                    self.append_job_to_file(this_level + 1, job)
                else:
                    self.append_job_to_file(1, job)

    def get_level(self,job):
        job_name_list = job.split(".")
        num = int(job_name_list[2])
        num_level_1 = num//1000
        num_level_2 = (num//100) % 10
        child_dir= "num_{}{}00_{}{}99".format(num_level_1, num_level_2, num_level_1, num_level_2)
        
        return child_dir

    def run_job_base(self, job, cpu_num_list, level):
        # print("run_job12_base")  level=123
        print("start run job: {}  use cpu: {}".format(job, cpu_num_list))
        self.get_level_lock(level)
        work_path = os.path.join(self.root_path,self.get_level(job), job)
        log_path = os.path.join(self.root_path,self.get_level(job), job, "run.log")
        ing_path = os.path.join(self.root_path,self.get_level(job), job, "ing.flag")
        # if level==1:
        #     done_path = os.path.join(self.root_path, job, "done1.txt")
        # elif level==2:
        #     done_path = os.path.join(self.root_path, job, "done2.txt")
        # else:
        #     done_path = os.path.join(self.root_path, job, "done.txt")
        # q2flagsucess = os.path.join(self.root_path_q2sucess, "{}.sucess".format(job))
        q3flagsucess = os.path.join(self.root_path_q3sucess, "{}.sucess".format(job))
        if os.path.exists(ing_path) or os.path.exists(q3flagsucess) or not os.path.exists(work_path):  # or os.path.exists(done_path):
            to_free_cpu = list(set(self.cpu_list_in_use) - set(cpu_num_list))
            for cpu in to_free_cpu:
                self.cpu_list_in_use.remove(cpu)
            return "ing"
        else:
            with open(ing_path, "w+") as f:
                f.write(str(time.localtime()))

        is_base_file = self.check_base_file_need(job)
        if not is_base_file:
            print("缺少文件")
            with open(self.job_1_fail, "a+") as f:
                f.write("{}\n".format(job))
            return "ing"
        if level==1:
            self.run_job_qfail_remove(job)
        if len(cpu_num_list) == 1:
            cpus_use = str(cpu_num_list[0])
            run_sh = self.shs
        elif len(cpu_num_list) > 1:
            cpus_use = ""
            for c in cpu_num_list:
                cpus_use = cpus_use + "{},".format(c)
            cpus_use = cpus_use[:-1]
            run_sh = self.shp
        else:
            run_result = False
            return run_result

        try:
            cmd = "/usr/bin/taskset -c {0} {1} {2}  {3} >> {4} ".format(cpus_use, run_sh, work_path, level, log_path)
            returncode = os.system(cmd)  # TAG  subprocess.Popen会阻塞

            if returncode == 0:
                # run_result = True
                q_f = os.path.join(work_path, "NLFFFquality{}.log".format(level))
                if os.path.exists(q_f):
                    run_result = quality_is_ok(q_f)
                else:
                    self.run_job_qfail_remove(job)
                    run_result = False

            else:
                print("{}{}".format(cmd, returncode))
                # print(returncode)
                run_result = False
        except BaseException as e:
            print("{}{}".format(job, e))
            # print()
            run_result = False

        to_free_cpu = list(set(self.cpu_list_in_use) - set(cpu_num_list))
        for cpu in to_free_cpu:
            self.cpu_list_in_use.remove(cpu)

        if os.path.exists(ing_path):
            os.remove(ing_path)
        self.release_level_lock(level)
        return run_result

    def check_base_file_need(self, job):
        r_path = os.path.join(self.root_path,self.get_level(job), job)
        base_set = {"mask1.dat", "mask2.dat", "mask3.dat", "grid1.ini", "grid2.ini", "grid3.ini",
                    'allboundaries1.dat', 'allboundaries2.dat', 'allboundaries3.dat', 'boundary.ini'}
        this_set = set(os.listdir(r_path))
        if len(base_set - this_set) > 0:
            print(base_set - this_set)
            return False
        else:
            return True

    def run_job_qfail_remove(self, job):
        r_path = os.path.join(self.root_path,self.get_level(job), job)
        # with open(self.job_u_remove_sh, "a+") as f:
        #     f.write("rm -rf {}\n".format(r_path))
        try:
            p_list = ['Energy.log', 'grid2n2.ini', 'NLFFFquality.log',
                      'NLFFFquality3.log', 'step3.log', 'Bout.bin',
                      'Iteration_start.mark', 'prot2.log', 'NLFFFquality2.log',
                      'done1.txt', 'prot1.log', 'NLFFFquality1.log',
                      'prot3.log', 'zboundaries2n2.dat', 'done.txt', 'grid.ini',
                      'done2.txt', 'prot.log',
                      'step.log', 'step2.log', 'allboundaries.dat' , 'B0.bin',
                      'Iteration_stop.mark', 'mask.dat',
                      'step1.log'] #

            # os.path.
            for p in p_list:
                p_path = os.path.join(r_path, p)
                if os.path.exists(p_path):
                    os.remove(p_path)
            # shutil.rmtree(r_path)
        except BaseException as e:
            print("{} remove error {}\n".format(job, e))

    def get_need_cpu_num_by_grid(self, job, level):
        use_num = 1
        l_f = os.path.join(self.root_path,self.get_level(job), job, "grid{}.ini".format(level))
        if os.path.exists(l_f):
            with open(l_f, "r") as f:
                lines = f.readlines()
            if len(lines) == 10:
                xyz = int(lines[1]) * int(lines[3]) * int(lines[5])
                use_num = int(xyz / 1024 / 1024 / 5 / 4) + 1
                if use_num != 1:
                    use_num = use_num + 4
        return use_num

    def get_free_cpu_list(self, cpu_need_nums):

        cpu_free_all_list = self.get_free_cpu_list_base()
        while self.is_run_now() and len(cpu_free_all_list) - len(self.cpu_list_in_use) - cpu_need_nums < 0:
            print("cpu {}/{}".format(len(cpu_free_all_list), cpu_need_nums))
            time.sleep(20)
            cpu_free_all_list = self.get_free_cpu_list_base()
        cpu_list = list(set(cpu_free_all_list) - set(self.cpu_list_in_use))
        cpu_list = cpu_list[:cpu_need_nums]
        for cpu in cpu_list:
            self.cpu_list_in_use.append(cpu)
        return cpu_list

    def get_free_cpu_list_base(self):
        result_list = []
        # with open(self.run_flag_get_cpu, "r+") as f:
        #     fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 加锁
        self.is_get_cpu_lock.acquire()
        all_p = psutil.cpu_percent(interval=6, percpu=True)
        for i in range(len(all_p)):
            if all_p[i] < 10:
                result_list.append(i)
        self.is_get_cpu_lock.release()
        return result_list

    def is_run_now(self):
        if os.path.exists(self.run_flag_file):
            result = True
        else:
            result = False
        return result

    def __dir_if_not_exist_creat(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def __file_if_not_exist_creat(self, file_path):
        father_dir = os.path.dirname(file_path)
        self.__dir_if_not_exist_creat(father_dir)
        if not os.path.exists(file_path):
            with open(file_path, "w+") as f:
                f.write("")

    def __file_if_not_exist_creat_12(self, file_path):
        # os.remove(file_path)
        if not os.path.exists(file_path):
            self.__file_if_not_exist_creat(file_path)
            father_dir = os.path.dirname(file_path)
            file_list = os.listdir(father_dir)
            with open(file_path, "w+") as f:
                for dir_name in file_list:
                    if dir_name.startswith("hmi.sharp_cea_720s."):
                        f.write("{}\n".format(dir_name))


def get_config():
    if len(sys.argv) < 4:
        print("请输入3个参数：")
        result = None
    else:
        data_root = sys.argv[1]  # him文件夹父级根目录
        shs_path = sys.argv[2]  # sh单线程脚本路径
        shp_path = sys.argv[3]  # sh多线程脚本路径
        # single_percent = float(sys.argv[4])  # sh3脚本路径  single_percent = 0.3
        # parallel_num = int(sys.argv[5])  # sh3脚本路径  parallel_num = 10
        if os.path.exists(data_root) and os.path.exists(shs_path) and os.path.exists(shp_path):
            result = dict(data_root=data_root, shs_path=shs_path, shp_path=shp_path)
            # , single_percent=single_percent,
            #           parallel_num=parallel_num)
        else:
            print("输入参数有误")
            print(os.path.exists(data_root), os.path.exists(
                shs_path), os.path.exists(shp_path))
            result = None
    return result


def test():
    config_dict = dict()
    config_dict["data_root"] = r"/home/ma-user/work/project/pre_b2/num_0300_0399/"
    config_dict["shs_path"] = r"/home/ma-user/work/project/linff-sim/app_c/compiled.single/multigrid.sh"
    config_dict["shp_path"] = r"/home/ma-user/work/project/linff-sim/app_c/compiled.parallel/multigrid.sh"
    # config_dict["data_root"] = r"/home/zzr/project/linff/linff-main/deploy/save_dir/num_0000_0099"
    # config_dict["sh12_path"] = r"/home/zzr/project/linff/linff-sim/app_c/compiled.single/multigrid.sh"
    # config_dict["sh3_path"] = r"/home/zzr/project/linff/linff-sim/app_c/compiled.parallel/multigrid.sh"

    os.environ[
        "OMP_PROC_BIND"] = "true"  # https://support.huaweicloud.com/tngg-kunpenghpcs/kunpenghpcsolution_05_0025.html
    ls = linff_sim(root_path=config_dict["data_root"], shs=config_dict["shs_path"], shp=config_dict["shp_path"])
    ls.main_control()


if __name__ == "__main__":
    config_dict = get_config()
    if config_dict is not None:
        os.environ[
            "OMP_PROC_BIND"] = "true"  # https://support.huaweicloud.com/tngg-kunpenghpcs/kunpenghpcsolution_05_0025.html
        ls = linff_sim(root_path=config_dict["data_root"], shs=config_dict["shs_path"], shp=config_dict["shp_path"])
        ls.main_control()

    # test()

# python3 run.py dataroot sh2 sh3
