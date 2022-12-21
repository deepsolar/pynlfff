
# Toolkit Use

## Nlfff file reading and writing

### Create Object

```python
from pynlfff.pyproduct import file

r=file.NlfffFile()
```



### Read data

#### Read size from grid

```python
r = file.NlfffFile()

grid_path = r"\product0\grid3.ini"
s = r.get_size_from_grid(grid_path)
print(s)
```

```
[96, 228, 124]
```



#### Read Bout

Method 1: Given `Bout.bin` and the corresponding `grid.ini` file

```python
r = file.NlfffFile()

bout_bin_path = r"\product0\Bout.bin"
grid_path = r"\product0\grid3.ini"

s = r.read_bin(bout_bin_path, grid_path=grid_path)
print(s.shape)
print(s)
```

```
(3, 96, 228, 124)
[[[[ -4.85755745  -3.69001267  -4.07361282 ...  -0.26802718
     -0.26802718  -0.26802718]
   [ -2.37227954  -3.32715352  -4.60636354 ...  -0.26799428
     -0.26799428  -0.26799428]
   [  3.09420419  -2.96429436  -5.13911427 ...  -0.26796139
     -0.26796139  -0.26796139]
   ...
   ...
   [  7.94384187   6.06213112   4.73552989 ...  -0.45711367
     -0.45711367  -0.45711367]
   [  2.05455194   4.55914711   4.73552989 ...  -0.45711367
     -0.45711367  -0.45711367]
   [  7.05974157   4.55914711   4.73552989 ...  -0.45711367
     -0.45711367  -0.45711367]]]]
```

Method 2: Given `Bout.bin` and the corresponding `nx`, `ny`, `nz` values

```python
r = file.NlfffFile()

bout_bin_path = r"\product0\Bout.bin"
nx=96
ny=228
nz=124

s = r.read_bin(bout_bin_path, nx=nx,ny=ny,nz=nz)
print(s.shape)
print(s)
```


### Write data

#### Convert file format to hdf5

Method 1: Given `Bout.bin` and the corresponding `grid.ini` file, and the `hdf` file save path

```python
r = file.NlfffFile()

bout_bin_path = r"\product0\Bout.bin"
grid_path = r"\product0\grid3.ini"
h5_path = r"\product0\Bxyz.h5"
r.tran_bin2hdf5(bout_bin_path, h5_path, grid_path=grid_path, overwrite=True)
```

Method 2: Given `Bout.bin` and the corresponding `nx`, `ny`, `nz` values, and the `hdf` file save path

```python
r = file.NlfffFile()
bout_bin_path = r"\product0\Bout.bin"
h5_path = r"\product0\Bxyz.h5"

nx=96
ny=228
nz=124

r.tran_bin2hdf5(bout_bin_path, h5_path, nx=nx,ny=ny,nz=nz, overwrite=True)
```

#### Write array data

```python
r = file.NlfffFile()

array_data = np.random.uniform(-5, 5, size=(3, 100,50,40))
h5_path = r"\product0\Bxyz.h5"
r.write_hdf5(array_data, h5_path, overwrite=True)
```









