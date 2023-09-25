************
Installation
************

Vaxpress can be installed with ``pip``, ``conda``, or ``singularity``.
Pip is simple and easy to use since it can be operated in single command line, but ``R``, ``rpy2`` and ``iCodon`` dependencies should be managed separately.
Using conda package also allows the installation with single command line, and all the dependencies will managed automatically in this case. But it'll be quite slow compared to other ways.
Lastly, Singularity is fast, and automatically manages all dependencies. But Singularity should be installed first.
Based on your own circumstance, select proper way to install Vaxrpess!

.. _label-installing:

===============================
Installing VaxPress via ``pip``
===============================

.. note::
    **Prerequisites**

    If you install VaxPress via pip, ``R``, ``rpy2`` (version >= 3.0) and ``iCodon`` aren't included as dependencies.
    If you want to utilize iCodon's predicted stability in the fitness function, you'll need to install these separately.
    For iCodon installation, see `iCodon's GitHub page <https://github.com/santiago1234/iCodon/>`_.

**Installation**
::
    
    # To install using pip
    pip install vaxpress

    # To install using pip with LinearFold (only for non-commercial uses)
    pip install 'vaxpress[nonfree]'

    # To install from the Github
    git clone https://github.com/ChangLabSNU/VaxPress.git
    cd VaxPress
    pip install .

=========================================
Installing Vaxpress via ``conda`` package
=========================================
**Installation**
::

    conda install -c changlabsnu -c bioconda -c conda-forge vaxpress

=======================================
Installing Vaxpress via ``Singularity``
=======================================
.. note::
    **Prerequisite**

    To install VaxPress via Singularity, you will need to install `Singularity CE <https://sylabs.io/singularity/>`_ first.

**Installation**
Once Singularity is installed, you can download the VaxPress image from this GitHub repository and run using the following command:
::

    singularity vaxpress.sif ...

It is recommended that VaxPress be installed in a virtual environment to be controlled properly.
See `the python documentation for preparing virtual environments <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`_

===========================
Installing ``LinearDesign``
===========================

To use ``--lineardesign`` options, ``LinearDesign`` installation is required apart from VaxPress installation.
You can follow the instructions on the LinearDesign's `LinearDesign GitHub Page <https://github.com/LinearDesignSoftware/LinearDesign>`_.