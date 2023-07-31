/*
 * Python interface for LinearFold
 *
 * Copyright 2023 Hyeshik Chang
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * “Software”), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
 * THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define main _linearfold_main
#define lv
#define is_cube_pruning
#define is_candidate_list
#include "LinearFold.cpp"
#undef main

PyDoc_STRVAR(linearfold_fold_doc,
"fold(seq)\n\
\n\
Return the MFE structure and free energy predicted by LinearFold.");

static PyObject *
linearfold_fold(PyObject *self, PyObject *args)
{
    const char *seq;
    Py_ssize_t len;

    if (!PyArg_ParseTuple(args, "s#:fold", &seq, &len))
        return NULL;

    /* LinearFold arguments */
    const int beamsize = 100;
    const bool sharpturn = false;
    const bool is_verbose = false;
    const bool zuker_subopt = false;
    const float energy_delta = 5.0;
    const string shape_file_path = "";
    const bool fasta = false;
    const int dangles = 2;

    string rna_seq(seq);

    /* Call LinearFold */
    BeamCKYParser parser(beamsize, !sharpturn, is_verbose, false, zuker_subopt,
                         energy_delta, shape_file_path, fasta, dangles);
    BeamCKYParser::DecoderResult result = parser.parse(rna_seq, NULL);

    double score = result.score / -100.0;

    return Py_BuildValue("(s#d)", result.structure.c_str(), len, score);
}

static PyMethodDef linearfold_methods[] = {
    {"fold",             linearfold_fold,         METH_VARARGS,
        linearfold_fold_doc},
    {NULL,              NULL}           /* sentinel */
};

PyDoc_STRVAR(module_doc,
"CPython interface to LinearFold");

static struct PyModuleDef linearfoldmodule = {
    PyModuleDef_HEAD_INIT,
    "linearfold",
    module_doc,
    0,
    linearfold_methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit_linearfold(void)
{
    return PyModuleDef_Init(&linearfoldmodule);
}
