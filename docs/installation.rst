************
Installation
************

You can install VaxPress using *Pip,* *Conda,* or *Singularity.* *Pip* is
the recommended method for advanced users. The *Conda* package
simplifies the installation of necessary dependencies. The *Singularity*
container image runs just out of the box if your computing environment
already has *Singularity* installed.

.. note::
    **Optional Installation of LinearDesign**

    VaxPress can be integrated with *LinearDesign* for optimal coding
    sequence design that offers superior performance and versatility.
    To access these features, install *LinearDesign* separately. For
    information, see :ref:`installing-lineardesign`.

.. _label-installing:

=============================
Installing VaxPress using Pip
=============================

**Installing**
::

    # Create a virtual environment for VaxPress
    python -m venv /path/to/vaxpress-env

    # Activate the virtual environment
    source /path/to/vaxpress-env/bin/activate

    # Install VaxPress alone
    pip install vaxpress

    # Alternatively, install VaxPress with LinearFold (only for non-commercial uses)
    pip install 'vaxpress[nonfree]'

**Running**
::

    # Activate the virtual environment
    source /path/to/vaxpress-env/bin/activate

    # Run VaxPress
    vaxpress -h

.. note::
    **Optional Dependencies for Installations using Pip**

    If you wish to activate the iCodon predicted stability
    (``--iCodon-weight``) in the fitness function, ensure you have
    working installations of *R,* *rpy2* (version >= 3.0) and
    *iCodon.*  For detailed installation instructions, visit
    `iCodon's GitHub page <https://github.com/santiago1234/iCodon/>`_.

===============================
Installing VaxPress using Conda
===============================

**Installing**
::

    conda install -n vaxpress -y -c changlabsnu -c bioconda -c conda-forge vaxpress

**Running**
::

    # Activate the environment
    conda activate vaxpress

    # Run VaxPress
    vaxpress -h

================================
Running VaxPress via Singularity
================================

To run VaxPress via Singularity, you will need to install the
`Singularity CE <https://sylabs.io/singularity/>`_ first.

**Downloading the Image**

Download the container image from `the GitHub project page
<https://github.com/ChangLabSNU/VaxPress/releases>`_ and place it in a
directory of your choice.

**Running**
::

    singularity vaxpress.sif -h

.. warning::
    For ease of use, it's advised to store the VaxPress container
    image and all your input/output files in a directory within your
    home directory. If placed elsewhere, you might have to use the
    ``--bind`` option with *Singularity* each time you run the container.
    For detailed guidance, refer to `the Singularity documentation
    <https://sylabs.io/guides/latest/user-guide/bind_paths_and_mounts.html>`_.


.. _installing-lineardesign:

=======================
Installing LinearDesign
=======================

To utilize the ``--lineardesign`` options, you need to have *LinearDesign*
installed in addition to VaxPress. For installation guidance, visit
`the LinearDesign GitHub page
<https://github.com/LinearDesignSoftware/LinearDesign>`_.  Indicate
the path to the *LinearDesign* directory using the ``--lineardesign-dir``
option in the command line. This path will be stored in the
configuration file and will be activated as the default for subsequent
runs.

Further information on the ``--lineardesign`` options can be found in
:ref:`using-lineardesign`.
