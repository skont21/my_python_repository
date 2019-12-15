TITLE=$'\e[1;36m'
HEADER=$'\e[1;35m'
OKBLUE=$'\e[36;1m'
OKGREEN=$'\e[32;1m'
WARNING=$'\e[1;33m'
FAIL=$'\e[1;31m'
ENDC=$'\e[0m'
BOLD=$'\e[1m'
UNDERLINE=$'\e[4m'
HIGHLIGHT=$'\e[41;1m';

if [[ $# -lt 2 ]]; then
    echo -e "Usage: ./run_check.sh ${HEADER}PYTHON SCRIPT${ENDC} [${TITLE}IP_ADDRESS${ENDC}]\n"
    echo -e "${HEADER}PYTHON SCRIPT${ENDC}: \n"
    echo -e "${OKBLUE}1)${ENDC}${TITLE}ppc_check_v1.py :${ENDC} for basic PPC parameters"
    echo -e "${OKBLUE}2)array_check_v1.py :${ENDC}  for basic PVARRAYs/SPPCs parameters"
    echo -e "${OKBLUE}3)custom made python script :${ENDC} ${BOLD}${WARNING}Please, PROCEED WITH CAUTION !!!${ENDC}"
    exit 1
fi

file=./err.txt
if [[ -f "$file" ]]; then
	rm err.txt
fi

if [[ $# -lt 3 ]]; then

	cat $1 2> err.txt | ssh root@$2 python - 2>> err.txt
else
	cat $1 2> err.txt | ssh root@$3 python - $2 2>> err.txt
fi


status_cat="${PIPESTATUS[0]}"  status_ssh="${PIPESTATUS[1]}" status_all="${PIPESTATUS[@]}"

if [[ $status_cat -ne "0" ]]; then
  echo -e "${FAIL} File ERROR (CODE:$status_cat) :${ENDC}"
  echo -e $(head -n 1 err.txt) "\n"
  exit 1
fi


if [[ $status_ssh -ne "0" ]]; then
  echo -e "${FAIL} SSH ERROR  (CODE:$status_ssh) :${ENDC}"
  echo -e $(tail -n 1 err.txt) "\n"
  exit 1
fi
