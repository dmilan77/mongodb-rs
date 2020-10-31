mongod --dbpath  /data/db --replSet rs0


config={
    _id: "rs0", members: [
        {_id:0, host: "172.16.0.125"},
        {_id:1, host: " 172.16.0.10"}
    ]
};

rs.initiate(config)
rs.status()


rs.remove("172.16.0.10:27017")