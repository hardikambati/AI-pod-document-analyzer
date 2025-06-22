import logging

from fastapi import (
    status,
    FastAPI,
    APIRouter,
)
from fastapi.responses import JSONResponse

# Internal imports
from services.pod import PODService
from data_models.pod import PODRequest


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_pod_analysis")


app = FastAPI(
    title="POD Analysis",
    description="API to extract structured information from Proof of Delivery (POD) images.",
    version="1.0.0"
)
router = APIRouter()


class RootView:

    @router.get("/")
    async def read():
        payload = {
            "message": "Server is online and ready",
        }
        return JSONResponse(content=payload, status_code=status.HTTP_200_OK)


class PODAnalysisView:

    def __init__(self):
        self.service = PODService()

    @router.post("/analyze_pod")
    async def extract_pod_data(self, request: PODRequest):
        response = self.service.pipeline(request=request)
        return JSONResponse(
            content=response,
            status_code=status.HTTP_200_OK
        )

app.include_router(router)