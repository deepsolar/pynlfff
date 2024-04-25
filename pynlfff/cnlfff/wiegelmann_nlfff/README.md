
# NLFFF

## CPU version


## GPU version

### amd arch

```bash
PROJECTDIR=./
GRID=123

bash ./init_compile_ps_amd.sh
bash ./compiled.gpu.nvcc.amd/multigrid.sh  $PROJECTDIR $GRID

# this program need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this

```


### arm arch

```bash
PROJECTDIR=./
GRID=123

bash ./init_compile_ps_arm.sh
bash ./compiled.gpu.nvcc.arm/multigrid.sh  $PROJECTDIR $GRID

# this program need 2 parameter  
# 1 workspace path, which allboundaries123.dat grid123.ini mask123.dat boundary.ini etc. in it
# 2 which grid computer now, can be 1 12 123 2 23 3 , pay attenction if set 2 it has been run grid 1 before
# and need other app compiled bin in root along with this
```



```latex
@article{Wiegelmann2012Nov,
    author = {Wiegelmann, T. and Thalmann, J. K. and Inhester, B. and Tadesse, T. and Sun, X. and Hoeksema, J. T.},
    title = {{How Should One Optimize Nonlinear Force-Free Coronal Magnetic Field Extrapolations from SDO/HMI Vector Magnetograms?}},
    journal = {Sol. Phys.},
    volume = {281},
    number = {1},
    pages = {37--51},
    year = {2012},
    month = nov,
    issn = {1573-093X},
    publisher = {Springer Netherlands},
    doi = {https://doi.org/10.1007/s11207-012-9966-z}
}
```

## GPU Version

```latex
@misc{Zhang2024,
  author = {Xinze, Zhang and Zhongrui Zhao},
  title = {The cuda version for nlfff},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/deepsolar/pynlfff}},
}
```



