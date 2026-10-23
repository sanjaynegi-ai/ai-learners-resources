def quorum(requester, tenant, approvers):
    eligible={a['id'] for a in approvers if a['active'] is True and a['role']=='supervisor'
              and a['tenant']==tenant and a['id']!=requester}
    return len(eligible)>=2
