#!/bin/bash

set -e

TMP_F=$(mktemp -p .)
ERR=0

if ! ../extract_metabolite_tax.py input.xml > "${TMP_F}"
then
    echo "FAILED: ../extract_metabolite_tax.py completed with error"
    ERR=1
fi

if ! diff expected.txt "${TMP_F}"
then
    echo "FAILED: actual output does not match expected!"
    ERR=1
fi

if [ ${ERR} -eq 0 ]
then
    echo "TEST PASSED"
fi

rm "${TMP_F}"
exit ${ERR}
