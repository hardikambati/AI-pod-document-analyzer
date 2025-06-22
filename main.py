import logging

from fastapi import (
    status,
    FastAPI,
    APIRouter,
)
from fastapi_utils.cbv import cbv
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

  
@cbv(router)
class RootView:

    def __init__(self):
        self.service = PODService()

    @router.get("/")
    async def read():
        """
        Server status.
        """
        payload = {
            "message": "Server is up and running",
        }
        return JSONResponse(content=payload, status_code=status.HTTP_200_OK)



@cbv(router)
class PODAnalysisView:

    def __init__(self):
        self.service = PODService()

    @router.post("/analyze_pod")
    async def extract_pod_data(self, request: PODRequest):
        """
        Extracts POD metadata from images using a pipeline that includes AI image data extraction.
        """
        response = self.service.pipeline(request)
        return JSONResponse(content=response)

app.include_router(router)