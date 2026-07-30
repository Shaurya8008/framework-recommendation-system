def test_healthcheck(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "FrameworkFit API"


def test_list_frameworks(client):
    res = client.get("/frameworks")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 16  # All 16 seeded frameworks
    slugs = [f["slug"] for f in data]
    assert "iso-14001" in slugs
    assert "ghg-protocol" in slugs
    assert "csrd" in slugs


def test_get_framework(client):
    res = client.get("/frameworks/iso-14001")
    assert res.status_code == 200
    data = res.json()
    assert data["slug"] == "iso-14001"
    assert data["stage"] == "manage"


def test_create_and_get_profile(client, sample_profile_dict):
    # 1. Create profile
    res = client.post("/profiles", json=sample_profile_dict)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    assert data["organizationName"] == "Acme Manufacturing"
    assert data["industry"] == "manufacturing"

    # 2. Get profile
    res2 = client.get("/profiles/1")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["organizationName"] == "Acme Manufacturing"


def test_recommend_inline_profile(client, sample_profile_dict):
    res = client.post("/recommend", json=sample_profile_dict)
    assert res.status_code == 200
    data = res.json()
    assert "profileSummary" in data
    assert "stages" in data
    assert set(data["stages"].keys()) == {"manage", "measure", "report", "improve"}


def test_recommend_by_profile_id_and_history(client, sample_profile_dict):
    # 1. Create profile
    res_prof = client.post("/profiles", json=sample_profile_dict)
    profile_id = res_prof.json()["id"]

    # 2. Call recommend with profile_id
    res_rec = client.post("/recommend", json={"profile_id": profile_id})
    assert res_rec.status_code == 200
    data_rec = res_rec.json()
    assert "profileSummary" in data_rec

    # 3. Check past recommendations history endpoint
    res_hist = client.get(f"/recommendations/{profile_id}")
    assert res_hist.status_code == 200
    hist = res_hist.json()
    assert len(hist) > 0
    assert "slug" in hist[0]
    assert "score" in hist[0]
    assert "reason" in hist[0]
