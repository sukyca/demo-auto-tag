import os
import requests
import sys

TOKEN= str(sys.argv[0])
OWNER= str(sys.argv[1])
REPO= str(sys.argv[2])
Workflow_Name= str(sys.argv[3])
pl_Baseline_Number= str(sys.argv[4])
pl_Baseline_Revision = str(sys.argv[5])


print( "the token value is")
def trigger_workflow(Workflow_Name,pl_Baseline_Number,pl_Baseline_Revision):

      headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "access_token {TOKEN}"
      }

      data = {
        "event_type": Workflow_Name,
        "client_payload": {
          'baselinetag': pl_Baseline_Number,
          'revision_number': pl_Baseline_Revision
        }
      }

      responsevalue=requests.post("https://api.github.com/repos/{OWNER}/{REPO}/dispatches",data=data,headers=headers)
      print("The respoinse message is ",responsevalue.content)

trigger_workflow(Workflow_Name,pl_Baseline_Number,pl_Baseline_Revision)