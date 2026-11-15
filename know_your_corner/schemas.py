"""Pydantic models for the data, tool arguments and structured output."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

MetroLine = Literal["blue", "yellow", "green", "red"]


class Neighborhood(BaseModel):
    name: str
    aliases: list[str] = []
    rent_room_avg: int | None = Field(None, description="Average monthly rent for a room, EUR")
    rent_t1_avg: int | None = Field(None, description="Average monthly rent for a T1 flat, EUR")
    rent_source: str | None = None
    rent_date: date | None = None
    metro_lines: list[MetroLine] = []
    nearest_stations: list[str] = []
    train_or_bus_notes: str | None = None
    student_notes: str | None = None
    source_urls: list[str] = []
    compiled_by: str | None = None
    compiled_on: date | None = None


class ListNeighborhoodsArgs(BaseModel):
    max_room_rent: int | None = Field(
        None, description="Only neighborhoods whose average room rent is at most this many EUR per month"
    )
    metro_line: MetroLine | None = Field(None, description="Only neighborhoods on this Lisbon Metro line")


class GetNeighborhoodArgs(BaseModel):
    name: str = Field(description="Neighborhood name as the user wrote it, e.g. 'Arroios'")