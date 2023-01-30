import os
from subprocess import Popen, PIPE

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()


def get_git_version(default="v0.0.1"):
    try:
        p = Popen(['git', 'describe', '--tags'], stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        line = line.strip()
        return line.decode()
    except:
        return default

with open('README.md', 'r') as fd:
    long_description = fd.read()

setup(
    name='adsgcon',
    version=get_git_version(default="v0.0.1"),
    classifiers=['Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8'],
    url='http://github.com/adsabs/ADSGoogleConnector/',
    license='GPL-3.0',
    author='NASA/SAO ADS',
    description='File handling and manipulation for Google Drive and Sheets',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=required
)
