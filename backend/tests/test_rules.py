"""Rules endpoint tests."""
import pytest


class TestRules:
    def test_create_rule(self, client, analyst_headers):
        res = client.post("/api/v1/rules", headers=analyst_headers, json={
            "name": "Test Rule", "conditions": {"field": "severity", "op": "equals", "value": "high"}, "actions": [{"type": "notify"}]
        })
        assert res.status_code == 200
        assert "id" in res.json()

    def test_list_rules(self, client, analyst_headers):
        client.post("/api/v1/rules", headers=analyst_headers, json={"name": "R1", "conditions": {}, "actions": []})
        res = client.get("/api/v1/rules", headers=analyst_headers)
        assert res.status_code == 200
        assert len(res.json()["rules"]) >= 1

    def test_update_rule(self, client, analyst_headers):
        create = client.post("/api/v1/rules", headers=analyst_headers, json={"name": "Old", "conditions": {}, "actions": []})
        rule_id = create.json()["id"]
        res = client.put(f"/api/v1/rules/{rule_id}", headers=analyst_headers, json={"name": "New", "conditions": {}, "actions": []})
        assert res.status_code == 200

    def test_delete_rule(self, client, analyst_headers):
        create = client.post("/api/v1/rules", headers=analyst_headers, json={"name": "Del", "conditions": {}, "actions": []})
        rule_id = create.json()["id"]
        res = client.delete(f"/api/v1/rules/{rule_id}", headers=analyst_headers)
        assert res.status_code == 200

    def test_viewer_cannot_create(self, client, viewer_headers):
        res = client.post("/api/v1/rules", headers=viewer_headers, json={"name": "X", "conditions": {}, "actions": []})
        assert res.status_code == 403

    def test_viewer_can_list(self, client, viewer_headers):
        res = client.get("/api/v1/rules", headers=viewer_headers)
        assert res.status_code == 200
