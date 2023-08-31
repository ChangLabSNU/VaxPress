#
# VaxPress
#
# Copyright 2023 Hyeshik Chang
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# “Software”), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from setuptools import setup

setup(
    name='vaxpress',
    version='0.3',
    description='Codon Optimizer for mRNA Vaccine Design',
    author='Hyeshik Chang',
    author_email='hyeshik@snu.ac.kr',
    url='https://github.com/ChangLabSNU/VaxPress',
    download_url='https://github.com/ChangLabSNU/VaxPress/releases',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=[
        'mRNA vaccine',
        'messenger RNA',
        'codon optimization'
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    packages=['vaxpress', 'vaxpress.scoring', 'vaxpress.data'],
    package_data={'vaxpress': ['report_template/*']},
    data_files=[('share/vaxpress/examples',
        ['examples/count_homotrimers.py', 'examples/restriction_site.py'])],
    entry_points={
        'console_scripts': [
            'vaxpress = vaxpress.__main__:run_vaxpress',
        ],
    },
    install_requires=[
        'biopython >= 1.5',
        'numpy >= 1.15',
        'pandas >= 2.0',
        'pytrf >= 1.0.1',
        'rpy2 >= 3.0',
        'ViennaRNA >= 2.4',
        'tqdm >= 4.0',
        'tabulate >= 0.9',
        'Jinja2 >= 3.1',
        'plotly >= 5.0',
        'pylru >= 1.2',
    ],
    extras_require={
        'nonfree': ['linearfold-unofficial'],
    },
)
