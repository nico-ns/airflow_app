from fastapi import FastAPI, Request
from ._cache import Cache, CacheChecker
import logging
import pathlib

pathlib.Path('/web/app/log').mkdir(parents=True, exist_ok=True) 

logging.basicConfig(level=logging.INFO, filename="./app/log/APIlog.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

INTERVAL = 20
cache = Cache()
cache_checker = CacheChecker(cache.is_it_time_to_dump, INTERVAL) # check every INTERVAL seconds

     
app = FastAPI()

MAX_CACHE_SIZE = 300


@app.post("/ingest")
async def ingest_event(request: Request):
    content = await request.json()
    print(content)

    index = MAX_CACHE_SIZE - len(cache)
    print(index)
    
    if index > 0:
        # Cache still has some capacity, add element
        cache[index] = content 
    else:
        # Cache is full, dump and restart from 0
        message = "Cache is full, dumping to file and resetting."
        cache.dump_to_file(message)
        cache[MAX_CACHE_SIZE] = content
    
    return {"res": 200}



# def validate_request(req):
#     try:
#         content = request.json
#     except Exception as e:
#         return 503, 503 Bad request
    
#     keys = set(direction,extension,id,retry,size,
#                 status,stream,timestamp,chunks_metadata.protocol,
#                 chunks_metadata.time,chunks_metadata.type,client.channel,
#                 client.client_id,client.environment.type,client.id,client.internal,
#                 client.user_id,client.version.sdk,configuration.protocol,
#                 configuration.time,configuration.type,file_metadata.protocol,
#                 file_metadata.time,file_metadata.type,time.backend,time.chunks,time.total)
#     if set(content.keys()) == keys:
#         return 200,  content

#     else:
#         return 503, 503 Bad request