"""Explicitly requested live cleanup only; SDK call sequence is tested with Stubber."""
import argparse,re,time

def remove(sts,cfn,lam,stack,account,sleep=time.sleep):
    if not re.fullmatch(r'skillup-bedrock-[a-z0-9-]{1,24}',stack):raise ValueError('Dedicated lab stack name required')
    if not re.fullmatch(r'\d{12}',account) or sts.get_caller_identity()['Account']!=account:raise PermissionError('Unexpected account')
    resources=cfn.describe_stack_resources(StackName=stack)['StackResources']
    mapping=next(r['PhysicalResourceId'] for r in resources if r['LogicalResourceId']=='Mapping')
    lam.update_event_source_mapping(UUID=mapping,Enabled=False)
    for _ in range(12):
        state=lam.get_event_source_mapping(UUID=mapping)['State']
        if state=='Disabled':break
        sleep(5)
    else:raise TimeoutError('Mapping did not disable; do not delete while status is unknown')
    sleep(35)  # Allow the configured 30s invocation timeout plus margin before data destruction.
    cfn.delete_stack(StackName=stack)
    cfn.get_waiter('stack_delete_complete').wait(StackName=stack,WaiterConfig={'Delay':5,'MaxAttempts':24})
    return {'stack':stack,'status':'deleted','artifact_bucket':'not_deleted; clean the dedicated prefix separately'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--stack',required=True);p.add_argument('--account',required=True)
    p.add_argument('--profile',required=True);p.add_argument('--region',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    if not a.execute:p.exit(2,'No action taken. Review deletion/export requirements, then explicitly add --execute.\n')
    import boto3,json
    session=boto3.Session(profile_name=a.profile,region_name=a.region)
    print(json.dumps(remove(session.client('sts'),session.client('cloudformation'),session.client('lambda'),a.stack,a.account)))
if __name__=='__main__':main()
