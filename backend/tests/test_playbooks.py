"""Playbooks endpoint tests."""
import pytest


class TestPlaybooks:
    def test_create_playbook(self, client, analyst_headers):
        res = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Test PB", "steps": [{"type": "manual", "label": "Step 1"}]
        })
        assert res.status_code == 200
        assert "id" in res.json()

    def test_list_playbooks(self, client, analyst_headers):
        client.post("/api/v1/playbooks", headers=analyst_headers, json={"name": "PB1", "steps": []})
        res = client.get("/api/v1/playbooks", headers=analyst_headers)
        assert res.status_code == 200
        assert len(res.json()["playbooks"]) >= 1

    def test_update_playbook(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={"name": "Old", "steps": []})
        pb_id = create.json()["id"]
        res = client.put(f"/api/v1/playbooks/{pb_id}", headers=analyst_headers, json={"name": "New", "steps": []})
        assert res.status_code == 200

    def test_delete_playbook(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={"name": "Del", "steps": []})
        pb_id = create.json()["id"]
        res = client.delete(f"/api/v1/playbooks/{pb_id}", headers=analyst_headers)
        assert res.status_code == 200

    def test_execute_playbook(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={"name": "Exec", "steps": [{"type": "manual", "label": "S1"}]})
        pb_id = create.json()["id"]
        res = client.post(f"/api/v1/playbooks/{pb_id}/execute", headers=analyst_headers)
        assert res.status_code == 200
        assert "execution_id" in res.json()

    def test_viewer_cannot_create(self, client, viewer_headers):
        res = client.post("/api/v1/playbooks", headers=viewer_headers, json={"name": "X", "steps": []})
        assert res.status_code == 403

    def test_viewer_can_list(self, client, viewer_headers):
        res = client.get("/api/v1/playbooks", headers=viewer_headers)
        assert res.status_code == 200
