# coding=utf-8

"""
Purpose:   [1] plot the nlfff product (hdf format) to picture

Usage:     This code depends on the numpy h5py matplotlib
           The first librarie is in the standard Anaconda distribution.
           The h5py matplotlib library can be obtained from pip
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) Edit Python (2022.03)

"""

import numpy as np
import matplotlib.pyplot as plt
import h5py
import time


class NlfffPlotD3CutCake():
    """
    Draw a portion slice, like cut a cake
    """

    def __init__(self, *args, **kwargs):
        """
        init this function,you can set some values for matplotlib.pyplot.figure
        eg: d3_drawer=NlfffPlotD3CutCake(figsize=(6,9))
        :param args:
        :param kwargs:
        """

        # set colormap
        self.color_map = None # eg plt.get_cmap('coolwarm')
        self.colormap_set_max = 0  # colormap will show range [colormap_max,colormap_min]
        self.colormap_set_min = 0
        self.colormap_alpha = "auto" # None or auto or float, eg 0.8  set for global transparency
        self.colormap_out_range_display=True #True #False #True  # set True , Values that exceed the range are compressed to the maximum value instead of not being displayed
        self.colormap_auto_value = True  # auto change colormap_max,colormap_min by real value
        self.colormap_auto_zip = 0.8  # range (0 - 1]  for zip [colormap_max,colormap_min] , and 1 is not zip
        self.colormap_auto_mirror = True # If set True, and the maximum minimum value is positive and negative, respectively, then the final value becomes about 0 symmetry
        self.colorbar_show = True  # show colorbar in picture
        self.cut_line_edges = dict(color='0.6', linewidth=0.6, zorder=1e3)  # if you set None,it will not plot the lines
        self.cut_line_cross = dict(color='0.4', linewidth=1, zorder=1e3)

        # inner use
        self.__cut_list = []  # for add cut job
        self.__hdf_path = None  # for add path
        self.full_data_array = None
        self.set_default_cmap()


    def set_default_cmap(self):
        lut=8
        if self.color_map is None:
            self.color_map=plt.get_cmap('coolwarm',lut=lut)
        if self.colormap_alpha == "auto":
            a = np.append(np.linspace(0, 1, int(lut / 2)), np.linspace(1, 0, int(lut / 2)))
            self.color_map.set_gamma(a)


    def load_data_array(self, array_data):
        """
        load data from array
        :param array_data: numpy.ndarray shape like (3,Nx,Ny,Nz)
        :return:load sucessfully return True, error type or shape return False
        """
        result = False
        if isinstance(array_data, np.ndarray):
            if len(array_data.shape) == 4:
                self.full_data_array = array_data
                result = True
        return result

    def load_data_hdf(self, hdf_path):
        """
        given the path of hdf, it will load the data inner for next step use
        :param hdf_path: str or os.path
        :return: open sucessfully return True else return False
        """
        if self.__hdf_path is not None:
            self.close_data_hdf()
        try:
            self.__hdf_path = hdf_path
            self.__hf = h5py.File(self.__hdf_path, 'r')
            self.full_data_array = self.__hf[self.data_hdf_dataset_name]  # four D
            # print(self.full_data_array[0]) # three D
            # print(type(self.full_data_array[0])) #<class 'numpy.ndarray'>
            result = True
        except BaseException as e:
            print(e)
            result = False
        return result

    def close_data_hdf(self):
        """
        close the hdf file which haven open
        :return:
        """
        result = False
        try:
            self.__hf.close()
            result = True
        except BaseException as e:
            print(e)
        # time.sleep(100)
        return result

    def add_cut(self, B="Bx", N="Nx", cut_num=None, cut_percent=0.5):
        """
        when you haven load hdf data,
        add cut surface for cut draw, which can be use many times for different surfance in one picture
        :param B: 'Bx' 'By' or 'Bz'; choose one Magnetic field component to draw
        :param N: 'Nx' 'Ny' or 'Nz'; choose cut in which angle; when choose 'Nz', The slice will be perpendicular to z axis
        :param cut_num: int type , set for cut where, can be [0, max(axis)], if not set this,will use cut_percent default
        :param cut_percent: default 0.5, percent of axis
        :return: None
        """
        this_cut_dict = dict(B=B, N=N, cut_percent=cut_percent, cut_num=cut_num)
        self.__cut_list.append(this_cut_dict)

    def run_cut(self,
                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html
                fig_dict=dict(figsize=[6, 6],dpi=300.0),

                view_dict=None,

                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html
                is_show=True,
                show_dict=dict(block=True),

                # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html
                is_save=False,
                save_dict=dict(fname="./cut.png", dpi='figure')
                ):
        """
        when you haven load data and add_cut ,
        run cut for computer data and prepare for draw
        :return: None
        """
        # computer shape
        # set fig and you can use it outside like : d3_drawer.fig.XXX
        self.fig = plt.figure(**fig_dict)

        # set draw view and you can use it outside like : d3_drawer.ax.view_init(40, -30)
        self.ax = self.fig.add_subplot(projection='3d')
        ## Set distance and angle view
        if view_dict is None:
            elev=45
            azim=45
            dist=11
        else:
            elev=view_dict["elev"]
            azim=view_dict["azim"]
            dist=view_dict["dist"]
        self.ax.view_init(elev, azim)
        self.ax.dist = dist
        # self.ax.view_init(-40, 30)
        # self.ax.dist = 11
        self.data_hdf_dataset_name="Bxyz"
        ## Set labels and zticks
        self.ax.set(
            xlabel='X',
            ylabel='Y',
            zlabel='Z',
        )

        data_shape = self.full_data_array[0].shape
        self.__Nx = data_shape[1]
        self.__Ny = data_shape[0]
        self.__Nz = data_shape[2]
        self.__X, self.__Y, self.__Z = np.meshgrid(np.arange(self.__Nx), np.arange(self.__Ny), np.arange(self.__Nz))

        # prepare job
        contourf_list = []  # for draw dict
        x_value_list = []  # for cut line
        y_value_list = []
        z_value_list = []
        for cut in self.__cut_list:
            if cut["B"] == "Bx":
                bxyz_num = 0
            elif cut["B"] == "By":
                bxyz_num = 1
            elif cut["B"] == "Bz":
                bxyz_num = 2
            else:
                break
            if cut["N"] == "Nx":
                if cut["cut_num"] is not None and 0 <= cut["cut_num"] <= self.__Nx:  # set direct value
                    x_value = int(cut["cut_num"])
                else:
                    x_value = int(self.__Nx * cut["cut_percent"])  # computer value by percent
                data1_x = self.full_data_array[bxyz_num][:, x_value, :]
                if self.colormap_auto_value:  # set auto for computer max and min
                    self.colormap_set_max = max(self.colormap_set_max, data1_x.max())
                    self.colormap_set_min = min(self.colormap_set_min, data1_x.min())
                data2_y = self.__Y[:, x_value, :]
                data3_z = self.__Z[:, x_value, :]
                draw_job_dict = dict(X=data1_x, Y=data2_y, Z=data3_z, zdir="x", offset=x_value)
                contourf_list.append(draw_job_dict)
                x_value_list.append(x_value)  # for draw cut line
            elif cut["N"] == "Ny":
                if cut["cut_num"] is not None and 0 <= cut["cut_num"] <= self.__Ny:
                    y_value = int(cut["cut_num"])
                else:
                    y_value = int(self.__Ny * cut["cut_percent"])
                data1_x = self.__X[y_value, :, :]
                data2_y = self.full_data_array[bxyz_num][y_value, :, :]
                if self.colormap_auto_value:
                    self.colormap_set_max = max(self.colormap_set_max, data2_y.max())
                    self.colormap_set_min = min(self.colormap_set_min, data2_y.min())
                data3_z = self.__Z[y_value, :, :]
                draw_job_dict = dict(X=data1_x, Y=data2_y, Z=data3_z, zdir="y", offset=y_value)
                contourf_list.append(draw_job_dict)
                y_value_list.append(y_value)
            elif cut["N"] == "Nz":
                if cut["cut_num"] is not None and 0 <= cut["cut_num"] <= self.__Nz:
                    z_value = int(cut["cut_num"])
                else:
                    z_value = int(self.__Nz * cut["cut_percent"])
                data1_x = self.__X[:, :, z_value]
                data2_y = self.__Y[:, :, z_value]
                data3_z = self.full_data_array[bxyz_num][:, :, z_value]
                if self.colormap_auto_value:
                    self.colormap_set_max = max(self.colormap_set_max, data3_z.max())
                    self.colormap_set_min = min(self.colormap_set_min, data3_z.min())
                draw_job_dict = dict(X=data1_x, Y=data2_y, Z=data3_z, zdir="z", offset=z_value)
                contourf_list.append(draw_job_dict)
                z_value_list.append(z_value)
        if 1 > self.colormap_auto_zip > 0 and self.colormap_auto_value:  # for zip color map
            c_min = self.colormap_set_min * self.colormap_auto_zip
            c_max = self.colormap_set_max * self.colormap_auto_zip
        else:
            c_min = self.colormap_set_min
            c_max = self.colormap_set_max

        if self.colormap_auto_mirror and c_min*c_max < 0: # set True, and the maximum minimum value is positive and negative
            max_abs=max(abs(c_max),abs(c_min))
            c_max=max_abs
            c_min=-max_abs

        kw = {
            'vmin': c_min,
            'vmax': c_max,
            # 'levels': np.linspace(c_min, c_max, 10),
            'cmap': self.color_map,
            # "c": np.linspace(c_min, c_max, 10) / 2550,

            # 'alpha': self.colormap_alpha,
        }
        if c_min != c_max: # if same will raise error
            kw["levels"]=np.linspace(c_min, c_max, 19)
        if isinstance(self.colormap_alpha,float) and 0<self.colormap_alpha <1:
            kw["alpha"]=self.colormap_alpha

        # draw
        cut_obj_list = []  # cut obj  for band colorbar and other use
        for cut_job in contourf_list:
            if self.colormap_out_range_display:
                if cut_job["zdir"] == "x":
                    cut_job["X"] = np.clip(cut_job["X"], a_min=c_min, a_max=c_max)
                elif cut_job["zdir"] == "y":
                    cut_job["Y"] = np.clip(cut_job["Y"], a_min=c_min, a_max=c_max)
                elif cut_job["zdir"] == "z":
                    cut_job["Z"] = np.clip(cut_job["Z"], a_min=c_min, a_max=c_max)
            cut_job.update(kw)  # add common dict
            cut_obj = self.ax.contourf(**cut_job)
            cut_obj_list.append(cut_obj)

        # set axis
        xmin, xmax = 0, self.__Nx
        ymin, ymax = 0, self.__Ny
        zmin, zmax = 0, self.__Nz
        self.ax.set(xlim=[xmin, xmax], ylim=[ymin, ymax], zlim=[zmin, zmax])

        # draw line
        x_value_len = len(x_value_list)
        y_value_len = len(y_value_list)
        z_value_len = len(z_value_list)
        # for cut_line_cross
        if isinstance(self.cut_line_cross, dict):
            edges_kw = self.cut_line_cross
            ax = self.ax
            if y_value_len and z_value_len:  # if len is 0 , it is False
                for y_value in y_value_list:
                    for z_value in z_value_list:
                        ax.plot([xmin, xmax], [y_value, y_value], [z_value, z_value], **edges_kw)
            if x_value_len and z_value_len:
                for x_value in x_value_list:
                    for z_value in z_value_list:
                        ax.plot([x_value, x_value], [ymin, ymax], [z_value, z_value], **edges_kw)
            if x_value_len and y_value_len:
                for x_value in x_value_list:
                    for y_value in y_value_list:
                        ax.plot([x_value, x_value], [y_value, y_value], [zmin, zmax], **edges_kw)
        # for cut_line_edges
        if isinstance(self.cut_line_edges, dict):
            edges_kw = self.cut_line_edges
            ax = self.ax
            if x_value_len:
                for x_value in x_value_list:
                    ax.plot([x_value, x_value], [ymin, ymin], [zmin, zmax], **edges_kw)
                    ax.plot([x_value, x_value], [ymax, ymax], [zmin, zmax], **edges_kw)
                    ax.plot([x_value, x_value], [ymin, ymax], [zmin, zmin], **edges_kw)
                    ax.plot([x_value, x_value], [ymin, ymax], [zmax, zmax], **edges_kw)
            if y_value_len:
                for y_value in y_value_list:
                    ax.plot([xmin, xmax], [y_value, y_value], [zmin, zmin], **edges_kw)
                    ax.plot([xmin, xmax], [y_value, y_value], [zmax, zmax], **edges_kw)
                    ax.plot([xmin, xmin], [y_value, y_value], [zmin, zmax], **edges_kw)
                    ax.plot([xmax, xmax], [y_value, y_value], [zmin, zmax], **edges_kw)
            if z_value_len:
                for z_value in z_value_list:
                    ax.plot([xmin, xmin], [ymin, ymax], [z_value, z_value], **edges_kw)
                    ax.plot([xmax, xmax], [ymin, ymax], [z_value, z_value], **edges_kw)
                    ax.plot([xmin, xmax], [ymin, ymin], [z_value, z_value], **edges_kw)
                    ax.plot([xmin, xmax], [ymax, ymax], [z_value, z_value], **edges_kw)

        # add color bar
        if len(cut_obj_list) > 0 and self.colorbar_show:
            self.fig.colorbar(cut_obj_list[0], ax=self.ax, fraction=0.02, pad=0.1)  # , label='Name [units]')
        if is_save:
            plt.savefig(**save_dict)
        if is_show:
            plt.show(**show_dict)
        
