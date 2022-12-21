import pickle
import numpy as np
import datetime
import wget
import pickle
import os
from peewee import *
import time


class HarpNoaa():
    def __init__(self):
        self.all_harps_with_noaa_ars_online="http://jsoc.stanford.edu/doc/data/hmi/harpnum_to_noaa/all_harps_with_noaa_ars.txt"
        self.all_harps_with_noaa_ars_local="all_harps_with_noaa_ars.txt"
        self.kharp_vnoaalist_dict=dict()
        self.knoaa_vharp_dict=dict()
        self.noaa_list=list()
        self.harp_list=list()
        self.has_prepare=False

    
    def prepare(self):
        if not os.path.exists(self.all_harps_with_noaa_ars_local):
            wget.download(self.all_harps_with_noaa_ars_online,out=self.all_harps_with_noaa_ars_local)
        with open(self.all_harps_with_noaa_ars_local,"r")as f:
            all=f.read().split("\n")
        for i in all:
            try:
                harp_num=str(int(i.split(" ")[0]))
                noaa_list=i.split(" ")[1].split(",")
                self.kharp_vnoaalist_dict[harp_num]=noaa_list
                for noaa_num in noaa_list:
                    self.knoaa_vharp_dict[noaa_num]=harp_num
            except BaseException as e:
                print(i)
                print(e)
        self.noaa_list=list(self.knoaa_vharp_dict)
        self.harp_list=list(self.kharp_vnoaalist_dict)
        self.has_prepare=True


    def save(self,kharp_vnoaalist_dict_pickle_path=None,knoaa_vharp_dict_pickle_path=None,noaa_list_path=None,harp_list_path=None):
        if not self.has_prepare:
            self.prepare()
        if kharp_vnoaalist_dict_pickle_path is not None:
            with open(kharp_vnoaalist_dict_pickle_path,'wb+') as pickle_file:  
                pickle.dump(self.kharp_vnoaalist_dict,pickle_file)          
        if knoaa_vharp_dict_pickle_path is not None:
            with open(knoaa_vharp_dict_pickle_path,'wb+') as pickle_file: 
                pickle.dump(self.knoaa_vharp_dict,pickle_file) 
        if noaa_list_path is not None:
            with open(noaa_list_path,"w+") as f:
                f.write("\n".join(self.noaa_list))
        if harp_list_path is not None:
            with open(harp_list_path,"w+") as f:
                f.write("\n".join(self.harp_list))
                



class Flare(Model):
    deeps_flare_id = IntegerField(null=True)
    latitude = IntegerField(null=True)
    longtitude = IntegerField(null=True)
    noaa_ar = IntegerField(null=True)
    end_datetime = DateTimeField(null=True)
    peak_datetime = DateTimeField(null=True)
    source = CharField(null=True)
    start_datetime = DateTimeField(null=True)
    xray_class = CharField(null=True)
    xray_intensity = IntegerField(null=True)
    # id xray_class xray_intensity latitude longtitude start_datetime peak_datetime end_datetime source
    class Meta:
        database = None
        table_name = 'a202203_flare'
        primary_key = False
    

class NoaaFlaretime():
    def __init__(self,db_name,config_dict):
        # db_name='deepsolar'
        # config_dict={'host': '10.10.1.1', 'port': 1234, 'user': 'deepsolar', 'password': 'xxxxxxxx'}
        self.Flare=Flare
        self.Flare._meta.database=PostgresqlDatabase(db_name, **config_dict)
        self.noaa_list=[]
        self.noaa_flaretime_dict=dict()


    def set_noaa_list(self,noaa_list=None,noaa_list_path=None):
        if noaa_list is not None:
            self.noaa_list=noaa_list
        if noaa_list_path is not None:
            with open(noaa_list_path) as f:
                allstrraw=f.read()
            self.noaa_list=allstrraw.split("\n")
            
    def deal_one_noaa_num(self,noaa_num,save_path=None):
        noaa_num=int(noaa_num)
        if save_path is not None and not os.path.exists(save_path):
            os.makedirs(save_path)
            is_save=True
        else:
            is_save=False
        all=[[0,0,0,-1]]
        for i in self.Flare.select().where(self.Flare.noaa_ar==noaa_num):
            # # print(type(i),i.id,i.xray_class,i.xray_intensity)
            # # print(type(i.start_datetime),i.end_datetime,int(i.end_datetime.timestamp()))
            if i.start_datetime is  None and i.end_datetime is  None:
                continue
            end_t=int(i.end_datetime.timestamp())
            start_t=int(i.start_datetime.timestamp())
            map_dict={"A":100,"B":200,"C":300,"M":400,"X":500}  
            if i.xray_class not in map_dict.keys():
                continue
            if isinstance( i.xray_intensity,int):
                sub_v=i.xray_intensity
            else:
                sub_v=0
            xray_value=map_dict[i.xray_class]+sub_v
            all.append([start_t,end_t,xray_value,i.deeps_flare_id])
        if len(all)==1:
            return False
        a=np.array(all)
        
        s=a[:,0]
        e=a[:,1]
        l=a[:,2]
        i=a[:,3]
        new_order=list(np.lexsort((l,s))) 

        a=a[new_order,:]
        a[0,0]=a[1,0]
        a[0,1]=a[-1,1]
        a=a.astype(int)
        flare_delta_num=a.shape[0]

        if is_save:
            this_p=os.path.join(save_path,"{}.f0.csv".format(noaa_num))
            np.savetxt(this_p,a,fmt='%i', delimiter=",")
        b=a
        
        i_have_add=0
        if flare_delta_num>1:
            for fi in range(1,flare_delta_num-1):
                if a[fi,1]<a[fi+1,0]:
                    this_insert_data=np.array([a[fi,1]+1,a[fi+1,0]-1,0,-1])
                    b=np.insert(b,fi+i_have_add+1,this_insert_data,axis=0)
                    i_have_add+=1
                elif a[fi,1]>a[fi+1,0]:
                    b[fi+i_have_add,1]=a[fi+1,0]-1
            
        if is_save:
            this_p=os.path.join(save_path,"{}.f1.csv".format(noaa_num))
            np.savetxt(this_p,a,fmt='%i', delimiter=",")
            # # print(a)
            this_p=os.path.join(save_path,"{}.f2.csv".format(noaa_num))
            np.savetxt(this_p,b,fmt='%i', delimiter=",")
            # # print(b)
        return b
        
    def deal_noaa_num(self,save_split_numpy_path=None):
        for i in self.noaa_list:
            print(i)
            try:
                this_r=self.deal_one_noaa_num(i,save_split_numpy_path)
                if this_r is not False:
                    self.noaa_flaretime_dict[str(i)]=this_r
                else:
                    print("{}.none".format(i))
            except BaseException as e:
                print("{}.error.{}".format(i,e))
        return self.noaa_flaretime_dict

    def save_pickle(self,pickle_path):
        with open(pickle_path,'wb+') as pickle_file:  
            pickle.dump(self.noaa_flaretime_dict,pickle_file)  
        
    def load_pickle(self,pickle_path):
        with  open(pickle_path,'rb') as pickle_file:   
            self.noaa_flaretime_dict=pickle.load(pickle_file) 
        



class DealFlareLevel():
    def __init__(self,noaa_flaretime_dict_pickle_path):
        # noaa_dict_path='/home/zzr/project2/tag/noaa_flare_time_dict.pickle'
        with open(noaa_flaretime_dict_pickle_path,'rb')  as f:
            self.noaa_dict = pickle.load(f)
            
    def get_one_noaa_time_in_level(self,noaa_ar,data_time,time_type="%Y%m%d_%H%M%S"):
        # data_time="20150303_204800"
        # noaa_ar=12292
        
        noaa_dict=self.noaa_dict
        if str(noaa_ar) not in noaa_dict.keys():
            return False
        
        this_time=int(datetime.datetime.strptime(data_time,time_type).timestamp())
        # this_time
        this_noaa_value=noaa_dict[str(noaa_ar)]
        raw_t=this_noaa_value[:,0:2]
        this_t=np.ones_like(raw_t)*this_time
        time_delta=this_t-raw_t
        flag=np.sign(time_delta[:,0])*np.sign(time_delta[:,1])<=0
        time_is_in=np.where(flag)[0]
        if len(time_is_in)>0:
            time_is_index=time_is_in[-1]
            this_value=this_noaa_value[time_is_index,:]
            # # # # print(this_value)
            this_level=this_value[2]
            this_id=this_value[-1]
            # # # # print(this_level,this_id)
        else:
            this_level=0
            this_id=-1
        result=[this_level,this_id]
        return result
        
        

        # noaa_dict=noaa_dict
    def get_one_noaa_timelist_maxlevel(self,noaa_ar,data_time,time_list_second=[6*60*60,12*60*60,24*60*60,48*60*60],time_type="%Y%m%d_%H%M%S"):
        # data_time="20150303_204800"
        # # data_time="20150303_204800"
        # # noaa_dict=noaa_dict TODO
        # noaa_ar=12292
        # time_later_list=[6*60*60,12*60*60,24*60*60,48*60*60]
        time_later_list=time_list_second
        noaa_dict=self.noaa_dict
        
        if str(noaa_ar) not in noaa_dict.keys():
            # # # print("not in")
            return False
        # this_t_delta=time_later_list[4]
        result=[]
        for this_t_delta in time_later_list:
            # # # print(this_t_delta)

            this_time=int(datetime.datetime.strptime(data_time,time_type).timestamp())
            next_time=this_time+this_t_delta
            # this_time
            this_noaa_value=noaa_dict[str(noaa_ar)]

            raw_t=this_noaa_value[:,0:2]
            this_t=np.ones_like(raw_t)*this_time
            next_t=np.ones_like(raw_t)*next_time

            this_time_delta=this_t-raw_t
            this_flag=np.sign(this_time_delta[:,0])*np.sign(this_time_delta[:,1])<=0
            # # # print(this_flag)
            this_time_is_in=np.where(this_flag)[0]
            next_time_delta=next_t-raw_t
            next_flag=np.sign(next_time_delta[:,0])*np.sign(next_time_delta[:,1])<=0
            # # # print(next_flag)
            next_time_is_in=np.where(next_flag)[0]


            if len(this_time_is_in)>0 and len(next_time_is_in)>0:
                # # # print(1)
                # # # print(this_time_is_in[-1],next_time_is_in[-1]+1)
                max_value_array=this_noaa_value[this_time_is_in[-1]:next_time_is_in[-1]+1,:]
            elif len(this_time_is_in)>0 :
                # # # print(2)
                max_value_array=this_noaa_value[this_time_is_in[-1]:,:]
            elif len(next_time_is_in)>0:
                # # # print(3)
                max_value_array=this_noaa_value[:next_time_is_in[-1]+1,:]
            elif np.sign(this_time_delta[0,0])*np.sign(this_time_delta[-1,1])<0:
                # # # print(4)
                max_value_array=this_noaa_value[:,:]
            else:
                # # # print(5)
                max_value_array=False
            # # # print(max_value_array)
                
            if max_value_array is not False:
                # # # print(len(max_value_array))
                if len(max_value_array)==1:
                    max_level=max_value_array[0,2]
                    max_id=max_value_array[0,3]
                elif len(max_value_array)>1:
                    max_index=np.argmax(max_value_array[:,2])
                    max_level=max_value_array[max_index,2]
                    max_id=max_value_array[max_index,3]
                # # # print(this_level,this_id)
                else:
                    max_level=0
                    max_id=-1
            else:
                max_level=0
                max_id=-1
            this_result=[max_level,max_id]
            result.append(this_result)
        # # # print(result)
        return result


    def deal_one_noaa_with_time(
        self,
        noaa_ar,
        data_time,
        time_list_second=[6*60*60,12*60*60,24*60*60,48*60*60],
        time_type="%Y%m%d_%H%M%S"):
        
        this_level=self.get_one_noaa_time_in_level(noaa_ar,data_time)
        range_level=self.get_one_noaa_timelist_maxlevel(noaa_ar,data_time,time_list_second,time_type)
        result=(this_level,range_level)
        return result
    
    def deal_one_or_group_noaa_with_time(
        self,
        noaa_ars,
        data_time,
        time_list_second=[6*60*60,12*60*60,24*60*60,48*60*60],
        time_type="%Y%m%d_%H%M%S"):
        """c1=w.deal_one_or_group_noaa_with_time([11147,11149],"20110122_081200")
           c1=w.deal_one_or_group_noaa_with_time([11149],"20110122_081200")
        Returns:
            tuple:   ([324, 65525], [[324, 65525], [324, 65525], [324, 65525], [324, 65525]])
                    [now flare level, now flare id] [given flare level, given flare id] 
        """
        t_level_result=[]
        t_range_result=[]
        if isinstance(noaa_ars,int) or isinstance(noaa_ars,str):
            result=self.deal_one_noaa_with_time(noaa_ars,data_time,time_list_second,time_type)
        elif isinstance(noaa_ars,list):  
            for noaa_ar in noaa_ars:
                # this_level=get_one_noaa_time_in_level(noaa_ar,data_time)
                # range_level=get_one_noaa_timelist_maxlevel(noaa_ar,data_time,time_list_second,time_type)
                # one_result=(this_level,range_level)
                # temp_result.append(one_result)
                # try:
                this_level,range_level=self.deal_one_noaa_with_time(noaa_ar,data_time,time_list_second,time_type)
                # # # print(this_level ,"00==========", range_level)
                if this_level and range_level:
                    t_level_result.append(this_level)
                    t_range_result.append(range_level)
            # print(t_range_result)
            level_result=np.array(t_level_result)
            # print(level_result)
            if len(level_result) > 0:
                # # print(level_result)
                level_index=level_result.argmax(axis=0)[1]
                # # print(level_index)
                level_result=t_level_result[level_index]
                
                # # print(t_range_result)

                max_index=np.array(t_range_result)[:,:,0]#[1]#.argmax()
                # print(max_index)
                # print(max_index.argmax(axis=0))
                max_list=max_index.argmax(axis=0) #list(max_index[:,1])
                finall_result_range=[]
                for i in range(len(max_list)):
                    # # print(i)
                    finall_result_range.append(t_range_result[max_list[i]][i])
                result=level_result,finall_result_range
                # # # print(result)
                #     return result
            else:
                result=False
        else:
            result=False
        return result







class DoSharp():
    def __init__(self,noaa_flaretime_dict_pickle_path,kharp_vnoaalist_dict_pickle_path,save_path=None):

        # noaa_flaretime_dict_pickle_path='/home/zzr/project2/tag/all_noaa_flaretime_dick_v3.pickle'
        # kharp_vnoaalist_dict_pickle_path='/home/zzr/project2/tag/noaa_to_harp.pickle'
        self.save_path=save_path #"/home/zzr/project2/tag/to_db_v3.2"
        self.dealfl=DealFlareLevel(noaa_flaretime_dict_pickle_path=noaa_flaretime_dict_pickle_path)
        with open(kharp_vnoaalist_dict_pickle_path,'rb')  as f:
            self.noaa_sharp_dict = pickle.load(f)
        self.noaa_sharp_dict_keys=list(self.noaa_sharp_dict.keys())

        
    
    def get_noaalist_from_sharpnum(self,sharp_num):
        sharp_num=str(sharp_num)
        # print(str(sharp_num)) 
        # print(self.noaa_sharp_dict.keys())
        # print(self.noaa_sharp_dict_keys)
        # print(str(sharp_num) in self.noaa_sharp_dict_keys)
        if str(sharp_num) in self.noaa_sharp_dict_keys:
            return self.noaa_sharp_dict[str(sharp_num)]
        else:
            return False
    
    # 2325.20121227_114800
    def deal_one_job(self,sharp_time,job_id=0):
        issharp=0
        iscea=1
        sharp_num,data_time=sharp_time.split(".")
        noaa_list=self.get_noaalist_from_sharpnum(sharp_num)
        # print(noaa_list)
        js=os.path.join(self.save_path,"{}.sucess.csv".format(job_id))
        jf=os.path.join(self.save_path,"{}.fail1.txt".format(job_id))
        jf2=os.path.join(self.save_path,"{}.fail2.txt".format(job_id))
        if noaa_list is not False:
            dresult=self.dealfl.deal_one_or_group_noaa_with_time(noaa_list,data_time)
            # ([0, -1], [[0, -1], [0, -1], [328, 74259], [328, 74259]])
            # print(dresult)
            if dresult is False:
                with open(jf2,"a+") as f:
                    f.write(sharp_time+"\n")   
                result = False
            else:
                sresult="{},{},{},{},{},{},{}".format(
                    sharp_time,
                    sharp_num,
                    data_time,
                    issharp,
                    iscea,
                    dresult[0][0],
                    dresult[0][1]
                )
                for i in dresult[1]:
                    sresult+=",{},{}".format(i[0],i[1])
                sresult+="\n"
                with open(js,"a+") as f:
                    f.write(sresult)
                result=True
        else:
            with open(jf,"a+") as f:
                f.write(sharp_time+"\n")     
            result=False
        return result      
    
    
    def run(self,harpnum_time_list_path,save_path=None):
        if save_path is not None:
            self.save_path=save_path
        if self.save_path is None:
            return False
        if os.path.exists(self.save_path):
            os.rename(self.save_path, "{}.bak.{}".format(self.save_path,time.time()))
        os.makedirs(self.save_path)

        #"/home/zzr/project2/tag/sharp12.txt"  # 5946.20150911_101200  list
        with open(harpnum_time_list_path,"r") as f:
            jobs=f.read().split("\n")
        lens=len(jobs)
        i=0
        for job in jobs:
            try:
                result=self.deal_one_job(job,0)
                if result is False:
                    js=os.path.join(self.save_path,"{}.runfail.txt".format(0))
                    with open(js,"a+") as f:
                        f.write(job+"\n")
            except BaseException as e:
                print(job)
                print(e)
                js=os.path.join(self.save_path,"{}.cantrun.txt".format(0))
                with open(js,"a+") as f:
                    f.write(job+"\n")
            i+=1
            if i%1000==0:
                print("{}/{}, {}".format(i,lens,i/lens))

