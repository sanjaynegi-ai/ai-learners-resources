import asyncio,json
from dataclasses import dataclass,field
from typing import Annotated
from pydantic import StrictInt,Field
from agents import Agent,Runner,Model,ModelResponse,RunConfig,RunContextWrapper,function_tool
from agents.usage import Usage
from agents.tracing import TracingProcessor,set_trace_processors
from openai.types.responses import ResponseFunctionToolCall,ResponseOutputMessage,ResponseOutputText

@dataclass
class Principal:
    tenant:str='A'
    role:str='agent'
    entries:list=field(default_factory=list)

def lookup(principal,quantity):
    if principal.tenant!='A' or principal.role!='agent':raise PermissionError('Denied by trusted application context')
    if type(quantity) is not int or not 1<=quantity<=5:raise ValueError('Invalid quantity')
    principal.entries.append({'quantity':quantity})
    return {'product':'QC-42','quantity':quantity,'available':True}

@function_tool(failure_error_function=None)
async def stock(ctx:RunContextWrapper[Principal],quantity:Annotated[StrictInt,Field(ge=1,le=5)]) -> dict:
    """Read synthetic QuickCart stock, with trusted context authorization."""
    return lookup(ctx.context,quantity)

class ScriptedModel(Model):
    def __init__(self,arguments='{"quantity":2}',loop=False,hang=False):
        self.arguments=arguments;self.loop=loop;self.hang=hang;self.calls=0
    async def get_response(self,*args,**kwargs):
        if self.hang:await asyncio.sleep(60)
        self.calls+=1
        if self.calls==1 or self.loop:
            output=[ResponseFunctionToolCall(type='function_call',name='stock',arguments=self.arguments,call_id=f'call{self.calls}')]
        else:
            output=[ResponseOutputMessage(type='message',id='final',role='assistant',status='completed',
                content=[ResponseOutputText(type='output_text',text='Scripted loop completed; inspect trusted tool records.',annotations=[])])]
        return ModelResponse(output=output,usage=Usage(),response_id=None)
    async def stream_response(self,*args,**kwargs):
        raise NotImplementedError('Streaming is outside this offline checkpoint')
        yield

class LocalTrace(TracingProcessor):
    def __init__(self):self.events=[]
    def on_trace_start(self,trace):self.events.append('trace_start')
    def on_trace_end(self,trace):self.events.append('trace_end')
    def on_span_start(self,span):self.events.append('span_start')
    def on_span_end(self,span):self.events.append('span_end')
    def shutdown(self):pass
    def force_flush(self):pass

async def run(principal=None,model=None,max_turns=3,deadline=5):
    principal=principal or Principal();model=model or ScriptedModel()
    trace=LocalTrace()
    set_trace_processors([trace])  # Replace remote exporter BEFORE starting the trace.
    agent=Agent(name='Stock inspector',instructions='Read stock only; no purchases.',model=model,tools=[stock])
    async with asyncio.timeout(deadline):
        result=await Runner.run(agent,'Inspect synthetic QC-42 stock.',context=principal,max_turns=max_turns,
            run_config=RunConfig(tracing_disabled=False,trace_include_sensitive_data=False))
    return {'output':result.final_output,'trusted_tool_entries':principal.entries,'model_calls':model.calls,
            'local_trace_events':trace.events,'evidence_kind':'scripted-model-real-sdk-loop'}

def main():print(json.dumps(asyncio.run(run()),indent=2))
if __name__=='__main__':main()
