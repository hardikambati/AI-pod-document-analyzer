import logging

from fastapi import (
    status,
    FastAPI,
    APIRouter,
)
from dotenv import load_dotenv
from fastapi_utils.cbv import cbv
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from pydantic import ValidationError

# Internal imports
from services.pod import PODService
from data_models.pod import PODRequest


# Load env variables
load_dotenv()


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

    @router.get("/")
    async def read(self):
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
        try:
            response = await self.service.pipeline(request)
            return JSONResponse(content=response, status_code=status.HTTP_200_OK)
        except ValidationError as e:
            return JSONResponse(content={"detail": e.errors()}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except ValueError as e:
            return JSONResponse(content={"detail": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JSONResponse(content={"detail": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
app.include_router(router)