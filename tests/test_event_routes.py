from datetime import timedelta


def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_api_events_returns_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_api_events_mode_upcoming(client, seeded_calendar_data):
    response = client.get("/api/events?mode=upcoming")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Upcoming Match"


def test_get_api_events_filter_by_sport(client, seeded_calendar_data):
    football_id = seeded_calendar_data["sports"]["football"].id
    response = client.get(f"/api/events?mode=all&sport_id={football_id}")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["sport_id"] == football_id


def test_get_api_events_filter_by_event_date(client, seeded_calendar_data):
    target_date = seeded_calendar_data["events"]["upcoming"].event_date.isoformat()
    response = client.get(f"/api/events?event_date={target_date}")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["event_date"] == target_date


def test_get_api_event_by_id_found(client, seeded_calendar_data):
    event_id = seeded_calendar_data["events"]["upcoming"].id
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_get_api_event_by_id_not_found(client, seeded_calendar_data):
    response = client.get("/api/events/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_post_api_events_rejects_same_home_away(client, seeded_calendar_data):
    event_date = seeded_calendar_data["events"]["upcoming"].event_date.isoformat()
    football_id = seeded_calendar_data["sports"]["football"].id
    ucl_id = seeded_calendar_data["competitions"]["ucl"].id
    real_id = seeded_calendar_data["teams"]["real"].id
    venue_id = seeded_calendar_data["venue"].id

    response = client.post(
        "/api/events",
        json={
            "title": "Invalid Same Teams",
            "event_date": event_date,
            "event_time_utc": "20:00:00",
            "status": "scheduled",
            "stage_name": "Knockout",
            "stage_ordering": 1,
            "description": "Invalid test",
            "sport_id": football_id,
            "competition_id": ucl_id,
            "home_team_id": real_id,
            "away_team_id": real_id,
            "venue_id": venue_id,
        },
    )
    assert response.status_code == 400
    assert "must be different" in response.json()["detail"]


def test_post_api_events_rejects_duplicate_event(client, seeded_calendar_data):
    existing = seeded_calendar_data["events"]["upcoming"]
    response = client.post(
        "/api/events",
        json={
            "title": "Duplicate Upcoming Match",
            "event_date": existing.event_date.isoformat(),
            "event_time_utc": existing.event_time_utc.isoformat(),
            "status": "scheduled",
            "stage_name": "Group Stage",
            "stage_ordering": 1,
            "description": "Duplicate test",
            "sport_id": existing._sport_id,
            "competition_id": existing._competition_id,
            "home_team_id": existing._home_team_id,
            "away_team_id": existing._away_team_id,
            "venue_id": existing._venue_id,
        },
    )
    assert response.status_code == 400
    assert "Duplicate event exists" in response.json()["detail"]


def test_post_api_events_creates_valid_event(client, seeded_calendar_data):
    football_id = seeded_calendar_data["sports"]["football"].id
    ucl_id = seeded_calendar_data["competitions"]["ucl"].id
    real_id = seeded_calendar_data["teams"]["real"].id
    city_id = seeded_calendar_data["teams"]["city"].id
    venue_id = seeded_calendar_data["venue"].id
    target_date = seeded_calendar_data["events"]["upcoming"].event_date + timedelta(days=1)

    response = client.post(
        "/api/events",
        json={
            "title": "Valid New Match",
            "event_date": target_date.isoformat(),
            "event_time_utc": "21:00:00",
            "status": "scheduled",
            "stage_name": "Semi Final",
            "stage_ordering": 2,
            "description": "Valid creation test",
            "sport_id": football_id,
            "competition_id": ucl_id,
            "home_team_id": real_id,
            "away_team_id": city_id,
            "venue_id": venue_id,
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Valid New Match"
    assert payload["competition_id"] == ucl_id
