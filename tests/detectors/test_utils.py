from dlt_init_openapi.detector.default import utils


def test_word_variations() -> None:
    assert set(utils.get_word_variations("dog")) == set(["dogs", "dog"])
    assert set(utils.get_word_variations("cats")) == set(["cat", "cats"])


def test_singularized_path_parts() -> None:
    assert utils.singularized_path_parts("hello/cats") == ["hello", "cat"]
    assert utils.singularized_path_parts("hello/{cats}/cats") == ["hello", "{cats}", "cat"]
