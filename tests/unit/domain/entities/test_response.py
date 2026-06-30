"""Unit tests for `nikola.domain.entities.response.Response`."""

from __future__ import annotations

from datetime import datetime

import pytest

from nikola.domain.entities.response import Response
from nikola.domain.value_objects.command_id import CommandId
from nikola.domain.value_objects.enums import ResponseType


@pytest.mark.unit
class TestResponseText:
    def test_text_sets_response_type_to_text(self) -> None:
        response = Response.text(command_id=CommandId.generate(), content="hi there")
        assert response.response_type == ResponseType.TEXT

    def test_text_sets_the_given_content(self) -> None:
        response = Response.text(command_id=CommandId.generate(), content="hi there")
        assert response.content == "hi there"

    def test_text_sets_a_created_at_timestamp(self) -> None:
        response = Response.text(command_id=CommandId.generate(), content="hi there")
        assert isinstance(response.created_at, datetime)

    def test_text_is_not_an_error(self) -> None:
        response = Response.text(command_id=CommandId.generate(), content="hi there")
        assert response.is_error is False


@pytest.mark.unit
class TestResponseError:
    def test_error_sets_response_type_to_error(self) -> None:
        response = Response.error(command_id=CommandId.generate(), content="it broke")
        assert response.response_type == ResponseType.ERROR

    def test_error_sets_the_given_content(self) -> None:
        response = Response.error(command_id=CommandId.generate(), content="it broke")
        assert response.content == "it broke"

    def test_error_is_an_error(self) -> None:
        response = Response.error(command_id=CommandId.generate(), content="it broke")
        assert response.is_error is True


@pytest.mark.unit
class TestResponseCommandAssociation:
    def test_response_references_the_given_command_id(self) -> None:
        command_id = CommandId.generate()
        response = Response.text(command_id=command_id, content="hi")
        assert response.command_id == command_id


@pytest.mark.unit
class TestResponseImmutability:
    def test_content_cannot_be_reassigned(self) -> None:
        response = Response.text(command_id=CommandId.generate(), content="hi")
        with pytest.raises(AttributeError):
            response.content = "mutated"  # type: ignore[misc]
