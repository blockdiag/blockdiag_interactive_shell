from setuptools import setup, find_packages
import sys

install_requires = [
    'setuptools',
    'flask',
    'actdiag',
    'blockdiag',
    'blockdiagcontrib-square',
    'blockdiagcontrib-qb',
    'blockdiagcontrib-class',
    'netdiag',
    'seqdiag',
    'pypng',
]
if sys.version_info < (2, 6):
    install_requires.append('simplejson')

setup(
    name = 'gae_blockdiag',
    version = '2011.4.27',
    packages = find_packages('app'),
    package_dir = {'': 'app'},
    #package_data = {'': ['buildout.cfg']},
    #include_package_data = True,
    install_requires = install_requires,
    entry_points = {
        'paste.app_factory': [
            'main=main:app_factory',
        ],
    },
)

