# SPDX-License-Identifier: Apache-2.0
"""Pure deterministic portfolio blueprints; no cloud I/O or governance authority.

The existing H2 resolver remains responsible for pinned profile/occurrence
selection and meeting preparation. This is not a competing record store.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

_KEYS = frozenset({"forum_ref", "profile_revision", "display_name", "register_ref", "template_ref",
                   "agenda_sections", "control_keys", "capabilities"})
_CAPS = frozenset({"prepare", "compare_calendar"})
_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")


def _valid_ref(value: object) -> bool:
    return isinstance(value, str) and _REF.fullmatch(value) is not None


def _valid_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 200 and not any(ord(c) < 32 for c in value)


def _valid_unique(values: object, *, references: bool = False) -> bool:
    return (isinstance(values, list) and 0 < len(values) <= 64
            and all((_valid_ref(x) if references else _valid_text(x)) for x in values)
            and len(set(values)) == len(values))


def compile_meeting_portfolio(forum_profiles: object) -> dict:
    """Produce a stable review-only plan for independently configured meetings.

    Profiles may share templates and a Decisions register. Each forum has its
    own namespace; actual authority, persistence and access remain with a
    separately selected local or Decisions provider and native installation.
    """
    blocked = {"state": "blocked", "reason": "INVALID_FORUM_BLUEPRINT", "native_write_authorised": False}
    if not isinstance(forum_profiles, list) or not 1 <= len(forum_profiles) <= 64:
        return blocked
    output = []
    seen = set()
    for profile in forum_profiles:
        if not isinstance(profile, dict) or set(profile) != _KEYS:
            return blocked
        if (not all(_valid_ref(profile[k]) for k in ("forum_ref", "profile_revision", "register_ref", "template_ref"))
                or not _valid_text(profile["display_name"])
                or not _valid_unique(profile["agenda_sections"])
                or not _valid_unique(profile["control_keys"], references=True)
                or not _valid_unique(profile["capabilities"], references=True)
                or not set(profile["capabilities"]) <= _CAPS):
            return blocked
        if profile["forum_ref"] in seen:
            return blocked
        seen.add(profile["forum_ref"])
        cap = set(profile["capabilities"])
        output.append({
            "forum_ref": profile["forum_ref"],
            "profile_revision": profile["profile_revision"],
            "display_name": profile["display_name"],
            "namespace": "forum:" + profile["forum_ref"] + ":",
            "register_ref": profile["register_ref"],
            "template_ref": profile["template_ref"],
            "agenda_sections": list(profile["agenda_sections"]),
            "control_keys": list(profile["control_keys"]),
            "automations": (["preflight", "carry_forward_review"] if "prepare" in cap else [])
                           + (["calendar_compare"] if "compare_calendar" in cap else []),
            "create_actions": False,
            "issue_minutes": False,
            "provider": "local_or_decisions_explicit",
        })
    output.sort(key=lambda x: x["forum_ref"])
    canonical = json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return {
        "state": "review_only", "schema_version": 1,
        "sha256": sha256(canonical.encode("utf-8")).hexdigest(),
        "forums": output, "native_write_authorised": False,
        "premium_required": False, "copilot_required": False,
        "core_connectors": ["sharepoint", "office365_outlook", "planner_basic_optional"],
    }
