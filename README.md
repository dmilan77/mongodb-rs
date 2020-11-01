# Run ansible 
f
```
ansible-playbook -i inventory ansible/mongod-rs-set.yml

```

mongod --dbpath  /data/db --replSet rs0
# ReStart mongodb
login as centos
sudo systemctl stop mongod
sudo -H -u mongod bash -c 'mongod --port 27017 --dbpath /var/lib/mongo --replSet rs0' 

python app.py -p ip-172-16-0-165.ec2.internal:27017 -s ip-172-16-0-132.ec2.internal:27017 -r rs0




