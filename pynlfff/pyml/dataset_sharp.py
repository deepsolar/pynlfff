
import numpy as np
# https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
import time
from torch.utils.data import Dataset
import os
import pandas as pd
import numpy as np
import random
import torch
from torchvision.transforms import Compose
import sqlite3
import random
from collections import deque
from torch.utils.data import Dataset, DataLoader, Sampler
from .dataset_sampler import ResamplingSampler
from astropy.io import fits


class sharp_fits_reader():
    def __init__(self, 
                 data_dir="/",
                 data_type="fits",
                 data_labels_pandas=None,
                 TRAIN_RUN_TASK=['c'],
                 forecast_win=[24,],
                 dimension_fun=None,
                 label_fun=None,
                 ):
        self.data_type=data_type
        self.label_fun=label_fun
        self.data_dir=data_dir
        self.data_labels=data_labels_pandas
        self.TRAIN_RUN_TASK=TRAIN_RUN_TASK
        self.forecast_win=forecast_win
        self.dimension_fun=dimension_fun
    
    def read_label(self, idx):
        """返回的是numpy数组，即标签列表，即使只有一个值，也放在列表里面
        任务输出都是 先窗口再等级 
        如 窗口1等级1 窗口1等级2 窗口2等级1 窗口2等级2 /  窗口1流量值  窗口2流量值 窗口3流量值

        Args:
            idx (_type_): _description_

        Returns:
            _type_: _description_
        """
        label=self.__read_label_value_list(idx)
        # if self.label_fun is not None:
        #     pass  # TODO
        return label
    
    def read_data(self,idx):
        """返回的是numpy数组，直接读取的数据，不包含batchsize的维度

        Args:
            idx (_type_): _description_

        Returns:
            _type_: _description_
        """
        if self.data_type == "npy":
            return self.read_data_npy(idx)
        elif self.data_type == "fits":
            return self.read_data_fits(idx)
        
        
    def __read_label_value_list(self, idx):
        if 'n' in self.TRAIN_RUN_TASK:
            return self.__read_label_value_list_has_n(idx)
        else:
            return self.__read_label_value_list_norm(idx)
    
    def __read_label_value_list_has_n(self, idx):
        sample=self.data_labels.loc[idx]
        label_train=[]
        label_eval=[]
        for win in self.forecast_win:
            col_name="h{}_index".format(win)
            label=sample[col_name]
            if label>=10:
                label=3
            elif label>=1:
                label=2
            elif label>=0.1:
                label=1
            else:
                label=0
            label_train.append(label)
            for task in self.TRAIN_RUN_TASK:
                if task in ["c","m","x"]:
                    col_name="h{}_index_label{}".format(win,task)
                    label = sample[col_name]
                    label_eval.append(label)
                else:
                    col_name="h{}_index_labelc".format(win)
                    labelc = sample[col_name]
                    if labelc==0:
                        label_eval.append(1)
                    else:
                        label_eval.append(0)
        result=label_train+label_eval
        result=np.array(result)
        # print(result)
        # print(  (np.log10(result)+4)/6 )
        # task_sharm_2d_full_class_resnet_o16
        return result
    
    def __read_label_value_list_norm(self, idx):
        sample=self.data_labels.loc[idx]
        result=[]
        for win in self.forecast_win:
            for task in self.TRAIN_RUN_TASK:
                if task=='v':
                    col_name="h{}_index".format(win)
                else:
                    col_name="h{}_index_label{}".format(win,task)
                label = sample[col_name]
                result.append(label)
        result=np.array(result)
        # print(result)
        # print(  (np.log10(result)+4)/6 )
        # task_sharm_2d_full_class_resnet_o16
        return result
    
    
    # @staticmethod
    def read_data_npy(self,idx):
        sample = self.data_labels.loc[idx]
        sub_p="{}/hmi.sharp_720s.{}.magnetogram.npy".format(
            sample["HARP_NUM"],sample["HARPNUM_TREC"]
        )
        sample_path = os.path.join(self.data_dir, sub_p)
        data=np.load(sample_path)
        return data
    
        # @staticmethod
    def read_data_fits(self,idx):
        sample = self.data_labels.loc[idx]
        sub_p="{}/hmi.sharp_720s.{}.magnetogram.fits".format(
            sample["HARP_NUM"],sample["HARPNUM_TREC"]
        )
        sample_path = os.path.join(self.data_dir, sub_p)
        
        # data=np.load(sample_path)
        with  fits.open(sample_path) as hdul:
            data = hdul[1].data.copy()
        
        return data

def makedirs(fpath,exist_ok):
    try:
        os.makedirs(fpath, exist_ok=exist_ok)
    except BaseException as e:
        print(e)

class HmiSharpMDataset(torch.utils.data.Dataset):
    def __init__(self,
                 dataset_type="train",
                 label_file_path="x.csv",
                 forecast_win=[24,],
                 transforms=[],
                 label_transforms=[],
                 data_type="fits",
                 data_dir="/",
                 TRAIN_RUN_TASK=['c'],
                 dimension_fun=None,
                 weight_division_window = 48,
                 weight_division_task = 'c',
                 sampler ='weight',
                 sample_random_use_fun_read_from=None,
                 sample_random_use_fun_read_from_can_write=False,
                 batch_size=2,
                 ):
        self.data_type=data_type
        self.dimension_fun=dimension_fun
        self.sample_random_use_fun_read_from=sample_random_use_fun_read_from
        self.sample_random_use_fun_read_from_can_write=sample_random_use_fun_read_from_can_write
        self.weight_division_window=weight_division_window
        self.weight_division_task=weight_division_task
        self.label_transforms=label_transforms
        self.TRAIN_SAMPLER=sampler
        self.dataset_type = dataset_type
        self.label_file_path = label_file_path
        self.forecast_win = forecast_win
        self.transforms = transforms
        self.data_dir=data_dir
        self.TRAIN_RUN_TASK=TRAIN_RUN_TASK
        self.batch_size=batch_size
        self.is_debugging_now=False
        self.is_debugging_now=True

        # ====
        self.length = None
        self.data_labels_pandas=None
        self.sample_transforms=None
        self.sample_label_transforms=None
        self.__init()

    def __init(self):
        self.__init_pandas()
        self.__init_reader()
        self.__int_transforms()
        self.__init_sampler_ps_weight()
        self.__init_sampler()
        self.__len__()
        
        
    # @staticmethod
    def __int_transforms(self):
        """
        :param self_transforms:
        :param device:
        :param unsqueeze: None or 具体数字
        :return:
        """
        if isinstance(self.transforms,list) and len(self.transforms)>=1:
            self.sample_transforms = Compose(self.transforms)
        elif  isinstance(self.transforms,Compose) or  isinstance(self.transforms,torch.nn.Sequential):
            self.sample_transforms = self.transforms
        if isinstance(self.label_transforms,list) and len(self.label_transforms)>=1:
            self.sample_label_transforms = Compose(self.label_transforms)
        elif  isinstance(self.label_transforms,Compose) or  isinstance(self.label_transforms,torch.nn.Sequential):
            self.sample_label_transforms = self.label_transforms
        
        # return self.__s_trans

    def __init_reader(self):
        # 配置样本数据读取器

        if self.dataset_type == "prepare":
            self.sample_reader = None #Nlfff_hdf_reader()
                # [TensorToNdarray(), ], 'cpu', None)
        elif self.dataset_type in ["train", "val", "test"]:
            self.sample_reader=sharp_fits_reader(
                 data_dir=self.data_dir,
                 data_type=self.data_type,
                 dimension_fun=self.dimension_fun,
                 data_labels_pandas=self.data_labels_pandas,
                 TRAIN_RUN_TASK=self.TRAIN_RUN_TASK,
                 forecast_win=self.forecast_win,
                 label_fun=None,
            )
        else:
            raise  Exception("not define dataset")

    def __init_pandas(self):
        # 读取标签
        if self.label_file_path.endswith(".csv"):
            df = pd.read_csv(self.label_file_path)
        elif self.label_file_path.endswith(".db"):
            query = """SELECT * FROM hmi_sharp_720s_with_noaa_m96_c60_cmx"""
            with  sqlite3.connect(self.label_file_path) as conn:
                df = pd.read_sql(query, conn)
        else:
            raise ValueError("指定错误label_file_path")
        df = df.fillna(0.1)
        # df_unique = df.drop_duplicates(subset=['file_path'])
        # self.data_csv = df_unique.copy()

        # 筛选标签
        # dataset_type_map = {"train": [1,], "val": [2, 3], "test": [2, 3], "prepare": None}
        dataset_type_map = {
            "train": [1,],
            "val": [2,3],
            "test": [2,3],
            "prepare": None,
            "explain":[4,],
        }
        

        if self.dataset_type not in dataset_type_map:
            raise ValueError("指定错误dataset_type")
        elif self.dataset_type in ["prepare",]:
            # print(len(df))
            df_unique = df.drop_duplicates(subset=['HARPNUM_TREC'])
            # print(len(df_unique))
            df_sorted = df_unique.sort_values(by='HARPNUM_TREC')
            self.data_labels_pandas = df_sorted.copy()
        elif self.dataset_type in ["train", "val", "test"]:
            # condition = ((df['forecast_window'] == self.forecast_win)
            #              & (df['dataset_flag'] == dataset_type_map[self.dataset_type]))
            condition =  (df['dataset_flag'].isin(dataset_type_map[self.dataset_type]))
            self.data_labels_pandas = df[condition].copy().reset_index(drop=True)
        elif self.dataset_type in ["explain"]:
            condition="TODO"
            self.data_labels_pandas = df[condition].copy().reset_index(drop=True)
        print("dataset:{};len:{}".format(self.dataset_type,len(self.data_labels_pandas)))

    def __get_one_train_without_try(self,idx):
        s_data = self.sample_reader.read_data(idx)
        if self.sample_transforms is not None:
            # print(s_data.shape)
            # print("===============")
            s_data=self.sample_transforms(s_data)
        s_label = self.sample_reader.read_label(idx)
        if self.sample_label_transforms is not None:
            s_label=self.sample_label_transforms(s_label)
        sample = {'data': s_data, 'label': s_label}
        return sample
        
    def get_one_train(self, idx):
        if self.is_debugging_now:
            # debug模式有错直接抛出
            sample=self.__get_one_train_without_try(idx=idx)
            
        else:
            # 运行模式，需要try catch
            try:
                sample=self.__get_one_train_without_try(idx=idx)
            except BaseException as e:
                print("ERROR {} {}".format(idx, e))
                idx=random.randint(0, self.length)
                # 会一直递归
                sample = self.get_one_train(idx)
        
        return sample

    def get_one_prepare(self, index):
        raise ValueError("指定错误get_one_prepare")

    def get_one_explain(self, index):
        raise ValueError("指定错误get_one_explain")

    def __getitem__(self, index):
        if self.dataset_type in ["train", "val", "test"]:
            return self.get_one_train(index)
        elif self.dataset_type in ["prepare"]:
            return self.get_one_prepare(index)
        elif self.dataset_type in ["explain"]:
            return self.get_one_explain(index)

    def __len__(self):
        if self.length is None:
            self.length = len(self.data_labels_pandas)
        return self.length


    
    def get_sampler_balance_batch(self,random_use_fun="balance|on_all",limit=-1,):
        sampler=ResamplingSampler(
            pos_index=self.pos_index_list, 
            neg_index=self.neg_index_list, 
            pos_weight=self.pos_weight_list, 
            neg_weight=self.neg_weight_list,
            random_use_fun=random_use_fun,
            random_use_fun_read_from=self.sample_random_use_fun_read_from,
            sample_random_use_fun_read_from_can_write=self.sample_random_use_fun_read_from_can_write,
            limit=limit,
            )
        return sampler

    def get_sampler(self):
        return self.finall_sampler
        
    def __init_sampler(self):
        if self.TRAIN_SAMPLER is None:
            self.finall_sampler=None
            return
        if not isinstance(self.TRAIN_SAMPLER,str):
            raise Exception("error TRAIN_SAMPLER")
        sampler_list=self.TRAIN_SAMPLER.split("|")

        
        if sampler_list[0] == 'weight':                                                         # weight[|xx]
            if len(sampler_list)==1 or sampler_list[1]=="on_all":                               # weight|on_all
                self.finall_sampler = self.get_sampler_balance_batch("weight|on_all")
            elif sampler_list[1]=="on_ps_balance":                                              # weight|on_ps_balance
                self.finall_sampler = self.get_sampler_balance_batch("weight|on_ps_balance")
        elif sampler_list[0] == 'balance':                                                      # balance[|xx]
            if len(sampler_list)==1 or sampler_list[1]=="on_all":                               # balance|on_all
                self.finall_sampler = self.get_sampler_balance_batch("balance|on_all")
            elif sampler_list[1]=="on_batch":                                                   # balance|on_batch
                self.finall_sampler = self.get_sampler_balance_batch("balance|on_batch")
        elif sampler_list[0] == 'all' or sampler_list[0] == 'random|all':                       # all  random|all
            self.finall_sampler = self.get_sampler_balance_batch("random|all")
        elif sampler_list[0] == 'limit':                                                        # limit|100
            limit_num=int(sampler_list[1])
            self.finall_sampler = self.get_sampler_balance_batch("limit",limit=limit_num)
        else:
            self.finall_sampler=None
        

    def __init_sampler_ps_weight(self):
        # self.weight_division_window=weight_division_window
        # self.weight_division_task=weight_division_task

        if self.weight_division_window is None:
            if "v" not in self.TRAIN_RUN_TASK:
                if 72 in self.forecast_win:
                    self.weight_division_window=72
                else:
                    self.weight_division_window=48
            else:
                if 72 in self.forecast_win:
                    self.weight_division_window=72
                else:
                    self.weight_division_window=48
        if self.weight_division_task is None:
            if "v" not in self.TRAIN_RUN_TASK:
                if 'c' in self.TRAIN_RUN_TASK:
                    self.weight_division_task='c'
                else:
                    self.weight_division_task='m'
            else:
                self.weight_division_task='m'
                # self.weight_division_task='c'
        
        # full
        full_weght_key="h{}_index".format(self.weight_division_window)
        self.full_weight_list = self.data_labels_pandas.iloc[:][full_weght_key].to_numpy()
        # pos neg
        label = "h{}_index_label{}".format(self.weight_division_window,self.weight_division_task)
        df = self.data_labels_pandas
        self.pos_index_list = list(df[df[label] == 1].index)
        self.neg_index_list = list(df[df[label] == 0].index)
        weight_col="h{}_index".format(self.weight_division_window)
        self.pos_weight_list = df.iloc[self.pos_index_list][weight_col].tolist()
        self.neg_weight_list = df.iloc[self.neg_index_list][weight_col].tolist()




