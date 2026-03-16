import agent


class DummyPlanner:
    doctor_report_called = 0
    doctor_fix_called = 0

    def __init__(self):
        pass

    @classmethod
    def reset(cls):
        cls.doctor_report_called = 0
        cls.doctor_fix_called = 0

    def doctor_report(self):
        DummyPlanner.doctor_report_called += 1
        return {
            "missing_files": [],
            "orphan_files": [],
            "invalid_records": [],
            "duplicate_names": [],
            "duplicate_filenames": [],
        }

    def doctor_fix(self):
        DummyPlanner.doctor_fix_called += 1
        return {
            "removed_records": [],
            "moved_files": [],
            "backup_path": None,
        }


def patch_agent_dependencies(monkeypatch):
    DummyPlanner.reset()
    monkeypatch.setattr(agent, "Planner", DummyPlanner)
    monkeypatch.setattr(agent, "setup_logging", lambda: "fake_log.log")


def test_main_prints_usage_if_no_command(monkeypatch, capsys):
    patch_agent_dependencies(monkeypatch)
    monkeypatch.setattr(agent.sys, "argv", ["agent.py"])

    agent.main()

    captured = capsys.readouterr()
    assert 'Uso: python agent.py "comando"' in captured.out
    assert DummyPlanner.doctor_report_called == 0
    assert DummyPlanner.doctor_fix_called == 0


def test_main_prints_unknown_command_if_command_is_not_recognized(monkeypatch, capsys):
    patch_agent_dependencies(monkeypatch)
    monkeypatch.setattr(agent.sys, "argv", ["agent.py", "comando_sconosciuto"])

    agent.main()

    captured = capsys.readouterr()
    assert "Comando non riconosciuto" in captured.out
    assert DummyPlanner.doctor_report_called == 0
    assert DummyPlanner.doctor_fix_called == 0


def test_main_doctor_calls_planner_doctor_report_and_prints_report(monkeypatch, capsys):
    patch_agent_dependencies(monkeypatch)
    monkeypatch.setattr(agent.sys, "argv", ["agent.py", "doctor"])

    agent.main()

    captured = capsys.readouterr()
    assert DummyPlanner.doctor_report_called == 1
    assert "DOCTOR REPORT" in captured.out
    assert "Stato: HEALTHY ✅ (0 problemi)" in captured.out
    assert DummyPlanner.doctor_fix_called == 0


def test_main_doctor_fix_calls_planner_doctor_fix(monkeypatch, capsys):
    patch_agent_dependencies(monkeypatch)
    monkeypatch.setattr(agent.sys, "argv", ["agent.py", "doctor_fix"])

    agent.main()

    capsys.readouterr()
    assert DummyPlanner.doctor_fix_called == 1
    assert DummyPlanner.doctor_report_called == 0


def test_main_carica_progetto_without_colon_prints_error(monkeypatch, capsys):
    patch_agent_dependencies(monkeypatch)
    monkeypatch.setattr(agent.sys, "argv", ["agent.py", "carica progetto"])

    agent.main()

    captured = capsys.readouterr()
    assert "❌ Devi specificare un nome. Esempio:" in captured.out
    assert 'python agent.py "carica progetto: nome"' in captured.out
    assert DummyPlanner.doctor_report_called == 0
    assert DummyPlanner.doctor_fix_called == 0