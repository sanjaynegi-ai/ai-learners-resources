import argparse
import json
from pathlib import Path
from .workflow import Application

def main():
    parser=argparse.ArgumentParser(description='Local synthetic approval workflow; no payment/provider')
    parser.add_argument('command',choices=['start','approve','resume','recover','inspect','revoke'])
    parser.add_argument('--request',default='R1')
    parser.add_argument('--directory',type=Path,default=Path('results/run'))
    parser.add_argument('--person',default='supervisor')
    args=parser.parse_args()
    app=Application(args.directory)
    try:
        app.seed()
        if args.command=='start': app.start(args.request)
        elif args.command=='approve': app.approve(args.request,args.person)
        elif args.command=='resume': app.resume(args.request)
        elif args.command=='recover': app.recover(args.request)
        elif args.command=='revoke':
            with app.db: app.db.execute('UPDATE members SET active=0 WHERE id=?',(args.person,))
        state=app.graph.get_state(app.config(args.request))
        print(json.dumps({'state':state.values,'next':list(state.next),'effects':app.effects()},indent=2))
    finally: app.close()

if __name__=='__main__': main()
