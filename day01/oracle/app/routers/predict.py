from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.horoscope import horoscope_for
from app.schemas import (
    BurnoutRequest,
    BurnoutResponse,
    HoroscopeResponse,
    IncomeRequest,
    IncomeResponse,
    MarriageRequest,
    MarriageResponse,
)

router = APIRouter()

INCOME_DISCLAIMER = (
    "A statistical estimate from the 2025 Stack Overflow Developer Survey. Not financial advice."
)
MARRIAGE_DISCLAIMER = "Trained on completely invented data. For entertainment only."

DAYS_PER_YEAR = 365.25


@router.post("/predict/income", response_model=IncomeResponse)
async def predict_income(body: IncomeRequest, request: Request) -> IncomeResponse:
    models = request.app.state.models
    income = models.predict_income(body.model_dump(exclude={"name"}))
    if body.name:
        request.app.state.store.record_income(body.name, income)
    return IncomeResponse(
        predicted_income_usd=round(income, 2),
        model_version=models.income_version,
        disclaimer=INCOME_DISCLAIMER,
    )


@router.post("/predict/marriage", response_model=MarriageResponse)
async def predict_marriage(body: MarriageRequest, request: Request) -> MarriageResponse:
    models = request.app.state.models
    years = models.predict_marriage_years(body.model_dump())
    return MarriageResponse(
        predicted_date=date.today() + timedelta(days=round(years * DAYS_PER_YEAR)),
        years_from_now=round(years, 1),
        model_version=models.marriage_version,
        disclaimer=MARRIAGE_DISCLAIMER,
    )


@router.get("/horoscope", response_model=HoroscopeResponse)
async def horoscope(
    birthday: Annotated[date, Query(description="YYYY-MM-DD")],
) -> HoroscopeResponse:
    sign, message = horoscope_for(birthday)
    return HoroscopeResponse(sign=sign, message=message)


BURNOUT_DISCLAIMER = (
    "This is a demonstration estimate, not a clinical assessment or validated prediction."
)


@router.post("/predict/burnout", response_model=BurnoutResponse)
async def predict_burnout(
    body: BurnoutRequest,
    request: Request,
) -> BurnoutResponse:
    models = request.app.state.models

    # Demonstration scoring logic; replace with a trained model.
    workload_score = (
        body.meetings_per_week * 0.05
        + body.on_call_weeks_per_year * 0.03
        + min(body.unread_emails, 100_000) / 10_000 * 0.1
    )

    years = max(0.5, 10.0 - workload_score)

    return BurnoutResponse(
        predicted_years_until_burnout=round(years, 2),
        model_version=getattr(models, "burnout_version", "demo-v1"),
        disclaimer=BURNOUT_DISCLAIMER,
    )
