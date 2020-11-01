#!/usr/bin/env bash
export ANSIBLE_HOST_KEY_CHECKING=False
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

change_standalone_to_replicaset()
{
    ansible-playbook -i inventory ansible/mongod-rs-set.yml  --extra-vars "variable_host=mongod1"  -v
    sleep 10s
}
replicate_and_failover()
{
    python app/rshelper.py -g mongod1 -f True
}


change_standalone_to_replicaset
replicate_and_failover

