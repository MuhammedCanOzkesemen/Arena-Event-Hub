def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_api_events_returns_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
