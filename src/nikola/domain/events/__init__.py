"""Domain events: immutable facts about notable occurrences in the domain.

A domain event records that something happened — to an entity, at a
specific time — distinct from an entity itself (which has identity and
may have mutable state) and distinct from an exception (which signals a
failure, not an occurrence worth recording).

Sprint 4 defines the event *shapes* only: `TaskStarted` and
`TaskCompleted`. No publishing/dispatch mechanism exists yet — that is an
infrastructure concern (the `EventBusPort` adapter) introduced in a later
sprint. These classes are pure data, safe to construct and pass around
without any infrastructure dependency.
"""

from nikola.domain.events.task_events import TaskCompleted, TaskStarted

__all__ = ["TaskStarted", "TaskCompleted"]
