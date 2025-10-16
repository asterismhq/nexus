import pytest
from nexus_sdk.nexus_client import (
    CallbackResponseStrategy,
    PatternMatchingStrategy,
    SequenceResponseStrategy,
    SimpleResponseStrategy,
)


def test_simple_strategy_returns_constant_content():
    strategy = SimpleResponseStrategy(content={"answer": 42})
    response = strategy.generate({"input": "ignored"})

    assert response.content == {"answer": 42}
    assert response.tool_calls == []


def test_callback_strategy_applies_predicate_and_tool_callback():
    def callback(payload: dict[str, object]) -> str:
        return str(payload["input"]).upper()

    def tool_callback(_: dict[str, object]) -> list[dict[str, object]]:
        return [{"name": "logger", "args": {"level": "debug"}}]

    strategy = CallbackResponseStrategy(
        callback=callback,
        tool_callback=tool_callback,
        predicate=lambda payload: payload.get("allow", False),
    )

    applicable = {"input": "content", "allow": True}
    skipped = {"input": "content", "allow": False}

    assert strategy.should_handle(applicable) is True
    assert strategy.should_handle(skipped) is False

    response = strategy.generate(applicable)
    assert response.content == "CONTENT"
    assert response.tool_calls == [{"name": "logger", "args": {"level": "debug"}}]


def test_pattern_matching_strategy_uses_regex_map():
    strategy = PatternMatchingStrategy(
        {
            r"summarize": {"content": "summary", "tool_calls": []},
            r"search": "search result",
        },
        default={"content": "fallback"},
    )

    summary_payload = {"input": [{"role": "user", "content": "Please summarize"}]}
    search_payload = {"input": [{"role": "user", "content": "try search"}]}
    fallback_payload = {"input": [{"role": "user", "content": "nothing"}]}

    assert strategy.generate(summary_payload).content == "summary"
    assert strategy.generate(search_payload).content == "search result"
    assert strategy.generate(fallback_payload).content == "fallback"


def test_sequence_strategy_walks_responses_and_repeats_last_when_configured():
    strategy = SequenceResponseStrategy(
        [
            {"content": "first"},
            {"content": "second", "tool_calls": [{"name": "a", "args": {}}]},
        ],
        repeat_last=True,
    )

    first = strategy.generate({"input": []})
    second = strategy.generate({"input": []})
    third = strategy.generate({"input": []})

    assert first.content == "first"
    assert first.tool_calls == []
    assert second.content == "second"
    assert second.tool_calls == [{"name": "a", "args": {}}]
    assert third.content == "second"
    assert third.tool_calls == [{"name": "a", "args": {}}]


def test_sequence_strategy_raises_when_exhausted_without_repeat():
    strategy = SequenceResponseStrategy(["only"], repeat_last=False)
    strategy.generate({"input": []})
    with pytest.raises(RuntimeError):
        strategy.generate({"input": []})
