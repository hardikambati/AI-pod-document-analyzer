import os
import logging
from datetime import datetime

from pydantic import ValidationError
from pydantic_ai import Agent, ImageUrl
from pydantic_ai import ModelHTTPError, UsageLimitExceeded

from data_models.pod import (
    ImageMaster,
    AnalysisData,
    AgentMetadata,
)


logger = logging.getLogger("ai_pod_analysis")


class LLMService:
    """
    LLM Service which implements call to AI for extracting results.
    """

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model_name = model
        
        if "gemini" in self.model_name and not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        self.text_prompt = "Extract the structured data from the following Image" 
        self.agent = Agent(
            model=self.model_name,
            result_type=AnalysisData,
            system_prompt = (
                "You are an image data extraction agent. Your task is to extract the following fields from a proof-of-delivery (POD) document image:\n\n"
                "- courier_partner\n"
                "- awb_number\n"
                "- recipient_name\n"
                "- recipient_address\n"
                "- recipient_signature\n"
                "- recipient_stamp\n"
                "- delivery_date\n"
                "- handwritten_notes\n"
                "- partial_delivery_note\n\n"
                "Extraction rules:\n"
                "1. For 'delivery_date', prefer the handwritten date near the signature/stamp. Do not return 'Ship Date' or 'Pickup Date'.\n"
                "2. For 'recipient_signature', only confirm presence (e.g., return 'Signed'). Do not attempt to OCR the signature.\n"
                "3. For 'handwritten_notes', extract any of the following keywords or their close variations, even if phrased differently or written informally:\n\n"
                "  KEYWORDS TO EXTRACT:\n"
                "  A. Box / Boxes\n"
                "  B. Short\n"
                "  C. Received\n"
                "  D. Damage / Damaged\n"
                "  E. Late / Delayed / Delivered\n"
                "  F. Delivery\n"
                "  G. Phone number / Ph no. / Phone\n"
                "  H. Digits (1-9) representing phone numbers or counts\n"
                "  I. OK\n"
                "  J. Verification\n"
                "  K. Condition\n"
                "  L. Returned\n"
                "  M. Loose\n"
                "  N. Qty / Quantity\n"
                "  O. Carton\n"
                "  P. Count\n\n"
                "INSTRUCTIONS:\n"
                "- Output a list of the keywords or phrases that are present in the handwritten note.\n"
                "- Match variants and similar meanings (e.g., 'ph no' → 'phone number', 'damaged' → 'damage').\n"
                "- Normalize extracted items to their canonical form (e.g., 'ph no' → 'phone number', 'qty' → 'quantity').\n"
                "- If a phone number is present (i.e., a 10-digit number), extract it separately.\n\n"
                "4. Return each field as a JSON key with value: `value`.\n"
                "   Example: \"recipient_name\": { \"value\": \"John Doe\"}\n"
                "5. If any field is missing or cannot be confidently determined from the image, set its value to null.\n"
                "6. If the image does not contain a proper POD document, return all fields as null.\n"
                "7. Only extract text that is clearly present in the image. DO NOT hallucinate, infer, fabricate, or lie in any text values.\n"
            ),
            instrument=True,
        )

        logger.info(f"AI Agent initialized with model: {self.model_name} and pydantic-ai Agent.")

    async def run(self, image_master: ImageMaster) -> ImageMaster:
        """
        Driver method.
        """       
        agent_metadata = AgentMetadata(
            model=self.model_name,
            start_timestamp=str(datetime.now()),
            metadata={"errors": []},
            tokens=None
        )

        awb = image_master.reference_data.awb_number
        logger.info(f"(AWB {awb}): Extracting structured analysis data...")

        image_part = ImageUrl(url=image_master.image_url)
 
        try:
            agent_result = await self.agent.run([image_part, self.text_prompt])
            extracted_data_result = agent_result.data

            if hasattr(agent_result, "usage"):
                token_usage = agent_result.usage()
                token_usage =  {
                    "request_tokens": token_usage.request_tokens,
                    "response_tokens": token_usage.response_tokens,
                    "total_tokens":token_usage.total_tokens
                }

            # populate extracted AI analysis data
            if extracted_data_result:
                image_master.analysis_data.text_quality_score = extracted_data_result.text_quality_score
                image_master.analysis_data.courier_partner = extracted_data_result.courier_partner
                image_master.analysis_data.awb_number = extracted_data_result.awb_number
                image_master.analysis_data.recipient_name = extracted_data_result.recipient_name
                image_master.analysis_data.recipient_address = extracted_data_result.recipient_address
                image_master.analysis_data.recipient_signature = extracted_data_result.recipient_signature
                image_master.analysis_data.recipient_stamp = extracted_data_result.recipient_stamp
                image_master.analysis_data.delivery_date = extracted_data_result.delivery_date
                image_master.analysis_data.handwritten_notes = extracted_data_result.handwritten_notes

            logger.info(f"(AWB {awb}): Analysis data extracted successfully.")

        except (ModelHTTPError, UsageLimitExceeded) as e:
            logger.error(f"(AWB {awb}): Resource limits reached, HTTP Error: {e}", exc_info=True)
            agent_metadata["metadata"]["errors"].append(str(e))
        
        except (ValidationError, AttributeError, ValueError, Exception) as e:
            logger.error(f"Step 1 (AWB {awb}): Failed during agent execution or validation: {e}", exc_info=True)
            token_usage = None
            agent_metadata["metadata"]["errors"].append(str(e))

        agent_metadata.end_timestamp = str(datetime.now())
        agent_metadata.tokens = token_usage

        image_master.agent_metadata = agent_metadata

        return image_master
