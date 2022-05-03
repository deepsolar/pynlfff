import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pynlfff',
    version='0.2.2',
    description='python for nlfff',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ZanderZhao/pynlfff',
    author='ZhaoZhongRui',
    author_email='zhaozhongrui21@mails.ucas.ac.cn',
    license='MIT',
    keywords='python nlfff',
    packages=[
        # 'pynlfff.pydownload',
        'pynlfff.pyprepare',
        'pynlfff.pypreprocess',
        # 'pynlfff.pycomputer',
        'pynlfff.pyproduct',
        'pynlfff.pyplot',
    ],
    install_requires=['numpy', 'h5py', 'matplotlib'],
    python_requires='>=3'
)
