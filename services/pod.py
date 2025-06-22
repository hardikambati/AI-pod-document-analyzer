import logging
from data_models.pod import (
    PODRequest,
    ImageMaster,
    ReferenceData,
)
from services.llm import LLMService


logger = logging.getLogger("ai_pod_analysis")


class PODService:

    def __init__(self):
        self.llm_service = LLMService()

    def load_image_master(self, request: PODRequest) -> ImageMaster:
        """
        Initialize image master for processing.
        """
        image_master = ImageMaster(
            image_path=request.pod_image_url,
            reference_data=ReferenceData(awb_number=request.awb),
        )
        return image_master

    async def pipeline(self, request: PODRequest):
        """
        Triggers the pipeline to process the POD image and extract structured data using AI.
        """
        # intialize image master
        image_master = self.load_image_master(request=request)

        # run llm service
        image_master = self.llm_service.run(image_master=image_master)

        return image_master.model_dump_json()
