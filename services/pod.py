import logging
from data_models.pod import (
    PODRequest,
    ImageMaster,
    AnalysisData,
    ReferenceData,
)
from services.llm import LLMService


logger = logging.getLogger("ai_pod_analysis")


class PODService:

    def load_image_master(self, request: PODRequest) -> ImageMaster:
        """
        Initialize image master for processing.
        """
        analysis_data = AnalysisData(
            text_quality_score=0,
            courier_partner=None,
            awb_number=None,
            recipient_name=None,
            recipient_address=None,
            recipient_signature=None,
            recipient_stamp=None,
            delivery_date=None,
            handwritten_notes=None,
        )
        image_master = ImageMaster(
            image_url=request.pod_image_url,
            reference_data=ReferenceData(awb_number=request.awb),
            analysis_data=analysis_data,
            agent_metadata=None,
        )
        return image_master

    async def pipeline(self, request: PODRequest):
        """
        Triggers the pipeline to process the POD image and extract structured data using AI.
        """
        # intialize image master
        image_master = self.load_image_master(request=request)

        # run llm service
        image_master = await LLMService().run(image_master=image_master)

        return image_master.model_dump()
