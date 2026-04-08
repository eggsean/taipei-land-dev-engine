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


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
