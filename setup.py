from setuptools import setup, find_packages
read_file = lambda x: [l.strip() for l in open(x).readlines()]

setup(
    name='liveprofiler',
    author='Piotr Szymanski',
    author_email='piotr.szymanski@fieldaware.com',
    url='https://github.com/fieldaware/liveprofiler',
    license='MIT',
    version='1.0.0',
    description='Package for profiling WSGI applications on production',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=read_file('requirements.txt'),
    include_package_data=True,
    package_data={
        'static': 'liveprofiler/static/*',
        'templates': 'liveprofiler/templates/*'
    },
)
