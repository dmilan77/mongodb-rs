#!/bin/bash
# set -x
script="main.sh"
#Declare the number of mandatory args
margs=2

# Common functions - BEGIN
function usage {
    echo -e "usage: $script -g GRPNAME -z HostedZoneID"
}
function example {
    echo -e "example: $script -g GRPNAME -z HostedZoneID"
}



function help {
  usage
    echo -e "MANDATORY:"
    echo -e "  -g, --group  GRPNAME  The server group name"
    echo -e "  -z, --hostedZoneId  HOSTEDZONEID  AWS Hosted Zone ID"
    echo -e "HELP:"
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
  echo -e "****** $#"

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
marg1=


# Args while-loop
while [ "$1" != "" ];
do
   case $1 in
   -g  | --group )  shift
                          marg0=$1
                		  ;;
   -z  | --hostedZoneId )  shift
                          marg1=$1
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
margs_check $marg0 $marg1

# ACTUAL STUFF HERE

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
    python app/rshelper.py -g ${marg0} -z ${marg1} -f True
}


change_standalone_to_replicaset
replicate_and_failover

