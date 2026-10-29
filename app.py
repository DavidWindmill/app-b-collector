"""App B: recibe mediciones y las entrega al procesador propio."""
import os
import httpx
from fastapi import FastAPI,HTTPException
from qos_faults import FaultProfile
fault_profile = FaultProfile()
app=FastAPI()
PROCESSOR_URL=os.environ.get('PROCESSOR_URL','http://processor00:8080')
@app.get('/health')
def health():return {'status':'ok'}
@app.get('/metrics')
def metrics():return fault_profile.decorate({'response_time_ms':24,'execution_time':6,'availability':24,'reliability':0.01,'cost':0.1,'status':'ok'})
@app.post('/reading')
async def reading(payload:dict):
    try:
        async with httpx.AsyncClient(timeout=4,trust_env=False) as client:
            r=await client.post(PROCESSOR_URL+'/save',json=payload)
        r.raise_for_status()
    except httpx.HTTPError as exc: raise HTTPException(503,'Processor not reachable') from exc
    return {'accepted':True}


@app.post('/admin/simulate')
def inject_qos_fault(payload: dict):
    """Modifica TEMPORALMENTE métricas expuestas por este contenedor real."""
    from fastapi import HTTPException
    try:
        return fault_profile.inject(payload)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
