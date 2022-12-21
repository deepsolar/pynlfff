
# register in https://pypi.org/

# --------------------------------
# upload tar
python setup.py sdist upload

# upload wheel
python setup.py bdist_wheel upload

# -------------------------------
pip install twine
twine upload dist/*



# https://zhuanlan.zhihu.com/p/115302375
# https://blog.csdn.net/m0_52571715/article/details/109713536