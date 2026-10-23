import argparse
import asyncio
import json
from pathlib import Path
from .batch import collect
from .models import InputError, parse_ticket, summarize


def main() -> None:
    parser = argparse.ArgumentParser(description='Local synthetic ticket summary; no model or network')
    parser.add_argument('fixture', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.fixture.read_text(encoding='utf-8-sig'))
        if not isinstance(data, list) or len(data) > 20:
            raise InputError('Fixture requires at most twenty tickets')
        tickets = [parse_ticket(item) for item in data]
        async def mock_provider(ticket):
            await asyncio.sleep(0)
            return f'{ticket.ticket_id}: inspected'
        results = asyncio.run(collect(tickets, mock_provider))
        print(json.dumps({'summary': summarize(tickets), 'results': results, 'mode':'offline synthetic'}, sort_keys=True))
    except (InputError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'Cannot inspect fixture: {type(error).__name__}; no raw payload logged')
