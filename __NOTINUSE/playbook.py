# import ansible_runner
# # r = ansible_runner.run(private_data_dir='/opt/git-workspace/github/other/mongodb-rs/.tmp', playbook='test.yml')
# r = ansible_runner.run(private_data_dir='/opt/git-workspace/github/other/mongodb-rs/.tmp', 
# playbook='test.yml', 
# # inventory='/opt/git-workspace/github/other/mongodb-rs/inventory/hosts',
# host_pattern='mongoddb')
# print("{}: {}".format(r.status, r.rc))
# # successful: 0
# for each_host_event in r.events:
#     print(each_host_event['event'])
# print("Final status:")
# print(r.stats)

import ansible_runner
r = ansible_runner.run(private_data_dir='/tmp/demo', 
playbook='/opt/git-workspace/github/other/mongodb-rs/project/test.yml',
inventory='/opt/git-workspace/github/other/mongodb-rs/inventory/hosts',
host_pattern='mongoddb'
)
print("{}: {}".format(r.status, r.rc))
# successful: 0
for each_host_event in r.events:
    print(each_host_event['event'])
print("Final status:")
print(r.stats)