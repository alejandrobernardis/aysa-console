# Author: Alejandro M. Bernardis
# Email: alejandro.bernardis at gmail.com
# Created: 2019/10/12
# ~

import aysa_console
from os import path
from io import open
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=aysa_console.__title__,
    version=aysa_console.__version__,
    description=aysa_console.__summary__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=aysa_console.__uri__,
    author=aysa_console.__author__,
    author_email=aysa_console.__email__,
    keywords='docker registry services development deployment',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.6.*, <4',

    package_data={
        '': ['LICENSE', 'README.md'],
        'aysa_console': ['config.toml']
    },

    install_requires=[
        'bcrypt==3.1.7',
        'certifi==2019.9.11',
        'cffi==1.13.2',
        'chardet==3.0.4',
        'cryptography==2.8',
        'docopt==0.6.2',
        'dotted==0.1.8',
        'fabric==2.5.0',
        'idna==2.8',
        'invoke==1.3.0',
        'paramiko==2.6.0',
        'prompt-toolkit==2.0.10',
        'pycparser==2.19',
        'pynacl==1.3.0',
        'requests==2.22.0',
        'six==1.13.0',
        'tomlkit==0.5.8',
        'urllib3==1.25.8',
        'wcwidth==0.1.7'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],

    entry_points={
        'console_scripts': [
            'aysax=aysa_console:main',
        ],
    },

    project_urls={
        'Bug Reports': aysa_console.__issues__,
        'Source': aysa_console.__uri__,
    },

)
