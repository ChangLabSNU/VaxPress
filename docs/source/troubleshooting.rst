Troubleshooting (FAQ)
***********************

-------------------
iCodon scoring does not work.
-------------------

If ``R``, ``rpy2`` and ``iCodon`` are not installed(see :ref:`prerequisites`), iCodon-predicted stability fitness function will automatically be silenced.
If iCodon score does not appear in the optimization report, check if they are installed::
    # check if rpy2 is installed
    $ python
    >>> from rpy2.robjects.packages import importr
    >>> importr('iCodon')



