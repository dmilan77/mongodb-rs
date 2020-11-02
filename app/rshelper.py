from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.cli.playbook import PlaybookCLI
from ansible.vars.manager import VariableManager
from ansible.executor.playbook_executor import PlaybookExecutor
import boto3



import json
import argparse
import time
from datetime import datetime
from bson import json_util
from pymongo import MongoClient
from pymongo import errors

delayInMin = 1
inventory_file_name = 'inventory/hosts'
data_loader = DataLoader()
inventory = InventoryManager(loader = data_loader,
                            sources=[inventory_file_name])
phost=''
shost=''

def replSetInitiate(c, config):
  try:
    return c.admin.command({"replSetGetStatus": 1, "initialSync": 1})
  except errors.OperationFailure:
    print("Seems replSetInitiate has not started.  Trying replSetInitiate...")
    c.admin.command("replSetInitiate", config)
    return c.admin.command({"replSetGetStatus": 1, "initialSync": 1})

# def getPHost():
#     inventory.get_groups_dict()[args.group][0]


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

def updateDNSEntry():
  route53Client = boto3.client('route53')
  ec2Client = boto3.client('ec2',region_name='us-west-1')
  # ec2Resource = boto3.resource('ec2',region_name='us-west-1')
  # instance = ec2Resource.Instance("i-0dcef093db77ba50a")
  # print(instance.private_ip_address)

  # response = ec2Client.describe_instances()


  phostEc2 = ec2Client.describe_instances(
    Filters=[
        {
            'Name': 'private-dns-name',
            'Values': [
                phost,
            ]
        },
    ]
  )
  phostEc2Ip4=phostEc2['Reservations'][0]['Instances'][0]['PrivateIpAddress']
  print("phostEc2Ip4:",phostEc2Ip4)
  shostEc2 = ec2Client.describe_instances(
    Filters=[
        {
            'Name': 'private-dns-name',
            'Values': [
                shost,
            ]
        },
    ]
  )
  shostEc2Ip4=shostEc2['Reservations'][0]['Instances'][0]['PrivateIpAddress']
  print("shostEc2Ip4:",shostEc2Ip4)



  params = {
        'HostedZoneId': 'Z01324193MJDSXPQB29M',
        'ChangeBatch': {
            'Changes': [{
                'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'mongodb.innovaccer.net',
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': shostEc2Ip4}]
                    }
                },]
        }
    }
  # response = route53Client.change_resource_record_sets(**params)
  # print(response)



def failover(args,config):
  print(datetime.now(),"Failing over..")
  cs = MongoClient(shost)
  print(datetime.now(), "Connected to secondary..")
  
  cp = MongoClient(phost)
  pIsMaster=cp.admin.command({"isMaster": 1})
  # print(json.dumps(pIsMaster, default=json_util.default, indent=2))
  print("pIsMaster:", pIsMaster["ismaster"])
  if pIsMaster["ismaster"]:
    print(datetime.now(), "Switching secondary to become primary..")
    print(datetime.now(), "connecting to primary:", phost)
    time.sleep(delayInMin*60)
    cp = MongoClient(phost)
    try:
      cp.admin.command({
          "replSetStepDown": 60,
          "secondaryCatchUpPeriodSecs": 10,
          "force": False
      })
    except:
      print(datetime.now(), "Ignore connection error..")
    updateDNSEntry()
    time.sleep(delayInMin*60)
    print(datetime.now(), shost,"is primary..")
  cs = MongoClient(shost)
  print(datetime.now(), "connecting... to secondary..")
  time.sleep(delayInMin*60)
  sIsMaster = cs.admin.command({"isMaster": 1})
  print(datetime.now(), "sIsMaster:", sIsMaster["ismaster"])
  if sIsMaster["ismaster"]:
    print(datetime.now(), "Dropping old primary..")
    updateConfig = {'_id': "rs0", "version": 2, 'members': [
        {'_id': 1,  'host': shost}]}
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
                      help='mongorshelper.py  [-h] -g GROUPNAME')

  parser.add_argument('-g', '--group', required=True,
                      help="format  groupname")


  parser.add_argument('-f', '--failover', required=False,
                      nargs='?', const=False, default=False, type=bool)
  return parser.parse_args()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      add_help=False, usage="mongorshelper.py  [-h] -g GROUPNAME'")
  args= parser_argument(parser)
  phost=inventory.get_groups_dict()[args.group][0]
  shost=inventory.get_groups_dict()[args.group][1]
  print(datetime.now(), "Primary host: phost:",phost)
  print(datetime.now(), "Secondary host: shost:",shost)
  # cp = MongoClient(phost)

  # config = {'_id': "rs0", 'members': [
  #     {'_id': 0, 'host': phost},
  #     {'_id': 1, 'host': shost}]}
  # replStatus = replSetInitiate(cp, config)
  # status=waitUntilReplComplete(cp, config)
  # print(datetime.now(), status)
  # if args.failover:
  #   failover(args, config)

  updateDNSEntry()




