"""Unit tests for RuleBasedPlanner."""

from __future__ import annotations

import pytest

from nikola.domain.entities.planning_request import PlanningRequest, PlanningResult
from nikola.domain.ports.planner_port import PlannerPort
from nikola.domain.value_objects.enums import StepType
from nikola.infrastructure.planners.rule_based_planner import RuleBasedPlanner


def _plan(goal: str, constraints: list[str] | None = None) -> PlanningResult:
    planner = RuleBasedPlanner()
    req = PlanningRequest.create(goal, constraints=constraints)
    return planner.plan(req)


@pytest.mark.unit
class TestRuleBasedPlannerIsAPort:
    def test_is_a_planner_port(self) -> None:
        assert isinstance(RuleBasedPlanner(), PlannerPort)

    def test_planner_name_is_rule_based(self) -> None:
        assert RuleBasedPlanner().planner_name == "rule_based"


@pytest.mark.unit
class TestRuleBasedPlannerKeywords:
    def test_python_keyword_produces_venv_and_deps_steps(self) -> None:
        result = _plan("set up a python project")
        titles = [s.title for s in result.plan.steps]
        assert any("virtual environment" in t.lower() for t in titles)
        assert any("dependencies" in t.lower() for t in titles)

    def test_flask_keyword_produces_flask_steps(self) -> None:
        result = _plan("build a flask app")
        titles = [s.title for s in result.plan.steps]
        assert any("flask" in t.lower() for t in titles)

    def test_git_keyword_produces_git_steps(self) -> None:
        result = _plan("init a git repository")
        titles = [s.title for s in result.plan.steps]
        assert any("git" in t.lower() for t in titles)
        assert any("gitignore" in t.lower() for t in titles)

    def test_test_keyword_produces_test_setup_step(self) -> None:
        result = _plan("add test coverage")
        titles = [s.title for s in result.plan.steps]
        assert any("test" in t.lower() for t in titles)

    def test_pytest_keyword_deduplicates_with_test(self) -> None:
        result = _plan("run pytest tests")
        titles = [s.title for s in result.plan.steps]
        test_steps = [t for t in titles if "test suite" in t.lower()]
        assert len(test_steps) == 1

    def test_docker_keyword_produces_dockerfile_step(self) -> None:
        result = _plan("dockerize the app")
        titles = [s.title for s in result.plan.steps]
        assert any("dockerfile" in t.lower() for t in titles)

    def test_deploy_keyword_produces_deployment_steps(self) -> None:
        result = _plan("deploy the application")
        titles = [s.title for s in result.plan.steps]
        assert any("deploy" in t.lower() for t in titles)

    def test_api_keyword_produces_api_steps(self) -> None:
        result = _plan("build a REST api")
        titles = [s.title for s in result.plan.steps]
        assert any("api" in t.lower() for t in titles)

    def test_multiple_keywords_merge_steps(self) -> None:
        result = _plan("create a python flask api with git and tests")
        assert result.plan.step_count > 3

    def test_multiple_keywords_deduplicate_by_title(self) -> None:
        result = _plan("run pytest and test the python code")
        titles = [s.title for s in result.plan.steps]
        assert len(titles) == len(set(titles))


@pytest.mark.unit
class TestRuleBasedPlannerNoMatch:
    def test_no_keyword_gives_generic_step(self) -> None:
        result = _plan("do something completely unrecognised xyz123")
        assert result.plan.step_count == 1
        assert result.plan.steps[0].step_type is StepType.REASONING

    def test_no_keyword_gives_low_confidence(self) -> None:
        result = _plan("do something completely unrecognised xyz123")
        assert result.confidence == 0.5

    def test_no_keyword_gives_a_warning(self) -> None:
        result = _plan("do something completely unrecognised xyz123")
        assert len(result.warnings) > 0


@pytest.mark.unit
class TestRuleBasedPlannerConfidence:
    def test_keyword_match_gives_full_confidence(self) -> None:
        result = _plan("set up python")
        assert result.confidence == 1.0


@pytest.mark.unit
class TestRuleBasedPlannerConstraintWarning:
    def test_constraints_produce_warning(self) -> None:
        result = _plan("set up python", constraints=["no pip"])
        assert any("constraint" in w.lower() for w in result.warnings)


@pytest.mark.unit
class TestRuleBasedPlannerDeterminism:
    def test_same_goal_produces_same_plan(self) -> None:
        goal = "create a python flask git project"
        r1 = _plan(goal)
        r2 = _plan(goal)
        titles1 = [s.title for s in r1.plan.steps]
        titles2 = [s.title for s in r2.plan.steps]
        assert titles1 == titles2


@pytest.mark.unit
class TestRuleBasedPlannerStepOrdering:
    def test_steps_are_ordered_sequentially(self) -> None:
        result = _plan("set up python flask git")
        orders = [s.order for s in result.plan.steps]
        assert orders == list(range(1, len(orders) + 1))

    def test_reasoning_summary_mentions_matched_keywords(self) -> None:
        result = _plan("set up python")
        assert "python" in result.reasoning_summary.lower()
