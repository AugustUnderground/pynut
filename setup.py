from setuptools import setup, find_packages

package_name = 'pynut'

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as req:
    requirements = req.read().splitlines()

setup( name                          = package_name
     , version                       = '0.0.1'
     , author                        = 'Yannick Uhlmann'
     , author_email                  = 'augustunderground@pm.me'
     , description                   = 'Binary NutMeg reader'
     , long_description              = long_description
     , long_description_content_type = 'text/markdown'
     , url                           = 'https://github.com/augustunderground/pynut'
     , packages                      = find_packages()
     , classifiers                   = [ 'Development Status :: 2 :: Pre-Alpha'
                                       , 'Programming Language :: Python :: 3'
                                       , 'Operating System :: POSIX :: Linux' ]
     , python_requires               = '>=3.8'
     , install_requires              = requirements
     #, entry_points                  = { 'console_scripts': [ 'FIXME' ]}
     , package_data                  = { '': ['*.hy', '*.coco', '__pycache__/*']}
     , )
