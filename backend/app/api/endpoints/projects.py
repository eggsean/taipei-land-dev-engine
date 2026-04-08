from fastapi import APIRouter

router = APIRouter()

# MVP: 歷史報告暫存記憶體中
_history: dict = {}


@router.get("/projects/{project_id}")
def get_project(project_id: str):
    report = _history.get(project_id)
    if not report:
        return {"error": "Project not found", "project_id": project_id}
    return report
