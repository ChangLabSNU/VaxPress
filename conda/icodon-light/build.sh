#!/bin/bash
patch -p1 < ${RECIPE_DIR}/minimal-icodon.diff
${R} -e "install.packages('.', repos=NULL, type='source')"
