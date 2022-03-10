# 准备包(pyprepare)

## 检查依赖包(rcheck)

### RCheck类(检查依赖)

#### 查看帮助

```python
import pynlfff

ck=pynlfff.RCheck()
ck.help()
```

```
This module is to test some module, for pynlfff which function you need, is install or not.
    Can use RCheck().check() or RCheck().check(0) for Full module test
    RCheck().check(1) for Base function module test 
    RCheck().check(2) for Preprocess function module test 
    RCheck().check(3) for Computer function module test 
    RCheck().check(4) for Product function module test 
    RCheck().check(5) for Plot function module test 
```

#### 检查依赖

```python
import pynlfff

ck=pynlfff.RCheck()
ck.check()  # 查看所有依赖
```

```
Start Test
<module 'pandas' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\pandas\\__init__.py'>
<module 'astropy' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\astropy\\__init__.py'>
<module 'numpy' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\numpy\\__init__.py'>
<module 'sunpy' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\sunpy\\__init__.py'>
<module 'drms' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\drms\\__init__.py'>
<module 'h5py' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\h5py\\__init__.py'>
<module 'matplotlib' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\matplotlib\\__init__.py'>
Test Finish, Result: [['pandas', 'Exists'], ['astropy', 'Exists'], ['numpy', 'Exists'], ['sunpy', 'Exists'], ['drms', 'Exists'], ['h5py', 'Exists'], ['matplotlib', 'Exists']]
['pandas', 'Exists']
['astropy', 'Exists']
['numpy', 'Exists']
['sunpy', 'Exists']
['drms', 'Exists']
['h5py', 'Exists']
['matplotlib', 'Exists']

Process finished with exit code 0

```



```python
import pynlfff

# ck=pynlfff.pyprepare.rcheck.RCheck()
ck=pynlfff.RCheck()
ck.help()
ck.check(4) # 和产品相关的包
```

```
Start Test
<module 'h5py' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\h5py\\__init__.py'>
<module 'numpy' from 'C:\\ProgramData\\Anaconda3\\envs\\pylinff\\lib\\site-packages\\numpy\\__init__.py'>
Test Finish, Result: [['h5py', 'Exists'], ['numpy', 'Exists']]
['h5py', 'Exists']
['numpy', 'Exists']

Process finished with exit code 0
```





