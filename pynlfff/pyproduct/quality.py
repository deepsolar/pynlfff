# coding=utf-8
"""
Purpose:   [1] check nlfff product quality


Usage:     This code depends on the os re
           The first two libraries are in the standard distribution.
           This code is compatible with python 3.7.x.

Examples:  None Now

Adapted:   ZhaoZhongRui (zhaozhongrui21@mails.ucas.ac.cn) Edit Python (2022.03)

"""

import os
import re


class QualityCheck():
    """
    check nlfff quality
    """

    def __init__(self, quality_max=30):
        self.quality_ok_value_max = quality_max  # 30

    def check_quality_from_bin(self):
        """
        check from bin
        :return:
        """
        # TODO
        return False

    def check_quality_from_log(self, file_path):
        """
        Detect whether the file degree angle is greater than 30,
        greater than 30 or the file is empty, return False,
        otherwise True
        :param file_path: NLFFFquality3.log path
        :return:
        """
        result = False
        if os.path.exists(file_path):
            with open(file_path, 'r')as f:
                file_data = f.read()
            # print(file_data)
            pattern = r'Angle.*?Degree'
            match = re.findall(pattern, file_data)
            # print(match)
            p = r'\d+\.?\d+'
            nums = re.findall(p, str(match))
            if len(nums) == 0:
                result = False
            else:
                result = True
                for num in nums:
                    if float(num) > self.quality_ok_value_max:
                        result_n = False
                    else:
                        result_n = True
                    result = result and result_n  # ensure every value is ok
        return result
