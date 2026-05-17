"""FastAPI routes for old OT + API wrapper."""

from fastapi import APIRouter, HTTPException

from schemas import ClearOTSessionRequest, CreateOTSessionRequest, OTStepRequest
from server.ot_flow_service import OTFlowService


router = APIRouter(prefix="/api", tags=["old-ot-api"])
service = OTFlowService()


@router.get("/health")
def health_check():
    return {"status": "ok", "architecture": "old OT core + FastAPI wrapper"}


@router.get("/books/catalog")
def get_catalog(group_id: str = "default"):
    try:
        return service.get_public_catalog(group_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/books/encrypted-package/{group_id}")
def get_encrypted_group_package(group_id: str):
    """Return the whole encrypted group package.

    This avoids a single-book download endpoint, which would reveal the final
    chosen index to the server.
    """
    try:
        return service.get_encrypted_group_package(group_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ot/session")
def create_ot_session(body: CreateOTSessionRequest):
    try:
        return service.create_ot_session(group_id=body.group_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ot/step")
def ot_step(body: OTStepRequest):
    try:
        return service.perform_ot_step(
            session_id=body.session_id,
            level=body.level,
            h0=body.h0,
            h1=body.h1,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ot/session/clear")
def clear_ot_session(body: ClearOTSessionRequest):
    return service.clear_session(body.session_id)
