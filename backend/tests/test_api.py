"""End-to-end API flows for the learning loop:
profile -> adventure -> play missions -> hints/remediation -> progress."""


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

def test_create_and_fetch_student(client):
    resp = client.post(
        "/api/students",
        json={"name": "Leo", "age": 14, "interests": ["football"]},
    )
    assert resp.status_code == 201
    sid = resp.json()["id"]

    resp = client.get(f"/api/students/{sid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Leo"
    assert resp.json()["interests"] == ["football"]


def test_invalid_profile_rejected(client):
    resp = client.post("/api/students", json={"name": "", "age": 2})
    assert resp.status_code == 422


def test_missing_student_404(client):
    assert client.get("/api/students/999999").status_code == 404


# ---------------------------------------------------------------------------
# Adventure generation
# ---------------------------------------------------------------------------

def test_create_adventure_generates_arc_and_missions(adventure):
    assert adventure["generator"] == "template"  # no API key in tests
    assert adventure["format"] == "mission-map-2d"
    arc = adventure["story_arc"]
    assert arc["theme"] == "space"  # matched from interests
    assert arc["story_title"]
    assert arc["mentor_character"]["name"]
    missions = adventure["missions"]
    assert [m["module"] for m in missions] == ["variables", "conditionals", "loops"]
    for m in missions:
        assert m["hidden_tests"]
        assert len(m["hints"]) >= 3
        # internal field must never leak to the client
        assert "reference_solution" not in m


def test_get_adventure_roundtrip(client, adventure):
    resp = client.get(f"/api/adventures/{adventure['id']}")
    assert resp.status_code == 200
    assert resp.json()["story_arc"] == adventure["story_arc"]


def test_adventure_for_missing_student_404(client):
    resp = client.post("/api/adventures", json={"student_id": 999999})
    assert resp.status_code == 404


def test_initial_progress_unlocks_only_first_mission(client, adventure):
    resp = client.get(f"/api/adventures/{adventure['id']}/progress")
    assert resp.status_code == 200
    progress = resp.json()
    statuses = [m["status"] for m in progress["missions"]]
    assert statuses == ["available", "locked", "locked"]
    assert progress["completed_count"] == 0
    assert progress["total_count"] == 3


# ---------------------------------------------------------------------------
# Submissions: failure -> escalating hints -> remediation; success -> advance
# ---------------------------------------------------------------------------

def submit(client, adventure, mission_idx, passed, code="x = 1"):
    mission = adventure["missions"][mission_idx]
    return client.post(
        "/api/submissions",
        json={
            "adventure_id": adventure["id"],
            "mission_id": mission["mission_id"],
            "code": code,
            "passed": passed,
            "test_results": [],
        },
    )


def test_failures_escalate_hints_then_remediate(client, adventure):
    mission = adventure["missions"][0]

    r1 = submit(client, adventure, 0, passed=False).json()
    assert r1["passed"] is False
    assert r1["next_action"] == "retry"
    assert r1["hint_level"] == 1
    assert r1["hint"] == mission["hints"][0]
    assert r1["remediation"] is None
    assert r1["story_feedback"] == mission["failure_feedback"]["story_feedback"]

    r2 = submit(client, adventure, 0, passed=False).json()
    assert r2["hint_level"] == 2
    assert r2["hint"] == mission["hints"][1]

    r3 = submit(client, adventure, 0, passed=False).json()
    assert r3["next_action"] == "remediate"
    assert r3["remediation"]["smaller_subtask"]
    assert r3["attempts"] == 3

    # hint level never overflows the hint list
    r4 = submit(client, adventure, 0, passed=False).json()
    assert r4["hint_level"] <= len(mission["hints"])


def test_success_advances_story_and_unlocks_next(client, adventure):
    mission = adventure["missions"][0]
    r = submit(client, adventure, 0, passed=True).json()
    assert r["passed"] is True
    assert r["next_action"] == "next"
    assert r["story_feedback"] == mission["success_feedback"]["story_feedback"]
    assert r["hint"] is None

    progress = client.get(f"/api/adventures/{adventure['id']}/progress").json()
    statuses = [m["status"] for m in progress["missions"]]
    assert statuses == ["completed", "available", "locked"]
    assert progress["completed_count"] == 1


def test_completing_final_mission_finishes_the_arc(client, adventure):
    for idx in range(3):
        r = submit(client, adventure, idx, passed=True).json()
    assert r["next_action"] == "finish"

    progress = client.get(f"/api/adventures/{adventure['id']}/progress").json()
    assert progress["completed_count"] == 3
    assert all(m["status"] == "completed" for m in progress["missions"])


def test_submission_to_unknown_mission_404(client, adventure):
    resp = client.post(
        "/api/submissions",
        json={
            "adventure_id": adventure["id"],
            "mission_id": "no-such-mission",
            "code": "x = 1",
            "passed": True,
        },
    )
    assert resp.status_code == 404


def test_attempts_are_persisted_for_telemetry(client, adventure):
    submit(client, adventure, 0, passed=False, code="broken =")
    submit(client, adventure, 0, passed=True, code="oxygen_level = 100")
    progress = client.get(f"/api/adventures/{adventure['id']}/progress").json()
    assert progress["missions"][0]["attempts"] == 2
