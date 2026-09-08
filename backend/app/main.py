from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="VCF Studio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "vcf-studio", "version": "0.1.0"}

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.vcenter import router as vcenter_router

app.include_router(vcenter_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def safe_validation_error(request, exc):
    # Do not echo input/context: malformed credential fields can contain secrets.
    return JSONResponse(status_code=422, content={"detail": [
        {"loc": list(error["loc"]), "type": error["type"], "msg": "Invalid request field"}
        for error in exc.errors()
    ]})
