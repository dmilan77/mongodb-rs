
import json
import argparse
import time
from datetime import datetime
from bson import json_util
from pymongo import MongoClient
from pymongo import errors

delayInMin = 1


def replSetInitiate(c, config):
  try:
    return c.admin.command({"replSetGetStatus": 1, "initialSync": 1})
  except errors.OperationFailure:
    print("Seems replSetInitiate has not started.  Trying replSetInitiate...")
    c.admin.command("replSetInitiate", config)
    return c.admin.command({"replSetGetStatus": 1, "initialSync": 1})


def waitUntilReplComplete(c, config):
  replInProgress=True
  counter=1
  status = "INPROGRESS"
  maxTry = 100
  # delayInMin=0.1
  while replInProgress:
    replStatus=c.admin.command({"replSetGetStatus": 1, "initialSync": 1})
    secondaryReplStatus = replStatus["members"][1]["state"]
    print(datetime.now(), "counter:", counter, "secondaryReplStatus:", secondaryReplStatus,
          "--> Replication inprogress..", "Sleeping .. ", delayInMin, "min")
    time.sleep(delayInMin*60)
    if secondaryReplStatus in [1,2] :
        replInProgress = False
        status="COMPLETE"
        print("Replication completed..")
    else:
      counter = counter+1
      if counter > maxTry :
        replInProgress = False
        status = "UNKNOWN"
  # time.sleep(delayInMin*60)
  return status


def failover(args,config):
  print(datetime.now(),"Failing over..")
  cs = MongoClient(args.secondary)
  print(datetime.now(), "Connected to secondary..")
  
  cp = MongoClient(args.primary)
  pIsMaster=cp.admin.command({"isMaster": 1})
  # print(json.dumps(pIsMaster, default=json_util.default, indent=2))
  print("pIsMaster:", pIsMaster["ismaster"])
  if pIsMaster["ismaster"]:
    print(datetime.now(), "Switching secondary to become primary..")
    print(datetime.now(), "connecting to primary:", args.primary)
    time.sleep(delayInMin*60)
    cp = MongoClient(args.primary)
    try:
      cp.admin.command({
          "replSetStepDown": 60,
          "secondaryCatchUpPeriodSecs": 10,
          "force": False
      })
    except:
      print(datetime.now(), "Ignore connection error..")
    time.sleep(delayInMin*60)
    print(datetime.now(), args.secondary,"is primary..")
  cs = MongoClient(args.secondary)
  print(datetime.now(), "connecting... to secondary..")
  time.sleep(delayInMin*60)
  sIsMaster = cs.admin.command({"isMaster": 1})
  print(datetime.now(), "sIsMaster:", sIsMaster["ismaster"])
  if sIsMaster["ismaster"]:
    print(datetime.now(), "Dropping old primary..")
    updateConfig = {'_id': args.replid, "version": 2, 'members': [
        {'_id': 1,  'host': args.secondary}]}
    status = cs.admin.command({
        "replSetReconfig": updateConfig,
        "force": False ,
        "maxTimeMS": 60000,
        "version": 2
    })
  
    status=cs.admin.command({"replSetGetStatus": 1})
    print(datetime.now(), json.dumps(status, default=json_util.default, indent=2))

  print(datetime.now(), "Failover completed: ")


def parser_argument(parser):
  parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                      help='app.py [-h] -p PRIMARYHOST:PORT -s SECONDARYHOST:PORT -r replicationid')

  parser.add_argument('-p', '--primary', required=True,
                      help="format  host:port")
  parser.add_argument('-s', '--secondary', required=True,
                      help="format  host:port")
  parser.add_argument('-r', '--replid', required=True,
                      help="replciation id")
  parser.add_argument('-f', '--failover', required=False,
                      nargs='?', const=False, default=False, type=bool)
  return parser.parse_args()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      add_help=False, usage="app.py [-h] -p PRIMARYHOST:PORT -s SECONDARYHOST:PORT -r replicationid")
  args= parser_argument(parser)

  print(datetime.now(), args.failover)
  cp = MongoClient(args.primary)
  config = {'_id': args.replid, 'members': [
      {'_id': 0, 'host': args.primary},
      {'_id': 1, 'host': args.secondary}]}
  replStatus = replSetInitiate(cp, config)
  status=waitUntilReplComplete(cp, config)
  print(datetime.now(), status)
  if args.failover:
    failover(args, config)

