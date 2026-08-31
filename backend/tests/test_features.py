"""Audit, rules explain, and playbook execution tests."""
import pytest


class TestAuditLogs:
    def test_admin_can_list_audit_logs(self, client, admin_headers):
        res = client.get("/api/v1/audit/logs", headers=admin_headers)
        assert res.status_code == 200
        data = res.json()
        assert "logs" in data
        assert "total" in data

    def test_analyst_can_list_all_audit_logs(self, client, analyst_headers):
        res = client.get("/api/v1/audit/logs", headers=analyst_headers)
        assert res.status_code == 200

    def test_user_can_list_own_audit_logs(self, client, analyst_headers):
        res = client.get("/api/v1/audit/logs/me", headers=analyst_headers)
        assert res.status_code == 200
        assert "logs" in res.json()

    def test_audit_logs_filter_by_action(self, client, admin_headers):
        res = client.get("/api/v1/audit/logs?action=user.login", headers=admin_headers)
        assert res.status_code == 200


class TestRulesExplain:
    def test_evaluate_rules_against_alert(self, client, analyst_headers):
        res = client.post("/api/v1/rules/evaluate", headers=analyst_headers, json={
            "alert": {"severity": "high", "attack_type": "ddos", "src_ip": "1.2.3.4", "dest_port": 80}
        })
        assert res.status_code == 200
        data = res.json()
        assert "trace" in data
        assert "rules_evaluated" in data

    def test_evaluate_requires_alert(self, client, analyst_headers):
        res = client.post("/api/v1/rules/evaluate", headers=analyst_headers, json={})
        assert res.status_code == 400

    def test_explain_rules_for_alert(self, client, analyst_headers):
        res = client.get("/api/v1/rules/alerts/nonexistent/explain-rules", headers=analyst_headers)
        assert res.status_code == 404


class TestPlaybookExecution:
    def test_execute_playbook_without_alert(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Exec NoAlert", "steps": [{"type": "manual", "label": "S1"}]
        })
        pb_id = create.json()["id"]
        res = client.post(f"/api/v1/playbooks/{pb_id}/execute", headers=analyst_headers)
        assert res.status_code == 200
        assert "execution_id" in res.json()

    def test_execute_playbook_with_alert(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Exec Alert", "steps": [{"type": "manual", "label": "S1"}]
        })
        pb_id = create.json()["id"]
        res = client.post(f"/api/v1/playbooks/{pb_id}/execute?alert_id=ALT-123", headers=analyst_headers)
        assert res.status_code == 200

    def test_get_execution_status(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Exec Status", "steps": [{"type": "manual", "label": "S1"}]
        })
        pb_id = create.json()["id"]
        exec_res = client.post(f"/api/v1/playbooks/{pb_id}/execute", headers=analyst_headers)
        execution_id = exec_res.json()["execution_id"]
        res = client.get(f"/api/v1/playbooks/executions/{execution_id}", headers=analyst_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "in_progress"
        assert data["current_step"] == 0

    def test_complete_step(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Exec Step", "steps": [{"type": "manual", "label": "S1"}, {"type": "manual", "label": "S2"}]
        })
        pb_id = create.json()["id"]
        exec_res = client.post(f"/api/v1/playbooks/{pb_id}/execute", headers=analyst_headers)
        execution_id = exec_res.json()["execution_id"]
        res = client.post(f"/api/v1/playbooks/executions/{execution_id}/steps/0", headers=analyst_headers, json={"notes": "done"})
        assert res.status_code == 200
        assert res.json()["status"] == "in_progress"
        status = client.get(f"/api/v1/playbooks/executions/{execution_id}", headers=analyst_headers).json()
        assert 0 in status["completed_steps"]
        assert status["current_step"] == 1

    def test_complete_all_steps_finishes(self, client, analyst_headers):
        create = client.post("/api/v1/playbooks", headers=analyst_headers, json={
            "name": "Exec Finish", "steps": [{"type": "manual", "label": "S1"}]
        })
        pb_id = create.json()["id"]
        exec_res = client.post(f"/api/v1/playbooks/{pb_id}/execute", headers=analyst_headers)
        execution_id = exec_res.json()["execution_id"]
        client.post(f"/api/v1/playbooks/executions/{execution_id}/steps/0", headers=analyst_headers, json={})
        status = client.get(f"/api/v1/playbooks/executions/{execution_id}", headers=analyst_headers).json()
        assert status["status"] == "completed"
