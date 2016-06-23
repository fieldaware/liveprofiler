import io
from setuptools import setup, find_packages
read_file = lambda x: [l.strip() for l in open(x).readlines()]

setup(
    name='liveprofiler',
    author='Piotr Szymanski',
    author_email='piotr.szymanski@fieldaware.com',
    url='https://github.com/fieldaware/liveprofiler',
    license='MIT',
    version='0.1.0',
    description='Package for profiling WSGI applications on production',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    packages=find_packages(),
    install_requires=read_file('requirements.txt'),
    include_package_data=True,
    package_data={
        'static': 'liveprofiler/static/*',
        'templates': 'liveprofiler/templates/*'
    },
)
