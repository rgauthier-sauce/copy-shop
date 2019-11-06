from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='copyshop',
    version='0.1.0',
    description='Tool for the Sauce Labs support teams.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rgauthier-sauce/copy-shop',
    author='Romain Gauthier',
    author_email='romain.gauthier@saucelabs.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='saucelabs copy-shop saucesupport',
    python_requires='>=3.5',
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'copyshop=copyshop:main',
        ],
    }
)
