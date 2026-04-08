import logging

from fastapi import APIRouter

from app.api.endpoints.projects import save_report
from app.rule_engine.pipeline import run_pipeline
from app.schemas.input import SiteInput
from app.schemas.output import EvaluationReport

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/evaluate", response_model=EvaluationReport)
def evaluate_site(site_input: SiteInput) -> EvaluationReport:
    logger.info("Received input: %s", site_input.model_dump())
    try:
        report = run_pipeline(site_input)
        save_report(report.project_id, report.model_dump())
        return report
    except Exception:
        logger.exception("Pipeline error")
        raise
