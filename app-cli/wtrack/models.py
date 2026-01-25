from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PayloadModel(BaseModel):
    model_config = ConfigDict(extra='ignore', frozen=True, populate_by_name=True)


class WeightEntry(PayloadModel):
    date: str
    weight: float


class TodayStatus(PayloadModel):
    has_entry: bool = Field(alias='hasEntry')
    weight: float | None = None

    @model_validator(mode='after')
    def _validate_weight(self) -> TodayStatus:
        if self.has_entry and self.weight is None:
            raise ValueError("Field 'weight' must be provided when 'hasEntry' is true.")
        return self


class Streak(PayloadModel):
    current: int
    longest: int


class Adherence(PayloadModel):
    window: int
    days_missed: int = Field(alias='daysMissed')


class StatusReport(PayloadModel):
    today: TodayStatus
    streak: Streak
    adherence: tuple[Adherence, ...] = ()


class WeightStats(PayloadModel):
    max: float
    min: float
    avg: float


class ReportData(PayloadModel):
    data: tuple[WeightEntry, ...] = ()
    stats: WeightStats | None = None
