import argparse
from typing import Annotated
from pydantic import StrictInt,Field
from mcp.server import MCPServer

def build(role):
    server=MCPServer('QuickCart local stock')
    @server.tool()
    def stock(quantity:Annotated[StrictInt,Field(ge=1,le=5)]) -> dict:
        """Read synthetic stock; no purchase or write operations."""
        if role!='agent':raise PermissionError('Denied by server-owned launch identity')
        return {'product':'QC-42','quantity':quantity,'available':True}
    @server.tool()
    def fault() -> str:
        """Deliberate failure for diagnosis, not a business operation."""
        raise RuntimeError('Synthetic tool failure')
    server.run(transport='stdio')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--role',choices=['agent','viewer'],default='viewer')
    args=parser.parse_args();build(args.role)
if __name__=='__main__':main()
