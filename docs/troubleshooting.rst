Troubleshooting
***************

------------------------
iCodon option is missing
------------------------

The predicted in-cell stability fitness function based on iCodon
will only load if *R,* *rpy2,* and *iCodon* are correctly installed.
To install these, please refer to the provided :doc:`installation
instructions <installation>`. To verify the installation,
execute the command below::

    python -c 'from rpy2.robjects.packages import importr; importr("iCodon")'
    # No output indicates success
