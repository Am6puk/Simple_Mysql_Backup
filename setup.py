__author__ = 'Am6puk'
#!/usr/bin/env python
"""
simple_backup setup file
"""

from distutils.core import setup

import glob


install_requires = [
    'mysql-python>=1.2.3',
    'argparse',
    'ConfigParser'
]

setup(
      name='simple_backup',
      version='0.1.3',
      description='Simple Mysql Backup',
      author='Andrey Rozhkov',
      author_email='am6puk@gmail.com',
      url='http://unixhelp.org/',
      long_description=open('README.md').read(),
      license='MIT License',
      zip_safe=False,
      platforms='any',
      install_requires=install_requires,
      package_dir={'': 'src'},
      packages=['simple_backup', 'simple_backup.modules', 'simple_backup.app'],
      scripts=glob.glob('src/simple-backup'),
      classifiers=[
            'License :: OSI Approved :: MIT License',
            'Environment :: Console',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Database',
            'Topic :: Utilities'
        ],
      data_files=[
            ('/etc/simple_backup',  glob.glob('./conf/*.conf')),
      ],
      keywords = 'mysql dump hotcopy',
)
