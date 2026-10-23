import json
import unittest
from pydantic import ValidationError
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from lc_mechanisms.demo import *


class MechanismTests(unittest.TestCase):
    def test_messages_match_direct_construction(self):
        actual = prompt().invoke({'evidence': QUOTE, 'question': 'code?'}).to_messages()
        self.assertEqual(actual, direct_messages(QUOTE, 'code?'))

    def test_missing_variable_rejected(self):
        with self.assertRaises(KeyError): prompt().invoke({'question': 'code?'})
        with self.assertRaises(ValueError): composed().invoke({'evidence':'', 'question':'code?'})
        with self.assertRaises(ValueError): direct(QUOTE,'x'*201)

    def test_composition_matches_explicit_steps_and_batch(self):
        inputs = {'evidence': QUOTE, 'question': 'code?'}
        self.assertEqual(composed().invoke(inputs), direct(**inputs))
        self.assertEqual(composed().batch([inputs, inputs]), [direct(**inputs)]*2)

    def test_schema_parser_and_semantic_validation_are_separate(self):
        parser = PydanticOutputParser(pydantic_object=Reply)
        result = parser.invoke('{"source":"QC-SHIP-01","quote":"invented"}')
        with self.assertRaises(ValueError): supported(result)
        with self.assertRaises(OutputParserException): parser.invoke('{"source":null}')

    def test_history_sessions_isolated(self):
        wrapped, histories = history_pair()
        for session, question in [('A','monitor'), ('B','keyboard'), ('A','which one')]:
            response = wrapped.invoke({'question':question}, config={'configurable':{'session_id':session}})
        self.assertEqual(json.loads(response.content), ['monitor','which one'])
        self.assertEqual(histories['B'].messages[0].content, 'keyboard')

    def test_history_bound_and_clear(self):
        wrapped, histories = history_pair()
        for i in range(5): wrapped.invoke({'question':str(i)},config={'configurable':{'session_id':'A'}})
        self.assertEqual(len(histories['A'].messages),4)
        self.assertEqual(histories['A'].messages[0].content,'3')
        histories['A'].clear()
        self.assertEqual(histories['A'].messages,[])

    def test_retriever_preserves_metadata_and_no_match(self):
        self.assertEqual(retriever().invoke('DELAY-42')[0].metadata, {'source':SOURCE,'revision':1})
        self.assertEqual(retriever().invoke('unrelated'), [])

    def test_tool_schema_and_role_are_separate(self):
        self.assertEqual(authorized_lookup('agent',{'quantity':2}), lookup(2))
        with self.assertRaises(PermissionError): authorized_lookup('viewer',{'quantity':2})
        for args in ({'quantity':True},{'quantity':6},{'quantity':1,'role':'agent'}):
            with self.assertRaises(ValidationError): authorized_lookup('agent',args)

    def test_bad_stage_rejected(self):
        broken = prompt() | RunnableLambda(lambda _: {'wrong':'shape'}) | PydanticOutputParser(pydantic_object=Reply)
        with self.assertRaises((ValidationError, TypeError)): broken.invoke({'evidence':QUOTE,'question':'code?'})
