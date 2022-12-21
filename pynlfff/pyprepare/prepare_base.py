# coding=utf-8
"""
Purpose:   [1] prepare Bp Bt Br or azimuth field inclination [disambig] for nlfff computer which is version 5 by Thomas Wiegelmann (wiegelmann@mps.mpg.de)

Usage:     This code depends on the pandas  numpy astropy and disambiguation
           The first two libraries are in the standard Anaconda distribution.
           astropy can be installed from conda or pip
           The disambiguation library can be obtained from https: https://github.com/mbobra/SHARPs/blob/master/disambiguation.py
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   From Thomas Wiegelmann (wiegelmann@mps.mpg.de)'s IDL code to do the same thing (2011.20)
           ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) & ZhuXiaoShuai(xszhu@bao.ac.cn) Edit Python code From Thomas Wiegelmann (2022.03)
"""

import os
import pandas
from astropy.io import fits
import numpy
from . import disambiguation

class PrepareWorker():
    
    def __init__(self,mu=0.1,nd=0,nue=0.00100000,boundary=0):
        self.mu = mu
        self.nd = nd
        self.nue = nue
        self.boundary=boundary


    def read_fits_hdu1_data(self,f_path):
        """read fits and return hudl[1].data

        Args:
            f_path (str): path of fits

        Returns:
            _type_: hudl[1].data
        """
        with fits.open(f_path) as hdul:
            data = hdul[1].data
        return data

    def write_boundary_to_ini(self,save_path):
        """write boundary to ini, which write Some constants to given path

        Args:
            save_path (str): path of save boundary with file name, eg /xxx/grid3.ini

        Returns:
            _type_: Success returns True, failure returns False
        """
        result=False
        grid_str = "nue\n\t{0}\nboundary\n\t{1}\nMask {2}\n".format(self.nue,self.boundary,"B_T/max(B_T)")
        file_path = save_path
        with open(file_path, mode='w', encoding='utf-8') as file_obj:
            file_obj.write(grid_str)
            result = True
        return result
    
    def write_nxy_to_grid(self,nx,ny,nz,save_path):
        """
        write grid.ini
        :param nx: nx
        :param ny: ny
        :param ny: nz
        :param save_path: save_path[1] should store the full save path of grid1.ini,grid2.ini with filename and suffix
        :return: Success returns True, failure returns False
        """
        result=False
        grid_str = "nx\n\t{0}\nny\n\t{1}\nnz\n\t{2}\nmu\n\t{3}\nnd\n\t{4}".format(nx,ny,nz,self.mu,self.nd)
        file_path = save_path
        with open(file_path, mode='w', encoding='utf-8') as file_obj:
            file_obj.write(grid_str)
            result = True
        return result
    
    def write_errormask_to_maskdat(self,save_path,deal_type=2,nx=0,ny=0,b3dx=None,b3dy=None):
        """[summary]

        Args:
            save_path ([path]): save path of mask
            deal_type (int, optional): error mask Algorithms used, Defaults to 2 is B_T/max(B_T), set 1 is keep all 1 in error mask
            nx (int, optional): nx value. Defaults to 0.
            ny (int, optional): ny value. Defaults to 0.
            b3dx ([2d array], optional): b3dx. Defaults to None.
            b3dy ([2d array], optional): b3dy. Defaults to None.

        Returns:
            [bool]: Success returns True, failure returns False
        """
        run_result = False
        mask_result_data=None
        if deal_type==1:
            nxny=nx*ny
            mask_result_data = numpy.ones((nxny,1))
        elif deal_type==2:
            if b3dx is not None and b3dy is not None:
                # print(bx)
                # print(type(bx)) # <class 'numpy.ndarray'>
                # btrans=sqrt(bx^2+by^2)
                # maxBT=max(btrans)
                # mask_result_data=btrans/maxBT
                x_array = b3dx.flatten('F')  # flatten in column-major (Fortran- style) , Because the original idl code is, first fix y, then change x
                y_array = b3dy.flatten('F')
                btrans=numpy.sqrt(x_array**2+y_array**2)
                maxBT=numpy.max(btrans)
                mask_result_data=btrans/maxBT
        if mask_result_data is not None:
            file_path = save_path
            numpy.savetxt(file_path,mask_result_data,fmt='%.05f')
            run_result = True
            
        return run_result
            


    def write_b3dxyz_to_allboundaries(self,dx,dy,dz,save_path):
        """
        write allboundaries
        :param dx: dx
        :param dy: dy
        :param dz: dz
        :param save_path: save_path should store the full save path with allboundaries.dat with filename and suffix
        :return: None
        """
        x_array = dx.flatten('F')  # flatten in column-major (Fortran- style) , Because the original idl code is, first fix y, then change x
        y_array = dy.flatten('F')  
        z_array = dz.flatten('F')
        xyz = numpy.vstack([x_array, y_array, z_array])
        xyz = xyz.flatten('F')
        # file_path = os.path.join(save_path_list,'allboundaries.dat')
        file_path = save_path
        numpy.savetxt(file_path, xyz, fmt="%.6f", delimiter="\n")  # https://numpy.org/doc/stable/reference/generated/numpy.savetxt.html


    def read_b3dxyz_from_array_Bptr(self,Bp,Bt,Br):
        n_b3dx = Bp.shape
        n_b3dy = Bt.shape
        n_b3dz = Br.shape
        b3dx=Bp
        b3dy=-Bt
        b3dz=Br
        if (n_b3dx == n_b3dy) and (n_b3dx == n_b3dz):  # Check legality
            nx = n_b3dx[0]
            ny = n_b3dx[1]
        else:
            nx = 0
            ny = 0
        return b3dx,b3dy,b3dz,nx,ny

    def change_b3dxyz_multiple_4(self, b3dx, b3dy, b3dz, nx, ny):
        nx_m=nx%4
        ny_m=ny%4
        if nx_m != 0:
            nx_s = 1
            nx_e = nx - nx_m + 1
        else:
            nx_s = 0
            nx_e = nx
        if ny_m != 0:
            ny_s = 1
            ny_e = ny - ny_m + 1
        else:
            ny_s = 0
            ny_e = ny
        b3dx = b3dx[nx_s:nx_e,ny_s:ny_e]
        b3dy = b3dy[nx_s:nx_e,ny_s:ny_e]
        b3dz = b3dz[nx_s:nx_e,ny_s:ny_e]
        nx = nx - nx_m
        ny = ny - ny_m
        # print(type(b3dx)) # <class 'numpy.ndarray'>
        # print(b3dx.shape)
        # print(nx,ny)
        nz_not_multiple_4=int((nx+ny)*3/8)
        nz_add_to_4=int(4-nz_not_multiple_4%4)
        nz=nz_not_multiple_4+nz_add_to_4
        return b3dx, b3dy, b3dz, nx, ny, nz

    def prepare_from_fits_Bprt(self,Bp_path, Bt_path, Br_path,save_dir):
        """Generate preprocessed data from Bp.bits,Bt.bits,Br.bits

        Args:
            Bp_path (str): path of Bp.fits
            Bt_path (str): path of Bt.fits
            Br_path (str): path of Br.fits
            save_dir (str): path to save pre file

        Returns:
            _type_: True
        """
        bp_array = self.read_fits_hdu1_data(Bp_path)
        bt_array = self.read_fits_hdu1_data(Bt_path)
        br_array = self.read_fits_hdu1_data(Br_path)
        b3dx, b3dy, b3dz, nx, ny = self.read_b3dxyz_from_array_Bptr(bp_array, bt_array, br_array)
        self.prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)
        return True
        
    def base_rebin_half(self,m):
        """average pooling

        Args:
            m (2d array): 2d array to average pooling, Get the values of the four points and take the average

        Returns:
            _type_: 2d array which has polling
        """
        m11=m[0::2,0::2]  # Get the values of the four points
        m12=m[0::2,1::2]  # The front indicates rows and the back indicates columns. 0::2 means intercepted in steps of 2 from 0, which is an odd number. 
        m21=m[1::2,0::2]
        m22=m[1::2,1::2]
        m_new=(m11+m12+m21+m22)/4 # can do so provided that m is an even number of rows and columns, otherwise the intercepted shapes are not the same and cannot be added together i.e. the elements in each of the four field positions are averaged into a new element and the fields do not overlap
        return m_new
        
    def change_b3dxyz_rebin(self,b3dx, b3dy, b3dz, nx, ny, nz):
        b3dx = self.base_rebin_half(b3dx)
        b3dy = self.base_rebin_half(b3dy)
        b3dz = self.base_rebin_half(b3dz)
        nx = int(nx/2)
        ny = int(ny/2)
        nz = int(nz/2) 
        return b3dx, b3dy, b3dz, nx, ny, nz
    
    
    def prepare_from_array_to_three(self,b3dx, b3dy, b3dz, nx, ny, save_dir):
        if not os.path.isdir(save_dir):
            print("mkdir {}".format(save_dir))
            os.makedirs(save_dir)
        # grid3
        b3dx, b3dy, b3dz, nx, ny, nz= self.change_b3dxyz_multiple_4(b3dx, b3dy, b3dz, nx, ny)
        save_path = os.path.join(save_dir,"allboundaries3.dat")
        self.write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz,save_path)
        save_path = os.path.join(save_dir,"grid3.ini")
        self.write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir,"mask3.dat")
        self.write_errormask_to_maskdat(save_path,nx=nx,ny=ny,b3dx=b3dx,b3dy=b3dy)
        # grid2
        b3dx, b3dy, b3dz, nx, ny, nz= self.change_b3dxyz_rebin(b3dx, b3dy, b3dz, nx, ny, nz)
        save_path = os.path.join(save_dir,"allboundaries2.dat")
        self.write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz,save_path)
        save_path = os.path.join(save_dir,"grid2.ini")
        self.write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir,"mask2.dat")
        self.write_errormask_to_maskdat(save_path,nx=nx,ny=ny,b3dx=b3dx,b3dy=b3dy)
        # grid1
        b3dx, b3dy, b3dz, nx, ny, nz= self.change_b3dxyz_rebin(b3dx, b3dy, b3dz, nx, ny, nz)
        save_path = os.path.join(save_dir,"allboundaries1.dat")
        self.write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz,save_path)
        save_path = os.path.join(save_dir,"grid1.ini")
        self.write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir,"mask1.dat")
        self.write_errormask_to_maskdat(save_path,nx=nx,ny=ny,b3dx=b3dx,b3dy=b3dy)
        save_path = os.path.join(save_dir,"boundary.ini")
        self.write_boundary_to_ini(save_path)
        # allboundaries1.dat  grid1.ini  mask1.dat  boundary.ini


    def prepare_from_fits_afi(self,a_raw_path,f_raw_path,i_raw_path,save_dir):
        """
        Generate preprocessed data from azimuth.bits,field.bits,inclination.bits
        :param a_raw_path: azimuth.fits File path (need to include file name)
        :param f_raw_path: field.fits File path (need to include file name)
        :param i_raw_path: inclination.fits File path (need to include file name)
        :param save_dir: pre save dir
        :return: None
        """
        a_hdul = fits.open(a_raw_path)  # Note do not use with open assignment return, otherwise only the header data is retained, there are no two data fields, the default only cache the first header
        a_hdul.verify('silentfix')
        # 'silentfix' fixes and no warnings 'fix' fixes but prints warnings   https://github.com/astropy/astropy/blob/main/docs/io/fits/usage/verification.rst
        dict_header = dict(a_hdul[1].header)
        data_keys_frame_header = pandas.DataFrame([dict_header])
        f_hdul = fits.open(f_raw_path)
        i_hdul = fits.open(i_raw_path)
        data_object = disambiguation.CoordinateTransform(a_hdul, f_hdul, i_hdul, data_keys_frame_header)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)
        a_hdul.close()
        f_hdul.close()
        i_hdul.close()
        b3dx, b3dy, b3dz, nx, ny = self.read_b3dxyz_from_array_Bptr(bptr[:, :, 0],bptr[:, :, 1],bptr[:, :, 2])
        self.prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)


    def prepare_from_fits_afid(self,a_raw_path,f_raw_path,i_raw_path,d_raw_path,save_dir):
        """
        Generate preprocessed data from  azimuth.fits,field.fits,inclination.fits
        :param a_raw_path: azimuth.fits  File path (need to include file name)
        :param f_raw_path: field.fits  File path (need to include file name)
        :param i_raw_path: inclination.fits  File path (need to include file name)
        :param d_raw_path: disambig.fits  File path (need to include file name)
        :param save_dir: pre save dir
        :return: None
        """
        a_hdul = fits.open(a_raw_path)
        a_hdul.verify('silentfix')
        dict_header = dict(a_hdul[1].header)
        data_keys_frame_header = pandas.DataFrame([dict_header])
        f_hdul = fits.open(f_raw_path)
        i_hdul = fits.open(i_raw_path)
        d_hdul = fits.open(d_raw_path)
        basic_obj = disambiguation.Basic(recordset=None,method=2)  
        a_hdul_have_d = disambiguation.Basic.perform_disambiguation(basic_obj,a_hdul,d_hdul)
        data_object = disambiguation.CoordinateTransform(a_hdul_have_d, f_hdul, i_hdul, data_keys_frame_header)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)
        a_hdul.close()
        f_hdul.close()
        i_hdul.close()
        d_hdul.close()
        b3dx, b3dy, b3dz, nx, ny = self.read_b3dxyz_from_array_Bptr(bptr[:, :, 0],bptr[:, :, 1],bptr[:, :, 2])
        self.prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)


    def prepare_from_fits_afid_online(self,save_dir):
        """
        Download data online and process it, just for demonstration, not for actual use
        :param save_dir: pre save dir
        :return:
        """
        ### download azimuth field inclination disambiguation

        ## to Bp Bt Br
        # fetch the data from JSOC by providing a recordset specification and a disambiguation method
        query_info = disambiguation.Basic('hmi.sharp_720s[377][2011.02.15_00:00:00]', 2)
        keys, azimuth, field, inclination, disambig = disambiguation.Basic.get_data(query_info)

        # disambiguate the azimuthal component of the magnetic field
        disambiguated_azimuth = disambiguation.Basic.perform_disambiguation(query_info, azimuth, disambig)

        # construct the field vector in spherical coordinate components on the CCD grid
        data_object = disambiguation.CoordinateTransform(disambiguated_azimuth, field, inclination, keys)
        # print(data_object)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)

        b3dx, b3dy, b3dz, nx, ny = self.read_b3dxyz_from_array_Bptr(bptr[:, :, 0],bptr[:, :, 1],bptr[:, :, 2])
        self.prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)
        print("pre demo_fun_use_afid_online")



### demo test ###
def demo_fun_use_Bptr():
    # config
    p_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bp.fits"
    t_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bt.fits"
    r_raw_path = r"/media/zander/Data/now/work-inner/sun/LINFF/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Br.fits"
    sroot=r"/public1/home/sc81826/temp/out"
    # create object
    pre_worker = PrepareWorker()
    # pre
    pre_worker.prepare_from_fits_Bprt(p_raw_path,t_raw_path,r_raw_path,sroot)
    print("finish demo_fun_use_Bptr_local")

def demo_fun_use_afi():
    save_dir = r"/public1/home/sc81826/temp/out"
    dd=r"/public1/home/sc81826/archive/selAR/2019/hmi.sharp_720s.7334.20190124_124800_TAI"
    a=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.azimuth.fits"
    f=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.field.fits"
    i=dd+"/hmi.sharp_720s.7334.20190124_124800_TAI.inclination.fits"
    pre_worker = PrepareWorker()
    pre_worker.prepare_from_fits_afi(a,f,i,save_dir)
    print("finish demo_fun_use_afi_local")

def demo_fun_use_afid():
    save_dir = r"/public1/home/sc81826/temp/out"
    dd=r"/public1/home/sc81826/run/linff-main/run_space/tool/data"
    a=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.azimuth.fits"
    f=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.field.fits"
    i=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.inclination.fits"
    d=dd+"/hmi.sharp_720s.7300.20180823_173600_TAI.disambig.fits"
    pre_worker = PrepareWorker()
    pre_worker.prepare_from_fits_afid(a,f,i,d,save_dir)
    print("finish demo_fun_use_afi_local")


if __name__=="__main__":
    demo_fun_use_Bptr()
    demo_fun_use_afi()
    demo_fun_use_afid()




