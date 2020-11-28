"""A super secure voting machine app.

Copyright(C) Peter Jackson Link III.

This file is part of Voting Machine.

    Voting Machine is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Voting Machine is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Voting Machine.  If not, see <https://www.gnu.org/licenses/>.
"""

from setuptools import setup, find_packages


readme_file = open('README.rst')

setup(
    name='voting_machine',
    version='0.0.0a0',
    packages=find_packages(),
    description=__doc__,
    long_description=readme_file.read(),
    long_description_content_type='text/x-rst',
    install_requires=[
        'flask',
        'requests'
    ],
    include_package_data=True,
    license='GPLv3 OR LATER'
)

readme_file.close()
