from cachetools import TTLCache

view_cache = TTLCache(maxsize=10000, ttl=3600)
