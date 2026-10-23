import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

def validate_result(value,quantity):
    if not isinstance(value,dict) or set(value)!={'product','quantity','available'} or value['product']!='QC-42' or type(value['quantity']) is not int or value['quantity']!=quantity or not 1<=value['quantity']<=5 or value['available'] is not True:
        raise ValueError('Untrusted tool result contract failed')
    return value

async def call(name='stock',arguments=None,role='agent',command=None):
    # The host chooses this pinned local server and launch identity, never model arguments.
    params=StdioServerParameters(command=command or sys.executable,args=['-m','stock_mcp.server','--role',role])
    async with asyncio.timeout(10):
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write,read_timeout_seconds=5) as session:
                await session.initialize()
                tools=await session.list_tools()
                if name not in {t.name for t in tools.tools}:raise ValueError('Unknown tool')
                result=await session.call_tool(name,arguments or {})
                if result.is_error:raise ValueError('MCP tool rejected/failed; no success credited')
                # Treat results as untrusted; validate exact shape and expected business fields.
                text=next(c.text for c in result.content if c.type=='text')
                if len(text)>2000:raise ValueError('Tool result exceeds application bound')
                value=json.loads(text)
                return validate_result(value,(arguments or {}).get('quantity'))

def main():print(json.dumps(asyncio.run(call(arguments={'quantity':2})),indent=2))
if __name__=='__main__':main()
