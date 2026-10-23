"""Native n8n JSON: one bounded local integration, not a second AI application."""
import json
from pathlib import Path

def workflow(event='E1',key='synthetic-lab-A',port=8765):
    return {'id':'review'+event,'name':'QuickCart local review admission','active':False,'nodes':[
      {'id':'manual','name':'Manual synthetic event','type':'n8n-nodes-base.manualTrigger','typeVersion':1,'position':[0,0],'parameters':{}},
      {'id':'event','name':'Synthetic envelope','type':'n8n-nodes-base.set','typeVersion':3.4,'position':[240,0],
       'parameters':{'assignments':{'assignments':[{'id':k,'name':k,'value':v,'type':'string'} for k,v in
        {'event_id':event,'ticket_id':'T1','text':'Synthetic refund inquiry'}.items()]},'options':{}}},
      {'id':'http','name':'Python review boundary','type':'n8n-nodes-base.httpRequest','typeVersion':4.2,'position':[480,0],
       'retryOnFail':True,'maxTries':2,'waitBetweenTries':500,
       'parameters':{'method':'POST','url':f'http://127.0.0.1:{port}/review','sendHeaders':True,
        'headerParameters':{'parameters':[{'name':'X-Lab-Key','value':key}]},'sendBody':True,'specifyBody':'json',
        'jsonBody':'={{ JSON.stringify($json) }}','options':{'timeout':1500}}}],
      'connections':{'Manual synthetic event':{'main':[[{'node':'Synthetic envelope','type':'main','index':0}]]},
                     'Synthetic envelope':{'main':[[{'node':'Python review boundary','type':'main','index':0}]]}},
      'settings':{'executionOrder':'v1','executionTimeout':15,'saveDataErrorExecution':'all','saveDataSuccessExecution':'none'}}

if __name__=='__main__':
    root=Path(__file__).resolve().parent/'workflows';root.mkdir(exist_ok=True)
    for name,event,key in [('happy','E1','synthetic-lab-A'),('retry','RETRY1','synthetic-lab-A'),('denied','DENIED1','wrong')]:
        (root/f'{name}.json').write_text(json.dumps(workflow(event,key),indent=2)+'\n',encoding='utf-8')
