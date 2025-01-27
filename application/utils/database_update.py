# Для докера
import logging
import asyncio

from application.db.database_users import fetch_user_ids
from application.utils.admin_check import update_user_status_based_on_admin


async def update_all_users_status():
    user_ids = await fetch_user_ids()

    tasks = [update_user_status_based_on_admin(user_id) for (user_id,) in user_ids]
    await asyncio.gather(*tasks)
       
async def run_updates():
    logging.info("Starting user status updates")
    await update_all_users_status()
    logging.info("User status updates completed")

