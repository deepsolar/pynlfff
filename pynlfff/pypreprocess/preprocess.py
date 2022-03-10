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


class Preprocess():

    def __init__(self, mu=0.1, nd=0):
        self.mu = mu
        self.nd = nd
        # self.nz = nz

    def __read_fits_hdu1_data(self, f_path):
        """
        工具库函数读取fits的hdu1的数据
        :param f_path: 文件路径
        :return: hdul[1].data
        """
        with fits.open(f_path) as hdul:
            data = hdul[1].data
        return data

    def __write_boundary_to_ini(self, save_path):
        """
        写grid.ini文件
        :param nx: nx值
        :param ny: ny值
        :param save_path: save_path[1]应该存储有grid1.ini,grid2.ini带文件名和后缀的完整保存路径
        :return: 成功返回True，失败返回False
        """
        result = False

        grid_str = "nue\n\t{0}\nboundary\n\t{1}\nMask {2}\n".format(0.00100000, 0, "B_T/max(B_T)")
        # file_path = os.path.join(save_path_list,'grid.ini')
        file_path = save_path
        with open(file_path, mode='w', encoding='utf-8') as file_obj:
            file_obj.write(grid_str)
            result = True
        return result

    def __write_nxy_to_grid(self, nx, ny, nz, save_path):
        """
        写grid.ini文件
        :param nx: nx值
        :param ny: ny值
        :param save_path: save_path[1]应该存储有grid1.ini,grid2.ini带文件名和后缀的完整保存路径
        :return: 成功返回True，失败返回False
        """
        result = False

        grid_str = "nx\n\t{0}\nny\n\t{1}\nnz\n\t{2}\nmu\n\t{3}\nnd\n\t{4}".format(nx, ny, nz, self.mu, self.nd)
        # file_path = os.path.join(save_path_list,'grid.ini')
        file_path = save_path
        with open(file_path, mode='w', encoding='utf-8') as file_obj:
            file_obj.write(grid_str)
            result = True
        return result

    def __write_errormask_to_maskdat(self, save_path, deal_type=2, nx=0, ny=0, bx=None, by=None):
        """[summary]

        Args:
            save_path ([type]): [description]
            deal_type (int, optional): [description]. Defaults to 2.
            nx (int, optional): [description]. Defaults to 0.
            ny (int, optional): [description]. Defaults to 0.
            bx ([2d数组], optional): [description]. Defaults to None.
            by ([2d数组], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        run_result = False
        mask_result_data = None
        if deal_type == 1:
            nxny = nx * ny
            mask_result_data = numpy.ones((nxny, 1))
        elif deal_type == 2:
            if bx is not None and by is not None:
                # print(bx)
                # print(type(bx)) # <class 'numpy.ndarray'>
                # btrans=sqrt(bx^2+by^2)
                # maxBT=max(btrans)
                # mask_result_data=btrans/maxBT
                x_array = bx.flatten('F')  # 因为原来idl代码是，先固定y，再变x的
                y_array = by.flatten('F')
                btrans = numpy.sqrt(x_array ** 2 + y_array ** 2)
                maxBT = numpy.max(btrans)
                mask_result_data = btrans / maxBT
        if mask_result_data is not None:
            file_path = save_path
            numpy.savetxt(file_path, mask_result_data, fmt='%.05f')
            # with open(file_path, mode='w', encoding='utf-8') as file_obj:
            #     file_obj.write(grid_str)
            run_result = True

        return run_result

    def __write_b3dxyz_to_allboundaries(self, dx, dy, dz, save_path):
        """
        写allboundaries文件
        :param dx: dx
        :param dy: dy
        :param dz: dz
        :param save_path: save_path[0]应该存储有allboundaries.dat带文件名和后缀的完整保存路径
        :return: 无
        """
        x_array = dx.flatten('F')  # 因为原来idl代码是，先固定y，再变x的
        y_array = dy.flatten('F')
        z_array = dz.flatten('F')
        xyz = numpy.vstack([x_array, y_array, z_array])
        xyz = xyz.flatten('F')
        # file_path = os.path.join(save_path_list,'allboundaries.dat')
        file_path = save_path
        numpy.savetxt(file_path, xyz, fmt="%.6f",
                      delimiter="\n")  # https://numpy.org/doc/stable/reference/generated/numpy.savetxt.html

    # ============================================================

    def __read_b3dxyz_from_array_Bptr(self, Bp, Bt, Br):
        n_b3dx = Bp.shape
        n_b3dy = Bt.shape
        n_b3dz = Br.shape
        b3dx = Bp
        b3dy = -Bt
        b3dz = Br
        if (n_b3dx == n_b3dy) and (n_b3dx == n_b3dz):
            nx = n_b3dx[0]
            ny = n_b3dx[1]
        else:
            nx = 0
            ny = 0
        return b3dx, b3dy, b3dz, nx, ny

    def __change_b3dxyz_multiple_4(self, b3dx, b3dy, b3dz, nx, ny):
        nx_m = nx % 4
        ny_m = ny % 4
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
        b3dx = b3dx[nx_s:nx_e, ny_s:ny_e]
        b3dy = b3dy[nx_s:nx_e, ny_s:ny_e]
        b3dz = b3dz[nx_s:nx_e, ny_s:ny_e]
        nx = nx - nx_m
        ny = ny - ny_m
        # print(type(b3dx)) # <class 'numpy.ndarray'>
        # print(b3dx.shape)
        # print(nx,ny)
        nz_not_multiple_4 = int((nx + ny) * 3 / 8)
        nz_add_to_4 = int(4 - nz_not_multiple_4 % 4)
        nz = nz_not_multiple_4 + nz_add_to_4
        return b3dx, b3dy, b3dz, nx, ny, nz

    def prepare_from_fits_Bptr(self, Bp_path, Bt_path, Br_path, save_dir):
        """
        从Bp.fits,Bt.fits,Br.fits产生预处理数据
        :param p_raw_path: Bp.fits文件路径（需要包含文件名）
        :param t_raw_path: Bt.fits文件路径
        :param r_raw_path: Br.fits文件路径
        :param save_path_list: 保存预处理文件路径列表，第0个保存allboundaries.dat，第1个保存grid.ini带文件名和后缀的完整保存路径,第二个保存mask.dat路径
        :return: 无
        """
        bp_array = self.__read_fits_hdu1_data(Bp_path)
        bt_array = self.__read_fits_hdu1_data(Bt_path)
        br_array = self.__read_fits_hdu1_data(Br_path)
        b3dx, b3dy, b3dz, nx, ny = self.__read_b3dxyz_from_array_Bptr(bp_array, bt_array, br_array)
        self.__prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)
        return True

    def __base_rebin_half(self, m):
        m11 = m[0::2, 0::2]
        m12 = m[0::2,
              1::2]  # 前面表示行 后面表示列   0::2表示从0开始步长为2截取，即为奇数    0::2表示从0开始步长为2截取，即为偶数 https://blog.csdn.net/weixin_41147129/article/details/88058446
        m21 = m[1::2, 0::2]
        m22 = m[1::2, 1::2]
        m_new = (m11 + m12 + m21 + m22) / 4  # 可以这么做，必须保证m是偶数行和偶数列，否则截取的形状不一样，不能相加  即每四个田字格位置的元素平均成新一个元素，田字格不重叠
        return m_new

    def __change_b3dxyz_rebin(self, b3dx, b3dy, b3dz, nx, ny, nz):
        b3dx = self.__base_rebin_half(b3dx)
        b3dy = self.__base_rebin_half(b3dy)
        b3dz = self.__base_rebin_half(b3dz)
        nx = int(nx / 2)
        ny = int(ny / 2)
        nz = int(nz / 2)
        return b3dx, b3dy, b3dz, nx, ny, nz

    def __prepare_from_array_to_three(self, b3dx, b3dy, b3dz, nx, ny, save_dir):
        """afi 真正写入函数

        Args:
            Bp ([type]): [description]
            Bt ([type]): [description]
            Br ([type]): [description]
            save_path_list ([type]): [description]
        """
        if not os.path.isdir(save_dir):
            print("创建目录{}".format(save_dir))
            os.makedirs(save_dir)
        b3dx, b3dy, b3dz, nx, ny, nz = self.__change_b3dxyz_multiple_4(b3dx, b3dy, b3dz, nx, ny)
        save_path = os.path.join(save_dir, "allboundaries3.dat")
        self.__write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz, save_path)
        save_path = os.path.join(save_dir, "grid3.ini")
        self.__write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir, "mask3.dat")
        self.__write_errormask_to_maskdat(save_path, nx=nx, ny=ny, bx=b3dx, by=b3dy)
        #
        b3dx, b3dy, b3dz, nx, ny, nz = self.__change_b3dxyz_rebin(b3dx, b3dy, b3dz, nx, ny, nz)
        save_path = os.path.join(save_dir, "allboundaries2.dat")
        self.__write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz, save_path)
        save_path = os.path.join(save_dir, "grid2.ini")
        self.__write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir, "mask2.dat")
        self.__write_errormask_to_maskdat(save_path, nx=nx, ny=ny, bx=b3dx, by=b3dy)
        #
        b3dx, b3dy, b3dz, nx, ny, nz = self.__change_b3dxyz_rebin(b3dx, b3dy, b3dz, nx, ny, nz)
        save_path = os.path.join(save_dir, "allboundaries1.dat")
        self.__write_b3dxyz_to_allboundaries(b3dx, b3dy, b3dz, save_path)
        save_path = os.path.join(save_dir, "grid1.ini")
        self.__write_nxy_to_grid(nx, ny, nz, save_path)
        save_path = os.path.join(save_dir, "mask1.dat")
        self.__write_errormask_to_maskdat(save_path, nx=nx, ny=ny, bx=b3dx, by=b3dy)
        save_path = os.path.join(save_dir, "boundary.ini")
        self.__write_boundary_to_ini(save_path)

    def prepare_from_fits_afi(self, a_raw_path, f_raw_path, i_raw_path, save_dir):
        """
        从azimuth.fits,field.fits,inclination.fits产生预处理数据
        :param a_raw_path: azimuth.fits文件路径（需要包含文件名）
        :param f_raw_path: field.fits文件路径（需要包含文件名）
        :param i_raw_path: inclination.fits文件路径（需要包含文件名）
        :param save_path_list: 保存预处理文件路径列表，第0个保存allboundaries.dat，第1个保存grid.ini带文件名和后缀的完整保存路径
        :return: 无
        """
        a_hdul = fits.open(
            a_raw_path)  # 注意不要用with打开赋值返回，否则只保留头数据，没有二个数据域，默认只缓存第一个头  https://blog.csdn.net/zaq15csdn/article/details/81255269
        a_hdul.verify('silentfix')
        # 'silentfix'修复且无警告 'fix'修复但打印警告   https://github.com/astropy/astropy/blob/main/docs/io/fits/usage/verification.rst
        dict_header = dict(a_hdul[1].header)
        data_keys_frame_header = pandas.DataFrame([dict_header])
        f_hdul = fits.open(f_raw_path)
        i_hdul = fits.open(i_raw_path)
        data_object = disambiguation.CoordinateTransform(a_hdul, f_hdul, i_hdul, data_keys_frame_header)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)
        a_hdul.close()
        f_hdul.close()
        i_hdul.close()
        ## 从Bp Bt Br处理
        # pre_worker = prepare_worker.Preprocess()
        # print(bptr[:, :, 0].shape)
        # self.__prepare_from_array_Bptr(bptr[:, :, 0], bptr[:, :, 1], bptr[:, :, 2], save_path_list)
        # b3dx, b3dy, b3dz, nx, ny = self.__read_b3dxyz_from_array_Bptr(Bp,Bt,Br)
        b3dx, b3dy, b3dz, nx, ny = self.__read_b3dxyz_from_array_Bptr(bptr[:, :, 0], bptr[:, :, 1], bptr[:, :, 2])
        self.__prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)

    def prepare_from_fits_afid(self, a_raw_path, f_raw_path, i_raw_path, d_raw_path, save_dir):
        """
        从azimuth.fits,field.fits,inclination.fits产生预处理数据
        :param a_raw_path: azimuth.fits文件路径（需要包含文件名）
        :param f_raw_path: field.fits文件路径（需要包含文件名）
        :param i_raw_path: inclination.fits文件路径（需要包含文件名）
        :param save_path_list: 保存预处理文件路径列表，第0个保存allboundaries.dat，第1个保存grid.ini带文件名和后缀的完整保存路径
        :return: 无
        """
        a_hdul = fits.open(
            a_raw_path)  # 注意不要用with打开赋值返回，否则只保留头数据，没有二个数据域，默认只缓存第一个头  https://blog.csdn.net/zaq15csdn/article/details/81255269
        a_hdul.verify('silentfix')
        # 'silentfix'修复且无警告 'fix'修复但打印警告   https://github.com/astropy/astropy/blob/main/docs/io/fits/usage/verification.rst
        dict_header = dict(a_hdul[1].header)
        data_keys_frame_header = pandas.DataFrame([dict_header])
        f_hdul = fits.open(f_raw_path)
        i_hdul = fits.open(i_raw_path)
        d_hdul = fits.open(d_raw_path)
        basic_obj = disambiguation.Basic(recordset=None, method=2)  # 尽量少修改代码原则，他原来github代码很怪，先产生对象，再把对象传递给静态方法
        a_hdul_have_d = disambiguation.Basic.perform_disambiguation(basic_obj, a_hdul, d_hdul)
        data_object = disambiguation.CoordinateTransform(a_hdul_have_d, f_hdul, i_hdul, data_keys_frame_header)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)
        a_hdul.close()
        f_hdul.close()
        i_hdul.close()
        d_hdul.close()
        ## 从Bp Bt Br处理
        # pre_worker = prepare_worker.Preprocess()
        # print(bptr[:, :, 0].shape)
        b3dx, b3dy, b3dz, nx, ny = self.__read_b3dxyz_from_array_Bptr(bptr[:, :, 0], bptr[:, :, 1], bptr[:, :, 2])
        self.__prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)

    def prepare_from_fits_afid_online(self, save_dir):
        """
        在线下载数据并处理，仅仅演示，实际不使用
        :param save_path_list: 保存预处理文件路径列表，第0个保存allboundaries.dat，第1个保存grid.ini带文件名和后缀的完整保存路径
        :return:
        """
        ### 网络下载 azimuth field inclination disambiguation  因为第四个好像没有给，只能网上下载完整的四个

        ## 先变成Bp Bt Br
        # fetch the data from JSOC by providing a recordset specification and a disambiguation method
        query_info = disambiguation.Basic('hmi.sharp_720s[377][2011.02.15_00:00:00]', 2)
        keys, azimuth, field, inclination, disambig = disambiguation.Basic.get_data(query_info)

        # disambiguate the azimuthal component of the magnetic field
        disambiguated_azimuth = disambiguation.Basic.perform_disambiguation(query_info, azimuth, disambig)

        # construct the field vector in spherical coordinate components on the CCD grid
        data_object = disambiguation.CoordinateTransform(disambiguated_azimuth, field, inclination, keys)
        # print(data_object)
        latlon, bptr = disambiguation.CoordinateTransform.ccd(data_object)

        ## 从Bp Bt Br处理
        # save_allboundaries_path = r"C:\Users\Zander\PycharmProjects\sun\nlfff\data\result\allboundaries.dat"
        # save_grid_path = r"C:\Users\Zander\PycharmProjects\sun\nlfff\data\result\grid.ini"
        # save_path_list = [save_allboundaries_path, save_grid_path]
        # print(bptr[:, :, 0].shape)
        b3dx, b3dy, b3dz, nx, ny = self.__read_b3dxyz_from_array_Bptr(bptr[:, :, 0], bptr[:, :, 1], bptr[:, :, 2])
        self.__prepare_from_array_to_three(b3dx, b3dy, b3dz, nx, ny, save_dir)
        print("预处理完成 demo_fun_use_afid_online")


####################################################3333
### 下面是演示测试函数 #####
def demo_fun_use_Bptr():
    # 配置文件
    # p_raw_path = r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bp.fits"
    # t_raw_path = r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bt.fits"
    # r_raw_path = r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_cea_720s.377.20110215_020000_TAI.Br.fits"
    rroot = r"/public1/home/sc81826/run/nlfff-main/run_space/tool/data"
    p_raw_path = rroot + "/hmi.sharp_cea_720s.3700.20140203_133600_TAI.Bp.fits"
    t_raw_path = rroot + "/hmi.sharp_cea_720s.3700.20140203_133600_TAI.Bt.fits"
    r_raw_path = rroot + "/hmi.sharp_cea_720s.3700.20140203_133600_TAI.Br.fits"

    # # sharp_cea_720s.377.20110215_020000_TAI.Br.fits
    # p_raw_path = rroot+"/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bp.fits"
    # t_raw_path = rroot+"/hmi.sharp_cea_720s.377.20110215_020000_TAI.Bt.fits"
    # r_raw_path = rroot+"/hmi.sharp_cea_720s.377.20110215_020000_TAI.Br.fits"

    # 配置保存文件所在目录
    # save_path_list = r"C:\Users\Zander\PycharmProjects\sun\nlfff\data"
    sroot = r"/public1/home/sc81826/temp/out"
    # save_allboundaries_path = sroot+"/allboundaries.dat"
    # save_grid_path = sroot+"/grid.ini"
    # save_mask_path = sroot+"/mask.dat"
    # save_path_list = [save_allboundaries_path,save_grid_path,save_mask_path]
    # 创建对象
    pre_worker = Preprocess()
    # 执行预先处理
    pre_worker.prepare_from_fits_Bptr(p_raw_path, t_raw_path, r_raw_path, sroot)
    print("预处理完成 demo_fun_use_Bptr_local")


def demo_fun_use_afi():
    save_dir = r"/public1/home/sc81826/temp/out"
    # save_allboundaries_path = a11+"/allboundaries.dat"
    # save_grid_path = a11+"/grid.ini"
    # save_mask_path = a11+"/mask.dat"

    # save_path_list = [save_allboundaries_path, save_grid_path,save_mask_path]
    dd = r"/public1/home/sc81826/archive/selAR/2019/hmi.sharp_720s.7334.20190124_124800_TAI"
    a = dd + "/hmi.sharp_720s.7334.20190124_124800_TAI.azimuth.fits"
    f = dd + "/hmi.sharp_720s.7334.20190124_124800_TAI.field.fits"
    i = dd + "/hmi.sharp_720s.7334.20190124_124800_TAI.inclination.fits"
    # a=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.azimuth.fits"
    # f=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.field.fits"
    # i=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.inclination.fits"

    pre_worker = Preprocess()
    pre_worker.prepare_from_fits_afi(a, f, i, save_dir)
    print("预处理完成 demo_fun_use_afi_local")


def demo_fun_use_afid():
    save_dir = r"/public1/home/sc81826/temp/out"
    # save_allboundaries_path = a11+"/allboundaries.dat"
    # save_grid_path = a11+"/grid.ini"
    # save_mask_path = a11+"/mask.dat"

    # save_path_list = [save_allboundaries_path, save_grid_path,save_mask_path] # azimuth field inclination disambig
    dd = r"/public1/home/sc81826/run/nlfff-main/run_space/tool/data"
    a = dd + "/hmi.sharp_720s.7300.20180823_173600_TAI.azimuth.fits"
    f = dd + "/hmi.sharp_720s.7300.20180823_173600_TAI.field.fits"
    i = dd + "/hmi.sharp_720s.7300.20180823_173600_TAI.inclination.fits"
    d = dd + "/hmi.sharp_720s.7300.20180823_173600_TAI.disambig.fits"
    # a=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.azimuth.fits"
    # f=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.field.fits"
    # i=r"/media/zander/Data/now/work-inner/sun/nlfff/data/hmi.sharp_720s.1.20100504_160000_TAI.inclination.fits"

    pre_worker = Preprocess()
    pre_worker.prepare_from_fits_afid(a, f, i, d, save_dir)
    print("预处理完成 demo_fun_use_afi_local")


if __name__ == "__main__":
    print("test")
    demo_fun_use_Bptr()
    demo_fun_use_afi()
    demo_fun_use_afid()
