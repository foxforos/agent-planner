
import planner as planner_module


def test_init_sets_memory_path_calls_load_memory_and_sets_memory(monkeypatch):

    calls={"count":0}

    def fake_load(self):
        calls["count"] += 1
        return ["MEMORY_FROM_FAKE"]
    
    monkeypatch.setattr(planner_module.Planner, "load_memory", fake_load)

    p=planner_module.Planner(memory_path="X.json")

    assert p.memory_path == "X.json"
    assert p.memory ==["MEMORY_FROM_FAKE"]
    assert calls["count"] == 1
    

    