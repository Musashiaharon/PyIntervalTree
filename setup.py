"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Distribution logic

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2013-2014 Chaim-Leib Halbert

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import os
import errno
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import re
try:
    import pandoc
except ImportError as e:
    print(e)
pandoc.PANDOC_PATH = 'pandoc'  # until pyandoc gets updated


## CONFIG
version = '1.0.2'
create_rst = True


## PyTest
# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # import here, because outside the required eggs aren't loaded yet
        sys.exit(pytest.main(self.test_args))


def get_rst():
    if os.path.isdir('pyandoc/pandoc') and os.path.islink('pandoc'):
        print("Generating README.rst from README.md")
        return generate_rst()
    elif os.path.isfile('README.rst'):
        print("Reading README.rst")
        return read_file('README.rst')
    else:
        print("No README.rst found!")
        return read_file('README.md')

## Convert README to rst for PyPI
def generate_rst():
    """Converts Markdown to RST for PyPI"""
    md = read_file("README.md")

    md = pypi_sanitize_markdown(md)
    rst = markdown2rst(md)
    rst = pypi_prepare_rst(rst)

    # Write it
    if create_rst:
        update_file('README.rst', rst)
    else:
        rm_f('README.rst')

    return rst


def markdown2rst(md):
    """Convert markdown to rst format using pandoc. No other processing."""
    doc = pandoc.Document()
    doc.markdown_github = md
    rst = doc.rst

    return rst


## Sanitizers
def pypi_sanitize_markdown(md):
    """Prepare markdown for conversion to PyPI rst"""
    md = chop_markdown_header(md)
    md = remove_markdown_links(md)

    return md


def pypi_prepare_rst(rst):
    """Add a notice that the rst was auto-generated"""
    head = ".. This file is automatically generated by setup.py from README.md.\n\n"
    rst = head + rst

    return rst


def chop_markdown_header(md):
    """
    Remove empty lines and travis-ci header from markdown string.
    :param md: input markdown string
    :type md: str
    :return: simplified markdown string data
    :rtype: str
    """
    md = md.splitlines()
    while not md[0].strip() or md[0].startswith('[!['):
        md = md[1:]
    md = '\n'.join(md)
    return md


def remove_markdown_links(md):
    """PyPI doesn't like links, so we remove them."""
    # named links, e.g. [hello][url to hello] or [hello][]
    md = re.sub(
        r'\[((?:[^\]]|\\\])+)\]'    # link text
        r'\[((?:[^\]]|\\\])*)\]',   # link name
        '\\1',
        md
    )

    # url links, e.g. [example.com](http://www.example.com)
    md = re.sub(
        r'\[((?:[^\]]|\\\])+)\]'    # link text
        r'\(((?:[^\]]|\\\])*)\)',   # link url
        '\\1',
        md
    )

    return md


## Filesystem utilities
def read_file(path):
    """Reads file into string."""
    with open(path, 'r') as f:
        data = f.read()
    return data


def mkdir_p(path):
    """Like `mkdir -p` in unix"""
    if not path.strip():
        return
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def rm_f(path):
    """Like `rm -f` in unix"""
    try:
        os.unlink(path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise


def update_file(path, data):
    """Writes data to path, creating path if it doesn't exist"""
    # delete file if already exists
    rm_f(path)

    # create parent dirs if needed
    parent_dir = os.path.dirname(path)
    if not os.path.isdir(os.path.dirname(parent_dir)):
        mkdir_p(parent_dir)

    # write file
    with open(path, 'w') as f:
        f.write(data)


## Run setuptools
setup(
    name='intervaltree',
    version=version,
    install_requires=[],
    description='Mutable, self-balancing interval tree',
    long_description=get_rst(),
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup',
    ],
    keywords="interval-tree data-structure intervals tree",  # Separate with spaces
    author='Chaim-Leib Halbert, Konstantin Tretyakov',
    author_email='chaim.leib.halbert@gmail.com',
    url='https://github.com/chaimleib/intervaltree',
    download_url='https://github.com/chaimleib/intervaltree/tarball/' + version,
    license="Apache",
    packages=find_packages(exclude=['test', 'pandoc', 'docutils']),
    include_package_data=True,
    zip_safe=True,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points={}
)
