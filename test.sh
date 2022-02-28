#Install schellscript
#based on tracker schell script from class

#!/bin/bash 

# 1. Install packages

REQ_PYTHON_V="370"

ACTUAL_PYTHON_V=$(python -c 'import sys; version=sys.version_info[:3]; print("{0}{1}{2}".format(*version))')
ACTUAL_PYTHON3_V=$(python3 -c 'import sys; version=sys.version_info[:3]; print("{0}{1}{2}".format(*version))')

if [[ $ACTUAL_PYTHON_V > $REQ_PYTHON_V ]] || [[ $ACTUAL_PYTHON_V == $REQ_PYTHON_V ]];  then 
    PYTHON="python"
elif [[ $ACTUAL_PYTHON3_V > $REQ_PYTHON_V ]] || [[ $ACTUAL_PYTHON3_V == $REQ_PYTHON_V ]]; then 
    PYTHON="python3"
else
    echo -e "\tPython 3.7.0 is not installed on this machine. Please install Python 3.7 before continuing."
    exit 1
fi

echo "Installing packages..."
chmod 775 install.sh
./install.sh
# 2. Run distances

echo "Options..."
while getopts d: opt; do 
    case $opt in 
        d) data=${OPTARG};;
    esac
done

if  ["$data" == dist ]; then
    printf "${Cyan}Calculating distances...\n${Color_Off}"
    $PYTHON distances.py 
fi

# 3. Run webpage
$PYTHON manage.py