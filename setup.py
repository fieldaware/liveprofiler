from setuptools import setup, find_packages
read_file = lambda x: [l.strip() for l in open(x).readlines()]

setup(
    name='liveprofiler',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file("requirements.txt"),
)
