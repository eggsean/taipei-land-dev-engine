from fastapi import APIRouter, HTTPException

router = APIRouter()

# MVP: 歷史報告暫存記憶體中
_history: dict = {}


def save_report(project_id: str, report: dict) -> None:
    """供 evaluate endpoint 呼叫，將評估結果存入歷史。"""
    _history[project_id] = report


@router.get("/projects/{project_id}")
def get_project(project_id: str):
    report = _history.get(project_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return report
