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

from distutils.core import setup
from distutils.extension import Extension

setup(name='vaxpress',
      version='0.1',
      description='Codon Optimizer for mRNA Vaccine Design',
      author='Hyeshik Chang',
      author_email='hyeshik@snu.ac.kr',
      url='https://github.com/ChangLabSNU/VaxPress',
      packages=['vaxpress', 'vaxpress.scoring'],
      entry_points={
        'console_scripts': [
            'vaxpress = vaxpress.__main__:run_vaxpress',
        ],
      },
      ext_modules=[
        Extension(
            'vaxpress.linearfold',
            ['src/linearfoldmodule.cc'],
            include_dirs=['contrib/LinearFold/src'],
        )],
     )
