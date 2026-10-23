import json
import sqlite3
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command


class State(TypedDict, total=False):
    request_id: str
    status: str


class Application:
    def __init__(self, directory):
        from pathlib import Path
        root = Path(directory); root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(root / 'authority.db')
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS members(id TEXT PRIMARY KEY,tenant TEXT,role TEXT,active INTEGER);
        CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,tenant TEXT,requester TEXT,amount INTEGER,status TEXT);
        CREATE TABLE IF NOT EXISTS approvals(request TEXT PRIMARY KEY,approver TEXT,approved INTEGER);
        CREATE TABLE IF NOT EXISTS effects(request TEXT PRIMARY KEY,amount INTEGER);
        ''')
        self.checkpoint_connection = sqlite3.connect(root / 'checkpoints.db', check_same_thread=False)
        self.saver = SqliteSaver(self.checkpoint_connection)
        builder = StateGraph(State)
        builder.add_node('validate', self.validate)
        builder.add_node('approval', self.approval)
        builder.add_node('execute', self.execute)
        builder.add_edge(START, 'validate')
        builder.add_conditional_edges('validate', lambda s: 'end' if s['status']=='denied' else 'approval',
                                      {'end': END, 'approval': 'approval'})
        builder.add_edge('approval','execute'); builder.add_edge('execute', END)
        self.graph = builder.compile(checkpointer=self.saver)
        self.crash_after_effect = False

    def seed(self):
        # Fixture initialization only; INSERT OR IGNORE never restores a revocation on restart.
        with self.db:
            self.db.executemany('INSERT OR IGNORE INTO members VALUES(?,?,?,1)',
                [('agent','A','agent'), ('supervisor','A','supervisor'), ('foreign','B','supervisor')])

    def submit(self, request_id, amount=100):
        if not isinstance(request_id,str) or not request_id.isalnum() or len(request_id)>40:
            raise ValueError('Bounded alphanumeric request ID required')
        if type(amount) is not int or not 1 <= amount <= 1000:
            raise ValueError('Synthetic credit must be an integer in 1..1000')
        with self.db:
            existing = self.db.execute('SELECT amount FROM requests WHERE id=?',(request_id,)).fetchone()
            if existing and existing['amount'] != amount: raise ValueError('Immutable request conflict')
            self.db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?,?,?)', (request_id,'A','agent',amount,'pending'))

    def request(self, state):
        if set(state)-{'request_id','status'} or not isinstance(state.get('request_id'),str):
            raise ValueError('Invalid workflow state')
        row = self.db.execute('SELECT * FROM requests WHERE id=?',(state['request_id'],)).fetchone()
        if row is None: raise ValueError('Unknown request')
        return row

    def validate(self, state):
        row = self.request(state)
        principal = self.db.execute('SELECT * FROM members WHERE id=?',(row['requester'],)).fetchone()
        allowed = principal and principal['active'] and principal['role']=='agent' and principal['tenant']==row['tenant']
        return {'status':'waiting' if allowed else 'denied'}

    def approve(self, request_id, approver, approved=True):
        if type(approved) is not bool: raise ValueError('Boolean decision required')
        with self.db:
            row = self.db.execute('SELECT * FROM requests WHERE id=?',(request_id,)).fetchone()
            person = self.db.execute('SELECT * FROM members WHERE id=?',(approver,)).fetchone()
            if not row or not person or not person['active'] or person['tenant']!=row['tenant'] or person['role']!='supervisor' or approver==row['requester']:
                raise PermissionError('Approval identity denied')
            self.db.execute('INSERT OR REPLACE INTO approvals VALUES(?,?,?)',(request_id,approver,int(approved)))

    def approval(self, state):
        row = self.request(state)
        interrupt({'request_id':row['id'], 'amount':row['amount'], 'reason':'Await trusted registry decision'})
        # Resume payload is only a wake-up, never approval authority. Code before interrupt reruns.
        return {'status':'reviewed'}

    def execute(self, state):
        row = self.request(state)
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            prior = self.db.execute('SELECT amount FROM effects WHERE request=?',(row['id'],)).fetchone()
            if prior:
                if prior['amount'] != row['amount']: raise ValueError('Effect/request mismatch requires reconciliation')
                return {'status':'completed'}  # Report an already committed fact, never apply again.
            approval = self.db.execute('SELECT a.approved,m.* FROM approvals a JOIN members m ON a.approver=m.id WHERE a.request=?',(row['id'],)).fetchone()
            requester = self.db.execute('SELECT * FROM members WHERE id=?',(row['requester'],)).fetchone()
            allowed = (approval and approval['approved'] and approval['active'] and approval['role']=='supervisor'
                       and approval['tenant']==row['tenant'] and approval['id']!=row['requester']
                       and requester and requester['active'] and requester['tenant']==row['tenant'] and requester['role']=='agent')
            if not allowed:
                self.db.execute("UPDATE requests SET status='denied' WHERE id=?",(row['id'],))
                return {'status':'denied'}
            # Simulated effect and durable action share one local transaction, keyed by immutable request ID.
            self.db.execute('INSERT OR IGNORE INTO effects VALUES(?,?)',(row['id'],row['amount']))
            self.db.execute("UPDATE requests SET status='completed' WHERE id=?",(row['id'],))
        if self.crash_after_effect:
            self.crash_after_effect = False
            raise RuntimeError('Simulated process loss after effect commit, before graph checkpoint')
        return {'status':'completed'}

    def config(self, request_id, limit=8):
        return {'configurable':{'thread_id':request_id},'recursion_limit':limit}

    def start(self, request_id, limit=8):
        if self.db.execute('SELECT 1 FROM requests WHERE id=?',(request_id,)).fetchone() is None:
            self.submit(request_id)
        snapshot = self.graph.get_state(self.config(request_id))
        if snapshot.values: return snapshot.values
        return self.graph.invoke({'request_id':request_id},self.config(request_id,limit))

    def resume(self, request_id, payload=None):
        snapshot = self.graph.get_state(self.config(request_id))
        if not snapshot.values: raise ValueError('No saved workflow')
        if not snapshot.next: return snapshot.values
        return self.graph.invoke(Command(resume=payload if payload is not None else 'wake'), self.config(request_id))

    def recover(self, request_id):
        return self.graph.invoke(None,self.config(request_id))

    def sequential(self, request_id):
        state={'request_id':request_id}
        if self.validate(state)['status']=='denied': return {'status':'denied'}
        return self.execute(state)  # Requires an already recorded decision; no waiting/checkpoint orchestration.

    def effects(self):
        return [dict(row) for row in self.db.execute('SELECT * FROM effects ORDER BY request')]

    def close(self):
        self.checkpoint_connection.close(); self.db.close()
