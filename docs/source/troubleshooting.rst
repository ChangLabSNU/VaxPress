Troubleshooting (FAQ)
***********************

-------------------------------
iCodon scoring does not work.
-------------------------------

If ``R``, ``rpy2`` and ``iCodon`` are not installed (see :ref:`installation <label-installing>`), iCodon-predicted stability fitness function will automatically be silenced.
If iCodon score does not appear in the optimization report, check if they are installed::
    
    # check if rpy2 is installed
    python
    >>> import rpy2.robjects.packages as rpackages
    # If ModuleNotFoundError is raised, rpy2 is not installed.

    >>> rpackages.importr('iCodon')
    # If PackageNotInstalledError is raised, iCodon is not installed.



