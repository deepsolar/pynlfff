# coding=utf-8
"""
Purpose:   [1] download data Bp Bt Br from jsoc
           [2] Demonstrate sunpy for jsoc basic usage,
               Officially already has a good package, this is just a demonstration of basic use

Usage:     This code depends on the requests bs4 lxml zeep drms sunpy astropy
           They can be installed from conda or pip
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) Edit Python code From Thomas Wiegelmann (2022.03)
"""
# This code is compatible with python 3.7.x.
# python3 -m pip install requests
# python3 -m pip install bs4  # https://stackoverflow.com/questions/11783875/importerror-no-module-named-bs4-beautifulsoup
# python3 -m pip install lxml
# python3 -m pip install zeep
# python3 -m pip install drms  # https://docs.sunpy.org/projects/drms/en/stable/
# python3 -m pip install sunpy
# python3 -m pip install astropy
from sunpy.net import Fido, attrs as a
import astropy.units as u
from concurrent.futures import ProcessPoolExecutor
import os


class DownloadJsoc():

    def __init__(self):

        self.is_print_log = True  # or False not print log

        self.mail_address_list = []  # eg ["demo@demo.com","demo2@demo.com"]
        #  You need to go to the following location URL to register the mailbox filled in the following list,
        #  so that when multi-threaded, it will not affect the download, because a user can only request once at a time
        #  http://jsoc.stanford.edu/ajax/exportdata.html
        # ---
        #  Note that this email address has a service period (it may be two months),
        # beyond which you need to re-register on the official website
        #  Note that the number of requests or downloads of the same ip is also limited,
        # otherwise the ip may be blocked, you need to apply for unblocking,
        # you may also automatically unblock after a long time, it is recommended that a small number of requests,
        # a single search request a large amount of data

        self.data_save_root_path = None  # eg r"C:\Users\Zander\PycharmProjects\pynlfff\pyproduct\test"

    def download_one_by_time_point(self, timepoint, harpnum, email=None, save_path=None):
        """
        Download the file based on the point in time
        :param timepoint: eg "2010-01-01T00:00:00.000"
        :param harpnum: eg "220"
        :param email: eg "eg@eg.com" register at http://jsoc.stanford.edu/ajax/exportdata.html
        :param save_path: str path
        :return: None
        """
        result = False
        try:
            if email is None:
                if isinstance(self.mail_address_list, list) and len(self.mail_address_list) > 0:
                    email = self.mail_address_list[0]
            if save_path is None:
                if os.path.exists(self.data_save_root_path):
                    save_path = self.data_save_root_path

            search_tuple = (
                a.Time(timepoint, timepoint),  # set same start time and end time is like to download this time point

                a.jsoc.Series("hmi.sharp_cea_720s"),
                # choose series  http://jsoc.stanford.edu/JsocSeries_DataProducts_map.html

                a.jsoc.Notify(email),  # a.jsoc.Notify("eg@gmail.com"),

                a.jsoc.Segment("Bp"),
                a.jsoc.Segment("Bt"),
                a.jsoc.Segment("Br"),

                a.jsoc.PrimeKey("HARPNUM", str(harpnum)),

                # a.jsoc.Keyword("LON_MIN") > -70, # JSOC keyword filtering with Fido  https://docs.sunpy.org/en/stable/whatsnew/3.1.html?highlight=t_rec#jsoc-keyword-filtering-with-fido
                # a.jsoc.Keyword("LON_MAX") < 70, # Note You can only filter numbers, not strings

                # a.Sample(96 * u.min), # time delta, need set time range before
            )

            results = Fido.search(*search_tuple)  # search for result
            downloaded_files = Fido.fetch(results, path=save_path)  # download result
            result = downloaded_files  # return result
        except BaseException as e:
            print(e)
        return result

    def download_one_by_time_range(self, timestart, timeend, harpnum, timedelta=96, email=None, save_path=None):
        """
        download by time range and delta
        :param timestart: str eg "2010-01-01T00:00:00.000"
        :param timeend:  str eg "2022-01-01T00:00:00.000"
        :param harpnum: str eg "235"
        :param timedelta: int eg 96
        :param email: str eg "eg@eg.com"
        :param save_path: str path which to save file
        :return: result set or False
        """
        result = False
        try:
            if email is None:
                if isinstance(self.mail_address_list, list) and len(self.mail_address_list) > 0:
                    email = self.mail_address_list[0]
            if save_path is None:
                if os.path.exists(self.data_save_root_path):
                    save_path = self.data_save_root_path
            search_tuple = (
                a.Time(timestart, timeend),
                # set time range, if want use delta must set this ("2010-01-01T00:00:00.000", "2022-01-01T00:00:00.000"),

                a.jsoc.Series("hmi.sharp_cea_720s"),
                # choose series  http://jsoc.stanford.edu/JsocSeries_DataProducts_map.html

                a.jsoc.Notify(email),  # a.jsoc.Notify("eg@gmail.com"),

                a.jsoc.Segment("Bp"),  # choose segment
                a.jsoc.Segment("Bt"),
                a.jsoc.Segment("Br"),

                a.jsoc.PrimeKey("HARPNUM", str(harpnum)),

                # a.jsoc.Keyword("LON_MIN") > -70, # JSOC keyword filtering with Fido  https://docs.sunpy.org/en/stable/whatsnew/3.1.html?highlight=t_rec#jsoc-keyword-filtering-with-fido
                # a.jsoc.Keyword("LON_MAX") < 70,

                a.Sample(timedelta * u.min),  # eg a.Sample(96 * u.min) time delta, need set time range before
            )

            results = Fido.search(*search_tuple)
            downloaded_files = Fido.fetch(results, path=save_path)
            result = downloaded_files
        except BaseException as e:
            print(e)
        return result

    def __download_one_by_time_point_concurrent(self, timepoint, harpnum, job_num=0, save_path=None):
        # harpnum = harpnum  # "7302"
        # stime=timepoint # "2018-09-08T14:24:00.000"
        print('job num: {} / pid : {} is runing\n'.format(job_num, os.getpid()))
        email_len = len(self.mail_address_list)
        mail_num = job_num % email_len
        result = self.download_one_by_time_point(timepoint, harpnum, self.mail_address_list[mail_num], save_path)
        return result

    def download_some_by_time_point(self, timepoint_list, harpnum_list):
        """

        :param timepoint_list:
        :param harpnum_list:
        :return:
        """
        result = []
        t_len = len(timepoint_list)
        h_len = len(harpnum_list)
        if t_len == h_len:
            for i in range(t_len):
                this_result = self.download_one_by_time_point(timepoint_list[i], harpnum_list[i])
                result.append(this_result)
        return result

    def download_some_by_time_point_concurrent(self, timepoint_list, harpnum_list):
        """
        Give a list of times and numbers to download data in parallel,Note that the two dimensions should be consistent
        :param timepoint_list: eg ["2018-09-08T14:24:00.000","2018-09-08T00:00:00.000"]
        :param harpnum_list: eg ["7020","7020"]
        :return: None
        """
        result = []
        t_len = len(timepoint_list)
        h_len = len(harpnum_list)
        if t_len == h_len:
            max_workers = len(self.mail_address_list)
            executor = ProcessPoolExecutor(max_workers=max_workers)
            for i in range(t_len):
                future = executor.submit(
                    self.__download_one_by_time_point_concurrent,
                    timepoint_list[i],
                    harpnum_list[i],
                    i)
                result.append(future)
            executor.shutdown(True)

    def tran_json_file_tai_num_time_to_download_format(self, raw_str):
        """
        Convert the file time downloaded by json to the parameter time required for download,
        eg "7020.20170524_222400_TAI" to ["7020","2018-09-08T14:24:00.000"]
        Both in the list are in str format
        :param raw_str: str, eg "7020.20170524_222400_TAI"
        :return:  [ str, str ] -> [ harpnum , timestr ], eg ["7020","2018-09-08T14:24:00.000"],
        If the over-feed value is malformed, the conversion fails and is returned None，
        """
        result = None
        if isinstance(raw_str, str):
            str_list = raw_str.split(".")  # split by . to ["7020","20170524_222400_TAI"]
            if len(str_list) == 2:
                if len(str_list[1]) >= 15:
                    try:
                        hnum = int(str_list[0])  # try if list[1] is not int
                        this_list = str_list[1]
                        stime = "20{}-{}-{}T{}:{}:00.000".format(
                            this_list[2:4],
                            this_list[4:6],
                            this_list[6:8],
                            this_list[9:11],
                            this_list[11:13],
                        )  # "2018-09-08T14:24:00.000"
                        result = [hnum, stime]
                    except BaseException as e:
                        print(e)
        return result

    def get_job_list_from_file(self, file_path):
        """
        The file content is like "7020.20170524_000000_TAI\n7020.20170524_222400_TAI\n"
        :param file_path: str or os.path format
        :return:  ["7020.20170524_000000_TAI","7020.20170524_222400_TAI"]
        """
        result = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                all_list = f.read().split("\n")
            result = all_list
        return result

    def demo_download_one(self):
        self.download_one_by_time_point("2018-08-23T17:36:00.000", "7300",email="eg@eg.com",save_path="/data")

    def demo_download_some_from_file(self, file_path=None, save_path=None, mail_list=None):
        """
        get work job from file and run concurrent
        The file content is like "7020.20170524_000000_TAI\n7020.20170524_222400_TAI\n"
        :param file_path: str or os.path format
        :param save_path: the path to save file
        :param mail_list: ["eg@eg.com","eg2@eg2.com"] which has registered in jsoc before
        :return:  None
        """
        if file_path is None:
            return False
        if file_path is not None:
            self.data_save_root_path = save_path
        if mail_list is not None:
            self.mail_address_list = mail_list

        job_raw_list = self.get_job_list_from_file(file_path)
        num_list = []
        time_list = []
        for job_raw in job_raw_list:
            job_tran = self.tran_json_file_tai_num_time_to_download_format(job_raw)
            if job_tran is not None:
                num_list.append(job_tran[0])
                time_list.append(job_tran[1])
        self.download_some_by_time_point_concurrent(time_list, num_list)



if __name__ == "__main__":
    print("start run")

    d = DownloadJsoc()
    file_path = r"/www/wwwroot/app_run/data/a"
    save_path = r"/www/wwwroot/app_run/data"
    mail_list = ["xxx@foxmail.com",
                 "xxx@outlook.com",
                 "xxxx@outlook.com",
                 "xxxxx@outlook.com", ]
    d.demo_download_some_from_file(file_path, save_path, mail_list)



