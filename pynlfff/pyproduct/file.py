# coding=utf-8

"""
Purpose:   [1] Read the bin file which is produced by nlfff (Thomas Wiegelmann's)

Usage:     This code depends on the numpy h5py
           The first libraries are in the standard Anaconda distribution.
           h5py can be installed from conda or pip
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   From Thomas Wiegelmann (wiegelmann@mps.mpg.de)'s IDL code to do the same thing (2011.20)
           ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) & ZhuXiaoShuai(xszhu@bao.ac.cn)  Edit Python Reference Thomas Wiegelmann (2022.03)

"""

import os
import re
import time
import h5py
import numpy as np


class NlfffFile():
    def __init__(self, bin_endian="little", bin_float_size=8):
        """
        given bin_endian and bin_float_size is the computer product bin data format not now read computer format
        :param bin_endian: little or big
        :param bin_float_size: 8 or 4
        """
        if bin_endian == "little":  # for read bin use
            self.endian = "<"
        elif bin_endian == "big":
            self.endian = ">"
        self.float_size = bin_float_size
        if bin_float_size == 8:
            self.float_format = "d"  # double
        elif bin_float_size == 4:
            self.float_format = "f"  # float
        self.data_hdf_dataset_name="Bxyz"

    def check_bin_size_with_grid(self, bin_path, grid_path=None,nx=None,ny=None,nz=None):
        """
        check bin size agree with bin or not
        :param bin_path: the path for Bout.bin or B0.bin,include file's name
        :param grid_path: the path for grid.ini path,include file's name
        :return: True or False
        """
        result = False
        if isinstance(grid_path,str) and os.path.exists(bin_path) and os.path.exists(grid_path):
            bin_xyz_size = self.get_size_from_grid(grid_path)
        elif isinstance(nx,int) and isinstance(ny,int) and isinstance(nz,int):
            bin_xyz_size=[nx,ny,nz]
        else:
            raise Exception("grid_path or nx,ny,nz not given or illegal")
        bin_os_size = os.path.getsize(bin_path)
        norm_size = 3 * self.float_size  # 24 like 24=3*8  three heft and 8byte for double
        bin_com_size = bin_xyz_size[0] * bin_xyz_size[1] * bin_xyz_size[2] * norm_size
        # like 10240 > 105371648 - (140 * 224 * 140 * 24) > 0
        can_delta_max = 10240  # byte
        can_delta_min = 0
        if can_delta_max >= bin_os_size - bin_com_size >= can_delta_min:
            result = True
        return result

    def get_size_from_grid(self, grid_path):
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

    def __bin2array_with_nxyz_oneload_alldata_nomap(self, nx, ny, nz, bin_path):
        """
        load all bin data to memory and tran to array
        :param nx: nx size
        :param ny: ny size
        :param nz: nz size
        :param bin_path: the path of bin
        :return: numpy array shape like (3,nx,ny,nz)
        """
        pic = False
        float_format = self.float_format
        endian = self.endian
        np_dtype_str = "{}{}".format(endian, float_format)  # like little '<d'
        with open(bin_path, "rb") as f:
            pic = np.fromfile(
                f,  # which is open
                dtype=np.dtype(np_dtype_str),
                # np_dtype_str eg '<d' little https://numpy.org/doc/stable/reference/arrays.dtypes.html
                count=-1,  # all data
                sep='',  # Binary without spacing
                offset=0
                # The offset from the beginning is 0, note that this is the first operation after opening the file
            ).reshape(
                (3, nx, ny, nz),  # 3*nx*ny*nz
                order='C'  # According to the C language order reshape, that is, the last (nz) changes the fastest
            )
        # time.sleep(100)
        return pic

    def __bin2array_with_nxyz_oneload_alldata_memmap(self, nx, ny, nz, bin_path):
        """
        not load all bin data to memory but use map, and tran to array
        :param nx: nx size
        :param ny: ny size
        :param nz: nz size
        :param bin_path: the path of bin
        :return: numpy array shape like (3,nx,ny,nz)
        """
        pic = False
        float_format = self.float_format
        endian = self.endian
        np_dtype_str = "{}{}".format(endian, float_format)  # eg '<d'
        pic = np.memmap(bin_path,
                        dtype=np.dtype(np_dtype_str),
                        offset=0,
                        shape=(3, nx, ny, nz),
                        order='C')  # https://numpy.org/doc/stable/reference/generated/numpy.memmap.html
        # time.sleep(100)
        return pic

    def read_bin(self, bin_path, grid_path=None,nx=None,ny=None,nz=None, memmap=True):
        """
        read bin to numpy array shape like (3,nx,ny,nz)
        :param bin_path: the path of Bout.bin or B0.bin
        :param grid_path: the path of grid.ini
        :param nx: the int value of nx
        :param ny: the int value of ny
        :param nz: the int value of nz
        :param memmap: True or False,default True, True use np.memmap
        :return: numpy array shape like (3,nx,ny,nz) ,or size is not ok return False
        """
        result = False
        if isinstance(grid_path,str) and os.path.exists(grid_path):
            cz = self.check_bin_size_with_grid(bin_path, grid_path=grid_path)
            nxyz = self.get_size_from_grid(grid_path)
        elif isinstance(nx,int) and isinstance(ny,int) and isinstance(nz,int):
            cz = self.check_bin_size_with_grid(bin_path, nx=nx,ny=ny,nz=nz)
            nxyz=[nx,ny,nz]
        else:
            raise Exception("grid_path or nx,ny,nz not given or illegal")
        if cz:
            if memmap:  # like lazy load
                result = self.__bin2array_with_nxyz_oneload_alldata_memmap(nxyz[0], nxyz[1], nxyz[2], bin_path)
            else:
                result = self.__bin2array_with_nxyz_oneload_alldata_nomap(nxyz[0], nxyz[1], nxyz[2], bin_path)
        return result
    
    def read_bin2(self,head_fileName=None,bout_fileName=None,bout_dir=None):
        if bout_dir is not None:
            head_fileName=os.path.join(bout_dir,'grid3.ini')
            bout_fileName=os.path.join(bout_dir,'Bout.bin')

        with open(head_fileName,'rb') as f:
            f.readline()
            nx=int(f.readline())
            f.readline()
            ny=int(f.readline())
            f.readline()
            nz=int(f.readline())
            f.close()

        nc=3    
        data=np.fromfile(file=bout_fileName,offset=0,count=3*nx*ny*nz,dtype=np.double).reshape(nc,nx,ny,nz)
        print('[bout] shape: %s'%(str(data.shape)))

        return data

    def tran_bin2hdf5(self, bin_path, hdf5_path, grid_path=None,nx=None,ny=None,nz=None, memmap=True, overwrite=True):
        """
        tran nlfff bin data to hdf5 format
        :param bin_path: the path of Bout.bin or B0.bin
        :param grid_path: the path of grid.ini
        :param hdf5_path: the save path of hdf5_path, with .h5 or .hdf5 suffix
        :param memmap: True or False, default True open bin to np array tran use memmap inner
        :param overwrite: True or False, default True, if hdf5 is exists,will overwrite
        :return: tran sucess will return True otherwise return False
        """
        result = False
        data_array = self.read_bin(bin_path=bin_path, grid_path=grid_path,nx=nx,ny=ny,nz=nz, memmap=memmap)
        if data_array is not False:
            result = self.write_hdf5(data_array, hdf5_path, overwrite)
        return result

    def write_hdf5(self, data_array, hdf5_path, overwrite=True):
        """
        write numpy array shape like (3,nx,ny,nz) to hdf5
        :param data_array: numpy array shape like (3,nx,ny,nz)
        :param hdf5_path: the save path of hdf5_path, with .h5 or .hdf5 suffix
        :param overwrite: True or False, default True, if hdf5 is exists,will overwrite
        :return: save sucess will return True otherwise return False
        """
        result = False
        if hdf5_path.endswith(".h5") or hdf5_path.endswith(".hdf5"):
            this_path = os.path.split(hdf5_path)
            if not os.path.exists(this_path[0]):
                os.makedirs(this_path[0])
            if not os.path.exists(hdf5_path) or overwrite:
                # dataset_amount = 1,
                # if dataset_amount == 1:
                with h5py.File(hdf5_path, 'w') as hf:
                    hf.create_dataset(self.data_hdf_dataset_name, data=data_array)
                    result = True
                # elif dataset_amount == 3:
                #     with h5py.File(hdf5_path, 'w') as hf:
                #         hf.create_dataset("Bx", data=data_array[0])
                #         hf.create_dataset("By", data=data_array[1])
                #         hf.create_dataset("Bz", data=data_array[2])
        else:
            raise Exception("hdf5_path need end with .h5 or .hdf5")
        return result

    def read_hdf5(self, hdf5_path):
        """
        read numpy array from hdf5 file
        :param hdf5_path: the path of hdf5 file
        :return: numpy array shape like (3,nx,ny,nz)
                if file not exists , or not end with .h5 .hdf5 , or read fail will return False
        """
        result = False
        if os.path.exists(hdf5_path):
            if hdf5_path.endswith(".h5") or hdf5_path.endswith(".hdf5"):
                with h5py.File(hdf5_path, 'r') as hf:
                    result = hf[self.data_hdf_dataset_name][:]
        else:
            raise Exception("hdf5 file not exists")
        return result


class nlfffFind():
    def __init__(self):
        pass

    def get_hmi_list_from_file(self, file_path):
        """
        get hmi list from ls or tree log
        :param file_path: the path of ls or tree log file
        :return: list like ["hmi.sharp_cea_720s.7334.20190125_013600_TAI","hmi.sharp_cea_720s.7334.20190126_062400_TAI"]
                file not exists or open fail will return False
        """
        result = False
        if os.path.exists(file_path):
            with open(file_path, 'r')as f:
                file_data = f.read()
            # print(file_data)
            pattern = r'hmi.*?_TAI'
            result = re.findall(pattern, file_data)
        return result

    def get_hmi_set_from_file(self, file_path):
        """
        get hmi set from ls or tree log
        :param file_path: the path of ls or tree log file
        :return: set like {"hmi.sharp_cea_720s.7334.20190125_013600_TAI","hmi.sharp_cea_720s.7334.20190126_062400_TAI"}
            file not exists or open fail will return False
        """
        result = False
        job_list = self.get_hmi_list_from_file(file_path)
        if job_list is not False:
            result = set(job_list)
        return result

    def get_level_dir_from_name(self, name):
        """
        given name return is level
        :param name: eg hmi.sharp_cea_720s.7334.20190126_062400_TAI
        :return: eg num_7300_7399
        """
        job = name
        job_name_list = job.split(".")
        num = int(job_name_list[2])
        num_level_1 = num // 1000
        num_level_2 = (num // 100) % 10
        this_dir = "num_{}{}00_{}{}99".format(
            num_level_1, num_level_2, num_level_1, num_level_2)
        return this_dir


if __name__ == "__main__":
    print("test")
    bout_bin_path = r"/home/zander/Desktop/Bout.bin"
    grid_path = r"/home/zander/Desktop/grid3.ini"
    h5_path = r"/home/zander/Desktop/Bxyz.h5"

    r = NlfffFile()

    s = r.get_size_from_grid(grid_path)
    print(s)

    s2 = r.read_bin(bout_bin_path, grid_path)
    s2 = r.read_bin(bout_bin_path,nx=204,ny=392,nz=224)
    print(s2)

    r.tran_bin2hdf5(bout_bin_path, h5_path, grid_path)
    r.tran_bin2hdf5(bout_bin_path, h5_path, nx=204,ny=392,nz=224)

    a=np.random.uniform(-5, 5, size=(3, 100,50,40))
    h5_path= r"/home/zander/Desktop/Bxyz2.h5"
    r.write_hdf5(a,h5_path)
    # time.sleep(100)
