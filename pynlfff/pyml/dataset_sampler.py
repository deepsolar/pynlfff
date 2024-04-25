import os
import random
import time

from torch.utils.data import Sampler


class ResamplingSampler(Sampler):
    def __init__(self,
                 pos_index,
                 neg_index,
                 pos_weight=None,
                 neg_weight=None,
                 random_use_fun='balance|on_all',
                 random_use_fun_read_from=None,
                 sample_random_use_fun_read_from_can_write=False,
                 limit=-1,
        ):
        self.pos_index = pos_index
        self.neg_index = neg_index
        self.pos_weight = pos_weight
        self.neg_weight = neg_weight
        self.limit=limit
        self.random_use_fun=random_use_fun
        self.random_use_fun_read_from=random_use_fun_read_from
        self.sample_random_use_fun_read_from_can_write=sample_random_use_fun_read_from_can_write
        self.this_epoch=0
        self.result_dict=dict()
        self.init_time=time.time()
        self.resample(is_init=True)
        # self.setup_data()

    def setup_data(self):
        # 打乱后的正负样本
        random_pos_index=self.pos_index.copy() 
        random.shuffle(random_pos_index)
        random_neg_index=self.neg_index.copy()
        random.shuffle(random_neg_index)
        # 随机打乱原始列表
        random_all=random_pos_index+random_neg_index
        random.shuffle(random_all)
        # 平衡后正样本，正样本重复和负数样本一样多
        random_balance_pos=(random_pos_index*int(len(random_neg_index)/len(random_pos_index)+1))
        random_balance_neg=random_neg_index
        min_len=min(len(random_balance_pos),len(random_balance_neg))
        random_balance_pos=random_balance_pos[:min_len]
        random_balance_neg=random_balance_neg[:min_len]
        # 在batch上平衡的正负样本
        # print(random_balance_pos, random_balance_neg)
        random_balance_all_on_banch=[item for sublist in zip(random_balance_pos, random_balance_neg) for item in sublist]
        # 在整体上平衡的正负样本
        random_balance_all_on_all=random_balance_all_on_banch.copy()
        random.shuffle(random_balance_all_on_all)
        # 加权取正负样本
        # random.choices(v, weights=w, k=n)
        all_len=len(self.pos_index)+len(self.neg_index)
        weight_on_all=random.choices(self.pos_index+self.neg_index, weights=self.pos_weight+self.neg_weight, k=all_len)
        
        weight_on_ps_half=int(all_len/2)
        weight_p=random.choices(self.pos_index,weights=self.pos_weight,k=weight_on_ps_half)
        weight_n=random.choices(self.neg_index,weights=self.neg_weight,k=weight_on_ps_half)
        weight_on_ps_balance=weight_p+weight_n
        random.shuffle(weight_on_ps_balance)
        
        # dict map
        self.result_dict={
            "random|all":random_all,
            "balance|on_batch":random_balance_all_on_banch,
            "balance|on_all":random_balance_all_on_all,
            "weight|on_ps_balance":weight_on_ps_balance,
            "weight|on_all":weight_on_all,
        }
        # random|all balance|on_batch balance|on_all  weight|on_ps_balance  weight|on_all
        if self.random_use_fun in self.result_dict:
            result= self.result_dict[self.random_use_fun]
            if self.limit>0:
                result=result[:self.limit]
        
        elif self.random_use_fun.startswith("limit"):
            # 限制个数
            if len(self.random_use_fun.split("|"))>=1:
                limit_num=int(self.random_use_fun.split("|")[1])
            elif self.limit>0:
                limit_num=self.limit
            else:
                limit_num=len(random_all)
                print("not set limit num, use all")
            limitall=random_balance_all_on_banch[:min(len(random_balance_all_on_banch),limit_num)]
            random.shuffle(limitall)
            result=limitall

        # print(self.random_use_fun)
        # sss
        self.indices=result
        

    def __iter__(self):
        # 不问原始数据集长度和这个self.indices长度，最终以self.indices能迭代多少次为准
        # list 
        # full list
        # pop
        return iter(self.indices)

    def __len__(self):
        return len(self.indices)
    
    def resample(self,is_init=False):
        self.this_epoch+=1
        self.check_random_use_fun_now(is_init=is_init)
        self.setup_data()
    
    def check_random_use_fun_now(self,is_init=False):
        if self.random_use_fun_read_from is None:
            pass
        elif os.path.exists(self.random_use_fun_read_from):
            try:
                # 初始化则重写文件
                if is_init:
                    with open(self.random_use_fun_read_from,"w+") as f:
                        init_info="\n=====\n{}\n{}".format(self.init_time,self.random_use_fun)
                        f.write(init_info)
                        print("write sampler to file {}: {}".format(self.random_use_fun_read_from,init_info))
                else:
                #    其他情况读文件
                    with open(self.random_use_fun_read_from,"r") as f:
                        choice_in_file=f.read().split("\n")[-1]
                        if choice_in_file in self.result_dict:
                            self.random_use_fun=choice_in_file
                            print("use {}".format(choice_in_file))
                        else:
                            print("not support {} in file, use before {}, need rewrite".format(choice_in_file,self.random_use_fun))
                    # 如果有写日志权限，读完可以写
                    if self.sample_random_use_fun_read_from_can_write:
                        his_path="{}.{}.history".format(self.random_use_fun_read_from,self.init_time)
                        with open(his_path,"a+") as f:
                            f.write("\n{}".format(self.random_use_fun))
            except BaseException as e:
                print(e)
        elif isinstance(self.random_use_fun_read_from,str) and self.sample_random_use_fun_read_from_can_write:
            # 有路径  没文件  可写 = 写
            try:
                os.makedirs(os.path.dirname(self.random_use_fun_read_from),exist_ok=True)
                with open(self.random_use_fun_read_from,"w+") as f:
                    init_info="\n=====\n{}\n{}".format(self.init_time,self.random_use_fun)
                    f.write(init_info)
                    print("write sampler to file {}: {}".format(self.random_use_fun_read_from,init_info))
            except BaseException as e:
                print(e)
        else:
            print("not change sampler fun")
        
        