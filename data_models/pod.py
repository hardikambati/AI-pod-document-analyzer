from typing import Any, Dict, Optional
from pydantic import BaseModel, HttpUrl, Field


class PODRequest(BaseModel):
    awb: str
    pod_image_url: str


class AgentMetadata(BaseModel):
    model: str = Field(..., description="Model used")
    start_timestamp: Optional[str] = Field(None, description="Start time of agent execution")
    end_timestamp: Optional[str] = Field(None, description="End time of agent execution")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Scratchpad for agent extraction process, storing intermediate results")
    tokens: Optional[Dict[str, Any]] = Field(None, description="Agent token consumption for cost estimation")


class AnalysisData(BaseModel):
    text_quality_score: int = Field(default=0, description="Quality score of text in the image (0-10)")
    courier_partner: Optional[str] = Field(default=None, description="Courier partner name")
    awb_number: Optional[str] = Field(default=None, description="AWB Number of shipment, usually near or below barcode")
    recipient_name: Optional[str] = Field(default=None, description="Recipient's name")
    recipient_address: Optional[str] = Field(default=None, description="Recipient's address details")
    recipient_signature: Optional[bool] = Field(default=False, description="Recipient's signature present or not")
    recipient_stamp: Optional[bool] = Field(default=None, description="Stamp details present or not")
    delivery_date: Optional[str] = Field(default=None, description="Delivery date")
    handwritten_notes: Optional[str] = Field(default=None, description="Handwritten notes")


class ReferenceData(BaseModel):
    awb_number: Optional[str] = Field(default=None, description="AWB Number of shipment extracted from database")


class ImageMaster(BaseModel):
    image_url: str = Field(..., description="URL of the proof of delivery image")
    reference_data: Optional[ReferenceData] = Field(default=None, description="Reference data for the image")
    analysis_data: Optional[AnalysisData] = Field(default=None, description="AnalysisData data extracted by AI")
    agent_metadata: Optional[AgentMetadata] = Field(default=None, description="Metadata for the agent execution")