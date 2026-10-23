import json,threading,unittest
from unittest.mock import patch
import boto3
from botocore.stub import Stubber
from bedrock_worker.app import parse,generate,process,handler,DynamoStore

class Store:
    def __init__(self,maximum=10):self.rows={};self.calls=0;self.maximum=maximum;self.lock=threading.Lock()
    def reserve(self,key,digest):
        with self.lock:
            if key in self.rows:return self.rows[key]
            if self.calls>=self.maximum:raise RuntimeError('Budget exhausted')
            self.calls+=1;self.rows[key]={'hash':digest,'status':'REVIEW_REQUIRED'}
    def complete(self,key,draft):self.rows[key].update(status='DRAFT_FOR_REVIEW',draft=draft)

class Provider:
    def __init__(self,fail=False):self.calls=0;self.fail=fail
    def converse(self,**kwargs):
        self.calls+=1
        if self.fail:raise TimeoutError('Synthetic timeout')
        return {'stopReason':'end_turn','output':{'message':{'content':[{'text':'Synthetic internal draft'}]}}}

BODY=json.dumps({'job_id':'J1','text':'Synthetic refund question'})
class WorkerTests(unittest.TestCase):
    def test_dynamo_reservation_sdk_shape(self):
        client=boto3.client('dynamodb',region_name='us-east-1',aws_access_key_id='synthetic',aws_secret_access_key='synthetic')
        with Stubber(client) as stub:
            stub.add_response('get_item',{})
            stub.add_response('transact_write_items',{})
            self.assertIsNone(DynamoStore(client,'synthetic-table').reserve('J1','synthetic-hash'))
            stub.assert_no_pending_responses()
    def test_duplicate_no_second_model_call(self):
        store=Store();model=Provider();process(BODY,store,model,'fixture');process(BODY,store,model,'fixture')
        self.assertEqual(model.calls,1);self.assertEqual(store.rows['J1']['status'],'DRAFT_FOR_REVIEW')
    def test_ambiguous_failure_never_retries_paid_attempt(self):
        store=Store();model=Provider(True)
        for _ in range(2):
            with self.assertRaises((TimeoutError,RuntimeError)):process(BODY,store,model,'fixture')
        self.assertEqual(model.calls,1);self.assertEqual(store.rows['J1']['status'],'REVIEW_REQUIRED')
    def test_budget_and_conflict(self):
        store=Store(1);model=Provider();process(BODY,store,model,'fixture')
        for body in (json.dumps({'job_id':'J2','text':'new'}),json.dumps({'job_id':'J1','text':'changed'})):
            with self.assertRaises((ValueError,RuntimeError)):process(body,store,model,'fixture')
        self.assertEqual(model.calls,1)
    def test_invalid_payload(self):
        for value in ({'job_id':'J1','text':'x','tenant':'B'},{'job_id':True,'text':'x'},{'job_id':'J1','text':'x'*1001}):
            with self.assertRaises(ValueError):parse(json.dumps(value))
    def test_partial_batch_and_source(self):
        event={'Records':[{'messageId':'m1','eventSourceARN':'queue','body':BODY},
                          {'messageId':'m2','eventSourceARN':'foreign','body':BODY}]}
        context=type('Context',(),{'get_remaining_time_in_millis':lambda self:20000})()
        with patch('bedrock_worker.app.clients',return_value=(Store(),Provider())),patch.dict('os.environ',{'QUEUE_ARN':'queue','MODEL_ID':'fixture'}):
            self.assertEqual(handler(event,context),{'batchItemFailures':[{'itemIdentifier':'m2'}]})
    def test_real_converse_schema_with_stubber(self):
        client=boto3.client('bedrock-runtime',region_name='us-east-1',aws_access_key_id='synthetic',aws_secret_access_key='synthetic')
        response={'output':{'message':{'role':'assistant','content':[{'text':'Synthetic draft'}]}},'stopReason':'end_turn',
                  'usage':{'inputTokens':5,'outputTokens':3,'totalTokens':8},'metrics':{'latencyMs':1}}
        with Stubber(client) as stub:
            stub.add_response('converse',response)
            self.assertEqual(generate(client,'synthetic.model-v1','synthetic'), 'Synthetic draft')
