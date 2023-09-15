Adding a custom scoring function
*************************************
You can extend VaxPress optimization algorithm by adding custom scoring functions that contributes to the fitness evaluation of each sequence. 
Example codes showing templates for additional scoring functions are in ``VaxPress/examples`` directory. 
After preparing a python code for the new scoring function, you can add it to the optimization process with two ways:  

-------------------------------
Using a command line option 
-------------------------------
Pass the path to the Python source file for the scoring function as an argument of ``-—addon`` option. 
If there are multiple scoring functions to add, ``-—addon`` can be specified multiple times.
::
    # Example command to add homotrimer count to the fitness evaluation

    vaxpress -i ./testseq/vegfa.fa\
             -o ../test_run\
             --iterations 500\
             --lineardesign 1\
             --lineardiesign-dir ../LinearDesign\
             --conservative-start 10[:7]\
			 --addon ./VaxPress/examples/count_homotrimers.py



--------------------------------------------
Install along with the VaxPress package
--------------------------------------------

Another way is to reinstall VaxPress after adding a new scoring function to the source directory. 
Since reinstalling makes the new scoring function incorporated as part of VaxPress’ default scoring functions, 
this method is recommended when the new scoring function is to be used continuously.

1) First, git clone VaxPress directory
2) Add the scoring function .py file inside ``VaxPress/vaxpress/scoring/`` directory.
3) Reinstall VaxPress (``pip install .`` from the root directory of VaxPress.).

.. code-block:: bash
    
    git clone https://github.com/ChangLabSNU/VaxPress.git
    cd VaxPress
    pip install .

4) Run VaxPress: After reinstalling, you don’t need to specify ``--addon`` separately.