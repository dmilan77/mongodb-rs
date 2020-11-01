#!/usr/bin/env bash
export ANSIBLE_HOST_KEY_CHECKING=False
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

change_standalone_to_replicaset()
{
    ansible-playbook -i inventory ansible/mongod-rs-set.yml  --extra-vars "variable_host=mongod1"  -v
    sleep 60s
}


change_standalone_to_replicaset

