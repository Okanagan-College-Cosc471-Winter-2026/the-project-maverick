from pathlib import Path

from app.modules.inference import model_loader


class DummyBundle:
    model_type = "dummy"
    feature_names: list[str] = []
    metadata: dict = {}
    model_path = Path("/tmp/dummy")


def test_get_model_bundle_is_lazy_and_cached(monkeypatch) -> None:
    calls: list[Path] = []

    def fake_create_model_bundle(path: Path) -> DummyBundle:
        calls.append(path)
        return DummyBundle()

    model_loader.get_model_bundle.cache_clear()
    monkeypatch.setattr(model_loader, "create_model_bundle", fake_create_model_bundle)

    try:
        assert calls == []

        first_bundle = model_loader.get_model_bundle()
        second_bundle = model_loader.get_model_bundle()

        assert isinstance(first_bundle, DummyBundle)
        assert first_bundle is second_bundle
        assert len(calls) == 1
    finally:
        model_loader.get_model_bundle.cache_clear()
