"""Local synthetic review admission; no model, email, purchase or real customer data."""
import argparse,hashlib,json,sqlite3,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

class ReviewStore:
    def __init__(self,path):
        self.db=sqlite3.connect(path,check_same_thread=False);self.lock=threading.Lock()
        self.db.executescript('CREATE TABLE IF NOT EXISTS reviews(tenant TEXT,event TEXT,payload_hash TEXT,ticket TEXT,route TEXT,PRIMARY KEY(tenant,event)); CREATE TABLE IF NOT EXISTS attempts(tenant TEXT,event TEXT,n INTEGER,PRIMARY KEY(tenant,event));')
    def accept(self,key,payload):
        if key!='synthetic-lab-A':return 403,{'status':'denied'}
        if not isinstance(payload,dict) or set(payload)!={'event_id','ticket_id','text'}:return 400,{'status':'invalid'}
        if any(not isinstance(payload[k],str) or not 1<=len(payload[k])<=limit for k,limit in [('event_id',64),('ticket_id',64),('text',2000)]):return 400,{'status':'invalid'}
        tenant='A';event=payload['event_id'];digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        with self.lock,self.db:
            existing=self.db.execute('SELECT payload_hash,route FROM reviews WHERE tenant=? AND event=?',(tenant,event)).fetchone()
            if existing and existing[0]!=digest:return 409,{'status':'idempotency_conflict'}
            route='human_review' if 'refund' in payload['text'].lower() else 'information_queue'
            self.db.execute('INSERT OR IGNORE INTO reviews VALUES(?,?,?,?,?)',(tenant,event,digest,payload['ticket_id'],route))
            self.db.execute('INSERT INTO attempts VALUES(?,?,1) ON CONFLICT(tenant,event) DO UPDATE SET n=n+1',(tenant,event))
            attempt=self.db.execute('SELECT n FROM attempts WHERE tenant=? AND event=?',(tenant,event)).fetchone()[0]
        # Deliberate ambiguous failure AFTER the record committed, once for this synthetic event.
        if event=='RETRY1' and attempt==1:return 503,{'status':'synthetic_response_failure_after_commit'}
        return 200,{'status':'accepted','event_id':event,'route':route,'duplicate':bool(existing)}
    def snapshot(self):
        with self.lock:
            return {'review_count':self.db.execute('SELECT count(*) FROM reviews').fetchone()[0],
                    'attempts':[list(r) for r in self.db.execute('SELECT * FROM attempts ORDER BY event')]}

def server(store,port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,value):
            body=json.dumps(value).encode();self.send_response(status)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path=='/health':self.send(200,{'status':'ok'})
            else:self.send(404,{'status':'not_found'})
        def do_POST(self):
            if self.path!='/review':self.send(404,{'status':'not_found'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096:raise ValueError('Body bound')
                payload=json.loads(self.rfile.read(length))
            except (ValueError,json.JSONDecodeError):self.send(400,{'status':'invalid'});return
            status,value=store.accept(self.headers.get('X-Lab-Key'),payload);self.send(status,value)
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)

def main():
    p=argparse.ArgumentParser();p.add_argument('--database',type=Path,default=Path('results/reviews.db'));p.add_argument('--port',type=int,default=8765);args=p.parse_args()
    args.database.parent.mkdir(parents=True,exist_ok=True);store=ReviewStore(args.database);http=server(store,args.port)
    try:http.serve_forever()
    finally:http.server_close();store.db.close()
if __name__=='__main__':main()
