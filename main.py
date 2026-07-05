from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import time
import uuid

app = FastAPI()

START_TIME = time.time()
HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests")
LOGS = deque(maxlen=1000)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    HTTP_REQUESTS.inc()
    request_id = str(uuid.uuid4())
    LOGS.append({
        "level":"INFO",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": request.url.path,
        "request_id": request_id
    })
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/work")
def work(n:int=1):
    for _ in range(n):
        pass
    return {"email":"24f2004747@ds.study.iitm.ac.in","done":n}

@app.get("/healthz")
def healthz():
    return {"status":"ok","uptime_s":time.time()-START_TIME}

@app.get("/logs/tail")
def logs_tail(limit:int=10):
    return list(LOGS)[-limit:]

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
