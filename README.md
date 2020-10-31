mongod --dbpath  /data/db --replSet rs0
# ReStart mongodb
login as centos
sudo systemctl stop mongod
sudo -H -u mongod bash -c 'mongod --port 27017 --dbpath /var/lib/mongo --replSet rs0' 





