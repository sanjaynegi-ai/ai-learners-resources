"""Inspectable reference for the independent DELETE exercise.

Consulting this file is disclosed assistance, not independent evidence. Your own implementation
belongs in src/quickcart_api/app.py on the existing ``router``.
"""
from fastapi import APIRouter, HTTPException, Response, status

from quickcart_api.app import NOT_FOUND, PrincipalDep, StoreDep, TicketIdPath

router = APIRouter()


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: TicketIdPath, principal: PrincipalDep, store: StoreDep) -> Response:
    # Role first: an agent learns nothing about whether the ticket exists.
    if principal.role != "supervisor":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Supervisor role required")
    # Tenant comes from the token, never from the path or body.
    if not store.delete(principal.tenant, ticket_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
