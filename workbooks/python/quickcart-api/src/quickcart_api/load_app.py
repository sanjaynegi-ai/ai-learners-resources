"""Explicit lab factory: extra routes are absent from the normal packaged API."""
from typing import Annotated, Literal
from fastapi import Body
from fastapi.responses import JSONResponse

from .app import PrincipalDep, TicketIdPath, create_app
from .serving import ServingLab


def create_load_app(settings, **limits):
    app = create_app(settings)
    lab = ServingLab(app.state.store, **limits)
    app.state.serving_lab = lab

    @app.post("/lab/tickets/{ticket_id}/triage")
    async def job(ticket_id: TicketIdPath, principal: PrincipalDep,
                  scenario: Annotated[Literal["normal", "failure", "timeout"], Body()] = "normal"):
        code, result = await lab.submit(principal.tenant, ticket_id, scenario)
        return JSONResponse(result, status_code=code,
                            headers={"Retry-After": "1"} if code == 429 else None)

    @app.post("/lab/tickets/{ticket_id}/cancel")
    async def cancel(ticket_id: TicketIdPath, principal: PrincipalDep):
        # Unknown and foreign tickets give the same not-cancelled result.
        return {"cancel_requested": lab.cancel(principal.tenant, ticket_id)}

    @app.get("/lab/stats")
    async def stats(principal: PrincipalDep):
        return lab.stats(principal.tenant)

    return app
