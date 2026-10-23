from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Path, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import __version__
from .config import Principal, Settings, load_settings_from_env
from .models import Ticket, TicketIn
from .store import DuplicateTicket, IdempotencyConflict, TicketGone, TicketStore
from .triage import MockTriageProvider, TriageProvider, TriageTimedOut, TriageUnavailable, classify_bounded

bearer = HTTPBearer(auto_error=False)
TicketIdPath = Annotated[str, Path(pattern=r"^QC-[0-9]{3,8}$")]
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", pattern=r"^[A-Za-z0-9_-]{8,64}$")]


def get_store(request: Request) -> TicketStore:
    return request.app.state.store


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_provider(request: Request) -> TriageProvider:
    return request.app.state.provider


def current_principal(
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    principal = settings.authenticate(credentials.credentials) if credentials else None
    if principal is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    return principal


PrincipalDep = Annotated[Principal, Depends(current_principal)]
StoreDep = Annotated[TicketStore, Depends(get_store)]
NOT_FOUND = "Ticket not found"  # Same answer for "absent" and "another tenant's": no existence leak.

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness only: the process answers. It does not prove a provider or database is usable."""
    return {"status": "ok"}


@router.post("/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(body: TicketIn, key: IdempotencyKey, principal: PrincipalDep,
                        store: StoreDep, response: Response) -> Ticket:
    try:
        ticket, created = store.create(principal.tenant, key, body)
    except IdempotencyConflict:
        raise HTTPException(status.HTTP_409_CONFLICT, "Idempotency-Key reused with a different request") from None
    except DuplicateTicket:
        raise HTTPException(status.HTTP_409_CONFLICT, "ticket_id already exists") from None
    except TicketGone:
        raise HTTPException(status.HTTP_409_CONFLICT, "The ticket created with this key was deleted") from None
    if not created:
        response.status_code = status.HTTP_200_OK
    return ticket


@router.get("/tickets/{ticket_id}")
async def read_ticket(ticket_id: TicketIdPath, principal: PrincipalDep, store: StoreDep) -> Ticket:
    ticket = store.get(principal.tenant, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return ticket


@router.post("/tickets/{ticket_id}/triage")
async def triage_ticket(ticket_id: TicketIdPath, principal: PrincipalDep, store: StoreDep,
                        settings: Annotated[Settings, Depends(get_settings)],
                        provider: Annotated[TriageProvider, Depends(get_provider)]) -> Ticket:
    ticket = store.get(principal.tenant, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)  # Checked before any provider spend.
    if ticket.status == "triaged":
        return ticket  # Repeat requests do not pay for another provider call.
    try:
        category = await classify_bounded(provider, ticket, settings.triage_timeout)
    except TriageTimedOut:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Triage provider timed out") from None
    except TriageUnavailable:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Triage provider unavailable") from None
    updated = store.set_category(principal.tenant, ticket_id, category)
    if updated is None:  # Deleted while the provider call was in flight.
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return updated


async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Report where and why validation failed without echoing the submitted values."""
    details = [{"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]} for error in exc.errors()]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": details})


def create_app(settings: Settings, provider: TriageProvider | None = None) -> FastAPI:
    """Build an isolated app: each call gets its own store, so tests never share state."""
    app = FastAPI(title="QuickCart synthetic ticket API", version=__version__)
    app.state.settings = settings
    app.state.store = TicketStore()
    app.state.provider = provider or MockTriageProvider()
    app.add_exception_handler(RequestValidationError, validation_error)
    app.include_router(router)
    return app


def create_app_from_env() -> FastAPI:
    """Factory for ``uvicorn --factory``; fails at startup if configuration is missing or invalid."""
    return create_app(load_settings_from_env())
