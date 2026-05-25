from __future__ import annotations

import asyncio

from app.services.telegram import sync_direct_telegram_webhook, sync_telegram_commands


async def main() -> None:
    webhook_result = await sync_direct_telegram_webhook()
    commands_result = await sync_telegram_commands()
    print(webhook_result)
    print(commands_result)


if __name__ == "__main__":
    asyncio.run(main())
