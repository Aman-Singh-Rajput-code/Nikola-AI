"""Unit tests for `nikola.domain.value_objects.intent`."""

from __future__ import annotations

import pytest

from nikola.domain.value_objects.intent import Intent, IntentType


@pytest.mark.unit
class TestIntentType:
    def test_has_expected_members(self) -> None:
        assert {m.value for m in IntentType} == {
            "chat",
            "tool_invocation",
            "clarification_needed",
            "out_of_scope",
        }

    def test_is_a_str_subclass(self) -> None:
        assert isinstance(IntentType.CHAT, str)


@pytest.mark.unit
class TestIntentConstruction:
    def test_defaults_to_full_confidence(self) -> None:
        intent = Intent(intent_type=IntentType.CHAT)
        assert intent.confidence == 1.0

    def test_defaults_to_no_reasoning(self) -> None:
        intent = Intent(intent_type=IntentType.CHAT)
        assert intent.reasoning is None

    def test_accepts_explicit_confidence_and_reasoning(self) -> None:
        intent = Intent(
            intent_type=IntentType.TOOL_INVOCATION,
            confidence=0.85,
            reasoning="User asked to run a command.",
        )
        assert intent.intent_type is IntentType.TOOL_INVOCATION
        assert intent.confidence == 0.85
        assert intent.reasoning == "User asked to run a command."


@pytest.mark.unit
class TestIntentValidation:
    def test_confidence_below_zero_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            Intent(intent_type=IntentType.CHAT, confidence=-0.1)

    def test_confidence_above_one_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            Intent(intent_type=IntentType.CHAT, confidence=1.001)

    def test_confidence_exactly_zero_is_accepted(self) -> None:
        intent = Intent(intent_type=IntentType.CLARIFICATION_NEEDED, confidence=0.0)
        assert intent.confidence == 0.0

    def test_confidence_exactly_one_is_accepted(self) -> None:
        intent = Intent(intent_type=IntentType.CHAT, confidence=1.0)
        assert intent.confidence == 1.0


@pytest.mark.unit
class TestIntentImmutability:
    def test_intent_type_cannot_be_reassigned(self) -> None:
        intent = Intent(intent_type=IntentType.CHAT)
        with pytest.raises(AttributeError):
            intent.intent_type = IntentType.TOOL_INVOCATION  # type: ignore[misc]


@pytest.mark.unit
class TestIntentEquality:
    def test_identical_intents_are_equal(self) -> None:
        a = Intent(intent_type=IntentType.CHAT, confidence=0.9)
        b = Intent(intent_type=IntentType.CHAT, confidence=0.9)
        assert a == b

    def test_different_intent_types_are_not_equal(self) -> None:
        a = Intent(intent_type=IntentType.CHAT)
        b = Intent(intent_type=IntentType.TOOL_INVOCATION)
        assert a != b
