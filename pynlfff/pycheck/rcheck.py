"""
Purpose:   [1] this project, pynlfff , may not use all function in computer machine
                For example, computer machines may not need the image function
                Therefore, to separate the different function dependencies to achieve mitigation,
                the role of this package is to check whether the package dependencies required
                for different functions are installed


Usage:     This code depends on None
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) 

"""
import os
import subprocess
import sys

class RCheck():
    """
    check pynlfff some function needed module is install or not
    """

    def __init__(self, version="0.3.x", print_try_log=True,try_install=True):
        """
        version default now, can use for different version test latter,
        print test log can show display or not
        :param version: default now version
        :param print_try_log: default True,show try log
        """
        self.version = version
        self.__data_is_load = False
        self.__requirements_list = []
        self.__load_data()
        self.print_try_log = print_try_log  # print log or not
        self.try_install=try_install

    def __load_data(self):
        """
        load data by version
        :return: None
        """
        if self.version.startswith("0.2"):
            self.__data_v02()
        if self.version.startswith("0.3"):
            self.__data_v03()
        else:
            print("no that version: {}".format(self.version))

    def __data_v02(self):
        """
        load v02 data
        :return: None
        """
        self.__full_list = [
            ["pandas", "", ""],  # 0
            ["astropy", "", ""],  # 1
            ["numpy", "", ""],  # 2
            ["sunpy", "", ""],  # 3
            ["drms", "", ""],  # 4
            ["h5py", "", ""],  # 5
            ["matplotlib", "", ""],  # 6



        ]
        d = self.__full_list
        self.__requirements_base = [d[2]]
        self.__requirements_prepare = [d[0], d[1], d[2], d[3], d[4]]
        self.__requirements_computer = [d[7]]
        self.__requirements_product = [d[5], d[2]]
        self.__requirements_plot = [d[5], d[6], d[2]]

        self.__requirements_list = [
            self.__full_list,  # 0
            self.__requirements_base,  # 1
            self.__requirements_prepare,  # 2
            self.__requirements_computer,  # 3
            self.__requirements_product,  # 4
            self.__requirements_plot,  # 5
        ]
        self.__data_is_load = True

    def __data_v03(self):
        """
        load v02 data
        :return: None
        """
        self.__full_list = [
            ["pandas", "", ""],  # 0
            ["astropy", "", ""],  # 1
            ["numpy", "", ""],  # 2
            ["sunpy", "", ""],  # 3
            ["drms", "", ""],  # 4
            ["h5py", "", ""],  # 5
            ["matplotlib", "", ""],  # 6
            ["psutil", "", ""],  # 7

            ["requests", "", ""],  # 8
            ["bs4", "", ""],  # 9
            ["lxml", "", ""],  # 10
            ["zeep", "", ""],  # 11

            ["wget", "", ""],  # 12
            ["peewee", "", ""],  # 13
            ["vtk", "", ""],  # 14
            
            # ["", "", ""],  # 
        ]
        d = self.__full_list
        self.__requirements_base = [d[2]]
        self.__requirements_prepare = [d[0], d[1], d[2], d[3], d[4]]
        self.__requirements_computer = []
        self.__requirements_product = [d[5], d[2]]
        self.__requirements_plot = [d[5], d[6], d[2], d[14]]
        self.__requirements_download = [d[1],d[3],d[4],d[8], d[9], d[10], d[11]]
        self.__requirements_label = [d[2],d[12],d[13]]


        self.__requirements_list = [
            self.__full_list,  # 0
            self.__requirements_base,  # 1
            self.__requirements_prepare,  # 2
            self.__requirements_computer,  # 3
            self.__requirements_product,  # 4
            self.__requirements_plot,  # 5
            self.__requirements_download, # 6
            self.__requirements_label, # 7
        ]
        self.__data_is_load = True
        
    def h(self):
        """
        print help
        :return: None
        """
        self.help()

    def help(self):
        """
        print help
        :return: None
        """
        help_str = """This module is to test some module, for pynlfff which function you need, is install or not.
    Can use RCheck().check() or RCheck().check(0) for Full module test
    RCheck().check(1) for Base function module test 
    RCheck().check(2) for Prepare function module test 
    RCheck().check(3) for Computer function module test 
    RCheck().check(4) for Product function module test 
    RCheck().check(5) for Plot function module test 
    RCheck().check(6) for Download fits raw data function module test 
    RCheck().check(7) for Label function module test 
    """  # Full Base  Prepare  Computer Product  Plot
        print(help_str)

    def check_one_module_exists_by_try(self, model_name):
        """
        test module is install or not
        :param model_name: str, this is import name
        :return: True or False
        """
        # model_name = 'time'
        result = False
        try:
            log = __import__(model_name)
            if self.print_try_log:
                print(log)
            result = True
        except BaseException as e:
            if self.print_try_log:
                print(e)
        return result

    def check_one_module(self, model_detail_list):
        """
        check one module by module list
        :param model_detail_list: like ["module_name_str","..."],index 0 is name ,other dev latter
        :return: [module_name,exists_str]
        """
        model_name = model_detail_list[0]

        exists_str = "Need Install"
        is_exists = self.check_one_module_exists_by_try(model_name)
        if self.print_try_log:
            print(is_exists)
        if is_exists:
            exists_str = "Exists"

        result = [model_name, exists_str]
        return result

    def check(self, num=0):
        """
        given function index num to check this function's requirements is install or not,
        the num can use RCheck().help() or RCheck().h() to get details.
        :param num: int 0 to 5, 0:Full 1:Base  2:Prepare  3:Computer 4:Product  5:Plot 6:Download raw fits 7:Label
        :return: print result and return test list , error num will return False
        """
        result = False
        if 0 <= num < len(self.__requirements_list):
            check_list = self.__requirements_list[num]
            result_list = []
            if self.print_try_log:
                print("Start Test")
            for check_model_detail_list in check_list:
                this_result = self.check_one_module(check_model_detail_list)
                result_list.append(this_result)
            if self.print_try_log:
                print("Test Finish, Result: {}".format(result_list))
                
            if self.try_install:
                install_fail_list=[]
                for r in result_list:
                    if self.print_try_log:
                        print(r)
                    if r[1]=="Need Install":
                        try:
                            # os.system("{} -m pip install {}".format(sys.executable,r[0]))
                            command="{} -m pip install {}".format(sys.executable,r[0])
                            ret=subprocess.run(command, shell=True)
                            if ret.returncode==0:
                                print("install sucess {}".format(r[0]))
                            else:
                                print("install fail {}".format(r[0]))
                                install_fail_list.append(r)
                        except BaseException as e:
                            print(e)
                if len(install_fail_list)>0:
                    print("=====\ninstall fail: {}".format(install_fail_list))
            result = result_list
        else:
            print("ERROR num: {}\ntry use function RCheck.h() or RCheck.help()".format(num))
        return result


if __name__ == "__main__":
    print("start test")
    # rc=RCheck()
    # RCheck(print_try_log=False).h()
    RCheck(print_try_log=False).check()
