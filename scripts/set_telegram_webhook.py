from __future__ import annotations

import asyncio

from app.services.telegram import sync_direct_telegram_webhook


async def main() -> None:
    result = await sync_direct_telegram_webhook()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

