replStatus = db.adminCommand({ replSetGetStatus: 1 })
printjson(replStatus)
// printjson(replStatus.members[0].state)
if (replStatus.ok==0){
    db.runCommand(replSetInitiate, {
        _id: "foo",
        members : [
         {_id : 0, host : "localhsot:27017"},
         { _id: 1, host: "localhsot:27018"}
        ]
    })
}
replStatus = db.adminCommand({ replSetGetStatus: 1 })
printjson(replStatus)

                  
