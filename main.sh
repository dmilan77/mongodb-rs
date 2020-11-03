#!/bin/bash
# set -x
script="main.sh"
#Declare the number of mandatory args
margs=5

# Common functions - BEGIN
function usage {
    echo -e "usage: $script -g GRPNAME -z HostedZoneID -d DnsRecord -oz OldHostedZoneId -od OldDnsRecord"
}
function example {
    echo -e "example: $script -g GRPNAME -z HostedZoneID -d DnsRecord -oz OldHostedZoneId -od OldDnsRecord"
}



function help {
  usage
    echo -e "MANDATORY:"
    echo -e "  -g, --group  GRPNAME  The server group name"
    echo -e "  -z, --hostedZoneId  HOSTEDZONEID  AWS Hosted Zone ID"
    echo -e "  -d, --dnsRecord  DNSRecord on  AWS Hosted Zone ID"
    echo -e "  -oz, --oldHostedZoneId  OldHOSTEDZONEID  AWS Hosted Zone ID"
    echo -e "  -od, --oldDnsRecord  OldDNSRecord on  AWS Hosted Zone ID"
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
function mdandatory_args_check {

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

group=
hostedZoneId=


# Args while-loop
while [ "$1" != "" ];
do
   case $1 in
   -g  | --group )  shift
                          group=$1
                		  ;;
   -z  | --hostedZoneId )  shift
                          hostedZoneId=$1
                		  ;;
   -d  | --dnsrecord )  shift
                          dnsrecord=$1
                		  ;;
   -oz  | --oldHostedZoneId )  shift
                          oldHostedZoneId=$1
                		  ;;
   -od  | --oldDnsrecord )  shift
                          oldDnsRecord=$1
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
mdandatory_args_check $group $hostedZoneId $dnsrecord $oldHostedZoneId $oldDnsRecord

# ACTUAL STUFF HERE

export ANSIBLE_HOST_KEY_CHECKING=False
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

change_standalone_to_replicaset()
{
    # ansible-playbook -i inventory ansible/mongod-rs-set.yml  -l ${group}  -v
    ansible-playbook -i inventory ansible/mongod-rs-set.yml  --extra-vars "variable_host=${group}"  -v
    sleep 10s
}
replicate_and_failover()
{
    python app/rshelper.py -g ${group} -z ${hostedZoneId} -d ${dnsrecord} -oz ${oldHostedZoneId} -od ${oldDnsRecord} -f True
}


change_standalone_to_replicaset
replicate_and_failover

