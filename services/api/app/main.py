import logging
from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.user import router as user_router
from routers.project import router as project_router
from routers.brain_pile import router as brain_pile_router

app = FastAPI(
    title="agcore"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(project_router, prefix="/project", tags=["project"])
app.include_router(brain_pile_router, prefix="/brain_pile", tags=["brain_pile"])

logging.basicConfig(level=logging.DEBUG, force=True)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"caught exception: {exc.detail}", exc_info=True)
    return exc
    
@app.get("/health")
async def health():
    return {"status": "ok"}