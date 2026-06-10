"""Progression pedagogy: given a mission and an attempt outcome, decide what
happens next — feedback, escalating hints, remediation, flow.

Pure logic, no I/O: this is the seam for unit-testing and A/B-testing hint
and remediation strategies without touching the HTTP layer. Flow on success
comes from the mission's engine-canonicalized next_mission_rules
(see generator._canonicalize_flow).
"""
from ..schemas import Mission, Remediation, SubmissionResult

# Failures on the same mission before remediation (a simpler explanation and a
# smaller subtask) is offered alongside the hint. Keep struggle productive but
# within reach — see research/learning/ (desirable difficulties).
REMEDIATION_THRESHOLD = 3


def evaluate_submission(mission: Mission, passed: bool, attempts: int) -> SubmissionResult:
    if passed:
        return SubmissionResult(
            recorded=True,
            passed=True,
            attempts=attempts,
            next_action=mission.next_mission_rules.on_success,
            hint_level=0,
            hint=None,
            technical_feedback=mission.success_feedback.technical_feedback,
            story_feedback=mission.success_feedback.story_feedback,
            remediation=None,
        )

    hint_level = min(attempts, len(mission.hints))
    needs_remediation = attempts >= REMEDIATION_THRESHOLD
    return SubmissionResult(
        recorded=True,
        passed=False,
        attempts=attempts,
        next_action="remediate" if needs_remediation else "retry",
        hint_level=hint_level,
        hint=mission.hints[hint_level - 1],
        technical_feedback=mission.failure_feedback.technical_feedback,
        story_feedback=mission.failure_feedback.story_feedback,
        remediation=Remediation(**mission.remediation.model_dump()) if needs_remediation else None,
    )
