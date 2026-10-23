from contextlib import asynccontextmanager
import asyncio
import os
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .core import Engine, fixture_paths


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Question(Strict):
    query: str = Field(min_length=1, max_length=500)


class Citation(Strict):
    document: str = Field(max_length=100)
    chunk: str = Field(max_length=200)
    quote: str = Field(max_length=1000)
    revision: int
    source_sha256: str = Field(pattern="^[0-9a-f]{64}$")


class Proposal(Strict):
    order_id: str = Field(pattern="^QC-[0-9]{1,8}$")
    amount_cents: int = Field(gt=0, le=5000)
    citations: list[Citation] = Field(min_length=1, max_length=3)


def create_app(engine=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.engine = engine or Engine(os.environ.get("CAPSTONE_STATE", "state"), *fixture_paths())
        yield
        if engine is None:
            app.state.engine.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

    @app.middleware("http")
    async def size_limit(request: Request, call_next):
        # Bound streamed body too: Content-Length alone is insufficient.
        body = bytearray()
        try:
            async with asyncio.timeout(2):
                async for part in request.stream():
                    body.extend(part)
                    if len(body) > 8192:
                        return JSONResponse({"detail": "body too large"}, status_code=413)
        except TimeoutError:
            return JSONResponse({"detail": "body timeout"}, status_code=408)
        request._body = bytes(body)
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def validation(request, error):
        return JSONResponse({"detail": "invalid request"}, status_code=422)

    def token(authorization):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(401, "missing bearer")
        return authorization[7:]

    @app.exception_handler(PermissionError)
    async def denied(request, error):
        return JSONResponse({"detail": "denied"}, status_code=403)

    @app.exception_handler(ValueError)
    async def invalid(request, error):
        return JSONResponse({"detail": "invalid input"}, status_code=422)

    @app.get("/health")
    async def health():
        return {"status": "process_alive", "provider": "synthetic"}

    @app.post("/answers")
    async def ask(body: Question, authorization: Annotated[str | None, Header()] = None):
        return await app.state.engine.ask(token(authorization), body.query)

    @app.get("/orders/{order_id}")
    async def order(order_id: str, authorization: Annotated[str | None, Header()] = None):
        return app.state.engine.order(token(authorization), order_id)

    @app.post("/proposals")
    async def propose(body: Proposal, authorization: Annotated[str | None, Header()] = None):
        return app.state.engine.propose(token(authorization), body.order_id, body.amount_cents,
                                       [c.model_dump() for c in body.citations])

    @app.post("/actions/{key}/approve")
    async def approve(key: str, authorization: Annotated[str | None, Header()] = None):
        return app.state.engine.approve(token(authorization), key)

    @app.post("/actions/{key}/execute")
    async def execute(key: str, authorization: Annotated[str | None, Header()] = None):
        return app.state.engine.execute(token(authorization), key)

    return app
