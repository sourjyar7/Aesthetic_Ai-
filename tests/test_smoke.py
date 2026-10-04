import ai
import catalog
import evaluation


def test_packages_import() -> None:
    assert [m.__name__ for m in (ai, catalog, evaluation)] == ["ai", "catalog", "evaluation"]
