"""API 整合測試。"""


def test_evaluate_endpoint(client):
    resp = client.post("/api/v1/evaluate", json={
        "address_or_lot": "臺北市大安區仁愛路三段1號",
        "site_area_sqm": 500,
        "intended_use": "residential",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"].startswith("TPE-")
    assert data["final_status"] in ["AUTO_PASS", "AUTO_FAIL", "REVIEW_REQUIRED", "HIGH_RISK"]
    assert len(data["legal_basis"]) > 0


def test_evaluate_invalid_input(client):
    resp = client.post("/api/v1/evaluate", json={
        "address_or_lot": "",
        "site_area_sqm": -1,
        "intended_use": "residential",
    })
    assert resp.status_code == 422


def test_evaluate_saves_to_history(client):
    """評估後可透過 project_id 回查報告。"""
    resp = client.post("/api/v1/evaluate", json={
        "address_or_lot": "臺北市信義區松仁路100號",
        "site_area_sqm": 300,
        "intended_use": "office",
    })
    assert resp.status_code == 200
    project_id = resp.json()["project_id"]

    resp2 = client.get(f"/api/v1/projects/{project_id}")
    assert resp2.status_code == 200
    assert resp2.json()["project_id"] == project_id


def test_project_not_found(client):
    """查詢不存在的 project_id → 404。"""
    resp = client.get("/api/v1/projects/NONEXISTENT")
    assert resp.status_code == 404


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
