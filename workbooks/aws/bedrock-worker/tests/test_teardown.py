import datetime,unittest,boto3
from botocore.stub import Stubber
from bedrock_worker.teardown import remove

class TeardownTests(unittest.TestCase):
    def client(self,name):return boto3.client(name,region_name='us-east-1',aws_access_key_id='synthetic',aws_secret_access_key='synthetic')
    def test_sdk_delete_sequence_without_cloud(self):
        sts,cfn,lam=[self.client(n) for n in ('sts','cloudformation','lambda')]
        stack='skillup-bedrock-test';uuid='00000000-0000-0000-0000-000000000000';waits=[]
        with Stubber(sts) as s,Stubber(cfn) as c,Stubber(lam) as l:
            s.add_response('get_caller_identity',{'Account':'123456789012','UserId':'synthetic','Arn':'arn:aws:iam::123456789012:user/synthetic'})
            c.add_response('describe_stack_resources',{'StackResources':[{'LogicalResourceId':'Mapping','PhysicalResourceId':uuid,'ResourceType':'AWS::Lambda::EventSourceMapping','Timestamp':datetime.datetime.now(datetime.timezone.utc),'ResourceStatus':'CREATE_COMPLETE'}]}, {'StackName':stack})
            l.add_response('update_event_source_mapping',{'UUID':uuid,'State':'Disabling'},{'UUID':uuid,'Enabled':False})
            l.add_response('get_event_source_mapping',{'UUID':uuid,'State':'Disabled'},{'UUID':uuid})
            c.add_response('delete_stack',{}, {'StackName':stack})
            c.add_client_error('describe_stacks','ValidationError','Stack does not exist',expected_params={'StackName':stack})
            self.assertEqual(remove(sts,cfn,lam,stack,'123456789012',sleep=waits.append)['status'],'deleted')
            self.assertEqual(waits,[35]);s.assert_no_pending_responses();c.assert_no_pending_responses();l.assert_no_pending_responses()
    def test_wrong_name_never_calls_aws(self):
        with self.assertRaises(ValueError):remove(None,None,None,'production','123456789012')
    def test_wrong_account_stops_before_mutation(self):
        sts=self.client('sts')
        with Stubber(sts) as stub:
            stub.add_response('get_caller_identity',{'Account':'111111111111','UserId':'synthetic','Arn':'arn:aws:iam::111111111111:user/synthetic'})
            with self.assertRaises(PermissionError):remove(sts,None,None,'skillup-bedrock-test','123456789012')
