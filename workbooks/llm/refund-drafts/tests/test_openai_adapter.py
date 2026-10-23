"""Offline contract tests for the OpenAI adapter: real SDK types and exceptions, a stub client, no network."""
import unittest

import httpx2
import openai
from openai.types.responses import Response, ResponseOutputMessage, ResponseOutputRefusal, ResponseOutputText, ResponseUsage
from openai.types.responses.response import IncompleteDetails

from refund_drafts.domain import load_records
from refund_drafts.prompt import build_request
from refund_drafts.providers import (OpenAIProvider, PermanentProviderError, TransientProviderError,
                                     make_openai_client)
from refund_drafts.schema import JSON_SCHEMA

REQUEST = httpx2.Request("POST", "https://api.openai.com/v1/responses")


def status_error(cls, code):
    return cls("synthetic", response=httpx2.Response(code, request=REQUEST), body=None)


def response(*, status="completed", parts=(), incomplete=None):
    message = ResponseOutputMessage.model_construct(type="message", role="assistant", id="msg_1", status="completed",
                                                    content=list(parts))
    return Response.model_construct(status=status, output=[message], model="synthetic-model",
                                    incomplete_details=IncompleteDetails.model_construct(reason=incomplete) if incomplete else None,
                                    usage=ResponseUsage.model_construct(input_tokens=321, output_tokens=45))


class StubResponses:
    def __init__(self, outcome):
        self.outcome, self.kwargs = outcome, None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class StubClient:
    def __init__(self, outcome):
        self.responses = StubResponses(outcome)


class OpenAIAdapterTests(unittest.TestCase):
    def setUp(self):
        records = load_records()
        ticket = records.tickets["T-001"]
        self.request = build_request(records.orders[ticket.order_id], records.policies["card"], ticket)

    def call(self, outcome):
        client = StubClient(outcome)
        result = OpenAIProvider(client, "synthetic-model").generate(self.request, timeout_s=7.5, max_output_tokens=400)
        return result, client.responses.kwargs

    def test_request_shape_uses_strict_schema_limits_and_no_storage(self):
        text = '{"reply_text": "Hi", "refund_date_used": null, "needs_agent": true}'
        result, kwargs = self.call(response(parts=[ResponseOutputText.model_construct(type="output_text", text=text, annotations=[])]))
        self.assertEqual(kwargs["text"]["format"], {"type": "json_schema", "name": "refund_reply_draft", "strict": True,
                                                    "schema": JSON_SCHEMA})
        self.assertEqual((kwargs["model"], kwargs["max_output_tokens"], kwargs["store"], kwargs["timeout"]),
                         ("synthetic-model", 400, False, 7.5))
        self.assertEqual(kwargs["instructions"], self.request.instructions)
        self.assertEqual((result.status, result.text, result.input_tokens, result.output_tokens), ("completed", text, 321, 45))

    def test_incomplete_and_refusal_are_reported_before_any_parsing(self):
        result, _ = self.call(response(status="incomplete", incomplete="max_output_tokens"))
        self.assertEqual((result.status, result.detail, result.text), ("incomplete", "max_output_tokens", None))
        result, _ = self.call(response(parts=[ResponseOutputRefusal.model_construct(type="refusal", refusal="No.")]))
        self.assertEqual((result.status, result.text), ("refused", None))

    def test_transient_errors_map_to_retryable(self):
        for error, reason in ((openai.APITimeoutError(request=REQUEST), "timeout"),
                              (openai.APIConnectionError(request=REQUEST), "connection_error"),
                              (status_error(openai.RateLimitError, 429), "rate_limit"),
                              (status_error(openai.InternalServerError, 503), "http_503")):
            with self.subTest(reason=reason), self.assertRaises(TransientProviderError) as raised:
                self.call(error)
            self.assertEqual(raised.exception.reason, reason)

    def test_client_errors_map_to_permanent_without_leaking_messages(self):
        for error, reason in ((status_error(openai.AuthenticationError, 401), "http_401"),
                              (status_error(openai.BadRequestError, 400), "http_400"),
                              (status_error(openai.NotFoundError, 404), "http_404")):
            with self.subTest(reason=reason), self.assertRaises(PermanentProviderError) as raised:
                self.call(error)
            self.assertEqual(str(raised.exception), reason)

    def test_client_is_built_with_sdk_retries_disabled(self):
        client = make_openai_client(api_key="synthetic-placeholder-key")
        self.assertEqual(client.max_retries, 0)


if __name__ == "__main__":
    unittest.main()
