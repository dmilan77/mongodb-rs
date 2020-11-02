## mongodb plugin install
```
ansible-galaxy collection install community.mongodb
```
# Run ansible 
f
```
ansible-playbook -i inventory ansible/mongod-rs-set.yml

```


ip-172-31-4-60.us-west-1.compute.internal 172.31.4.60  13.52.235.194

mongod --dbpath  /data/db --replSet rs0
# ReStart mongodb
login as centos
sudo systemctl stop mongod
sudo -H -u mongod bash -c 'mongod --port 27017 --dbpath /var/lib/mongo --replSet rs0' 

python app.py -p ip-172-16-0-165.ec2.internal:27017 -s ip-172-16-0-132.ec2.internal:27017 -r rs0




