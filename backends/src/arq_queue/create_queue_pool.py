from arq import create_pool, cron
from arq.connections import RedisSettings
from env import env_queue_host, env_queue_port

# V3 ARQ
# --- queue creator
async def create_queue_pool():
    return await create_pool(RedisSettings(host=env_queue_host(), port=env_queue_port()))

