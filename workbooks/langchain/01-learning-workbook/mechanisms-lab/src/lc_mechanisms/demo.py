import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ConfigDict, StrictInt, Field

SOURCE = 'QC-SHIP-01'
QUOTE = 'Carrier DELAY-42 indicates a carrier scan delay.'


class Reply(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: str
    quote: str


def supported(reply):
    if reply.source != SOURCE or reply.quote != QUOTE:
        raise ValueError('Schema-valid output is not supported by the source')
    return reply


def prompt():
    return ChatPromptTemplate.from_messages([
        ('system', 'Inspect synthetic evidence only: {evidence}'), ('human', '{question}')])


def direct_messages(evidence, question):
    return [SystemMessage(content=f'Inspect synthetic evidence only: {evidence}'), HumanMessage(content=question)]


def mock_call(prompt_value):
    # No inference. This fixed response proves control flow only.
    messages = prompt_value.to_messages() if hasattr(prompt_value, 'to_messages') else prompt_value
    assert messages[-1].type == 'human'
    return AIMessage(content=json.dumps({'source': SOURCE, 'quote': QUOTE}))


def validate_inputs(inputs):
    if inputs['evidence'] != QUOTE:
        raise ValueError('This fixed-response demonstration requires its exact supplied evidence')
    if not isinstance(inputs['question'], str) or not 0 < len(inputs['question'].strip()) <= 200:
        raise ValueError('Question must contain 1-200 characters')
    return inputs


def composed():
    return RunnableLambda(validate_inputs) | prompt() | RunnableLambda(mock_call) | PydanticOutputParser(pydantic_object=Reply) | RunnableLambda(supported)


def direct(evidence, question):
    # Same boundaries, deliberately explicit rather than composed.
    validate_inputs({'evidence': evidence, 'question': question})
    response = mock_call(direct_messages(evidence, question))
    return supported(Reply.model_validate_json(response.content))


class BoundedHistory(InMemoryChatMessageHistory):
    def add_messages(self, messages):
        super().add_messages(messages)
        self.messages[:] = self.messages[-4:]  # Last two human/AI pairs; not a token budget.


def history_pair():
    histories = {}
    def get_history(session_id):
        return histories.setdefault(session_id, BoundedHistory())
    template = ChatPromptTemplate.from_messages([
        ('system', 'Synthetic history inspection; no inference.'),
        MessagesPlaceholder('history'), ('human', '{question}')])
    def inspect(value):
        prior = [m.content for m in value.to_messages() if m.type == 'human']
        return AIMessage(content=json.dumps(prior))
    wrapped = RunnableWithMessageHistory(template | RunnableLambda(inspect), get_history,
                                        input_messages_key='question', history_messages_key='history')
    return wrapped, histories


class KeywordRetriever(BaseRetriever):
    documents: list[Document]
    def _get_relevant_documents(self, query, *, run_manager):
        if not isinstance(query, str) or len(query) > 200:
            raise ValueError('Bounded string query required')
        terms = set(query.lower().split())
        return [d for d in self.documents if terms & set(d.page_content.lower().split())][:3]


def retriever():
    return KeywordRetriever(documents=[Document(page_content=QUOTE, metadata={'source': SOURCE, 'revision': 1})])


class LookupArgs(BaseModel):
    model_config = ConfigDict(extra='forbid')
    quantity: StrictInt = Field(ge=1, le=5)


def lookup(quantity):
    return {'product': 'QC-42', 'quantity': quantity, 'available': True}


def lookup_tool():
    return StructuredTool.from_function(lookup, name='lookup_stock',
        description='Read synthetic QC-42 stock only.', args_schema=LookupArgs)


def authorized_lookup(role, arguments):
    # Role comes from application authority, never the model's arguments.
    if role != 'agent':
        raise PermissionError('Role denied before tool invocation')
    return lookup_tool().invoke(arguments)


def main():
    inputs = {'evidence': QUOTE, 'question': 'What is DELAY-42?'}
    chain_result = composed().invoke(inputs)
    wrapped, histories = history_pair()
    wrapped.invoke({'question': 'monitor'}, config={'configurable': {'session_id': 'A'}})
    history = wrapped.invoke({'question': 'keyboard'}, config={'configurable': {'session_id': 'B'}})
    print(json.dumps({'evidence_kind': 'offline-fixed-response', 'direct_equals_composed':
                     direct(**inputs) == chain_result, 'reply': chain_result.model_dump(),
                     'session_B_human_inputs': json.loads(history.content),
                     'retrieved_sources': [d.metadata['source'] for d in retriever().invoke('DELAY-42')],
                     'tool': authorized_lookup('agent', {'quantity': 2})}, indent=2))


if __name__ == '__main__': main()
