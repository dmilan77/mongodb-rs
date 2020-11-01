#!/bin/bash
script="main.sh"
#Declare the number of mandatory args
margs=1

# Common functions - BEGIN
function example {
    echo -e "example: $script -g GRPNAME"
}

function usage {
    echo -e "usage: $script MANDATORY [OPTION]\n"
}

function help {
  usage
    echo -e "MANDATORY:"
    echo -e "  -g, --group  GRPNAME  The server group name"
    echo -e "  -h,  --help             Prints this help\n"
  example
}

# Ensures that the number of passed args are at least equals
# to the declared number of mandatory args.
# It also handles the special case of the -h or --help arg.
function margs_precheck {
	if [ $2 ] && [ $1 -lt $margs ]; then
		if [ $2 == "--help" ] || [ $2 == "-h" ]; then
			help
			exit
		else
	    	usage
			example
	    	exit 1 # error
		fi
	fi
}

# Ensures that all the mandatory args are not empty
function margs_check {
	if [ $# -lt $margs ]; then
	    usage
	  	example
	    exit 1 # error
	fi
}
# Common functions - END

# Custom functions - BEGIN
# Put here your custom functions
# Custom functions - END

# Main
margs_precheck $# $1

marg0=


# Args while-loop
while [ "$1" != "" ];
do
   case $1 in
   -g  | --group )  shift
                          marg0=$1
                		  ;;
   -h   | --help )        help
                          exit
                          ;;
   *)                     
                          echo "$script: illegal option $1"
                          usage
						  example
						  exit 1 # error
                          ;;
    esac
    shift
done

# Pass here your mandatory args for check
margs_check $marg0

# Your stuff goes here

export ANSIBLE_HOST_KEY_CHECKING=False
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

change_standalone_to_replicaset()
{
    ansible-playbook -i inventory ansible/mongod-rs-set.yml  --extra-vars "variable_host=${marg0}"  -v
    sleep 10s
}
replicate_and_failover()
{
    python app/rshelper.py -g ${marg0} -f True
}


change_standalone_to_replicaset
replicate_and_failover

