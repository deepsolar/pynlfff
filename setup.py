import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pynlfff',
    version='0.4.2.3',
    description='python for nlfff',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/deepsolar/pynlfff',
    author='ZhongRui Zhao, Xinze Zhang',
    author_email='zhaozhongrui21@mails.ucas.ac.cn',
    license='MIT',
    keywords='python nlfff',
    packages=find_packages(),
    install_requires=['numpy', 'h5py', 'matplotlib'],
    # scripts=['pynlfff/cnlfff/wiegelmann_nlfff/init_compile_ps.sh'],
    package_data={'pynlfff': ['cnlfff/wiegelmann_nlfff/*']},
    include_package_data=True,
    python_requires='>=3'
)
