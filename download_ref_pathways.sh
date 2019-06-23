#!/bin/bash

set -e

###############################################################################################
##                                                                                           ##
## retrieves references pathways together with their linked compounds from the KEGG database ##
##                                                                                           ##
###############################################################################################


function output_spec(){
    F="${1}"
    FNR="${2}"
    EXCLUDE="${3:-}"

    head -1 "${F}" | awk -F "\t" '{
            rs = ""
            for(i = 1; i <= NF; ++i){
                if(i != exclude){
                    if(rs != ""){
                        rs = rs ","
                    }

                    rs = rs fnr "." i
                }
            }

            print rs
        }' fnr="${FNR}" exclude="${EXCLUDE}"
}


function merge_keep_left(){
    F1="${1}"
    F2="${2}"
    C1="${3}"
    C2="${4}"

    O="$(output_spec "${F1}" "1"),$(output_spec "${F2}" "2" "${C2}")"
    join -t "	" -i --header -o "${O}" -1 ${C1} -2 ${C2} -a 1 \
        <(head -1 "${F1}"; tail -n +2 "${F1}" | sort -t "	" -f -k${C1},${C1}) \
        <(head -1 "${F2}"; tail -n +2 "${F2}" | sort -t "	" -f -k${C2},${C2})
}



function download_to_tmp_file(){
    URL="${1}"
    FN=$(mktemp -p .)
    echo "${FN}"
    wget --no-verbose -O "${FN}" "${URL}"
}


function add_header_to_file(){
    FN="${1}"
    HEADER="${2}"
    { echo "${HEADER}"; cat "${FN}"; } | sponge "${FN}"
}


PW_RESOURCE="http://rest.kegg.jp/list/pathway"
PW_HEADER="pathway_id	pathway_name"

PW_CO_LINK_RESOURCE="http://rest.kegg.jp/link/cpd/pathway"
PW_CO_LINK_HEADER="pathway_id	compound_id"

CO_RESOURCE="http://rest.kegg.jp/list/compound"
CO_HEADER="compound_id	compound_name"


if [ $# -ne 1 ]
then
    echo "USAGE: ${0} output_file" >&2
    exit 1
fi 

OUTPUT_FILE="${1}"

TMP_PW=$(download_to_tmp_file "${PW_RESOURCE}")
TMP_PW_CO=$(download_to_tmp_file "${PW_CO_LINK_RESOURCE}")
TMP_CO=$(download_to_tmp_file "${CO_RESOURCE}")

add_header_to_file "${TMP_PW}" "${PW_HEADER}"
add_header_to_file "${TMP_PW_CO}" "${PW_CO_LINK_HEADER}"
add_header_to_file "${TMP_CO}" "${CO_HEADER}"

TMP_PW_PW_CO=$(mktemp -p .)
merge_keep_left "${TMP_PW}" "${TMP_PW_CO}" 1 1 > "${TMP_PW_PW_CO}"
merge_keep_left "${TMP_PW_PW_CO}" "${TMP_CO}" 3 1 > "${OUTPUT_FILE}"

rm "${TMP_PW}" "${TMP_PW_CO}" "${TMP_CO}" "${TMP_PW_PW_CO}"
