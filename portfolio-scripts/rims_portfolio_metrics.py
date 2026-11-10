"""Privacy-minimised descriptive RIMS analysis across existing research domains.

Every trusted entity and relationship requires independent verification. All
results remain draft source-side measures, not causal impacts or report approval.
No names, source identifiers, author affiliations or HR records are emitted.
"""
from __future__ import annotations

from collections import defaultdict
import re

DOMAINS = ("publications", "people", "organisations",
           "projects_studies", "funding")
LINK_TYPES = frozenset((
    "output_of_study", "award_supports_study", "author_of",
    "affiliated_with", "award_supports_output",
))
EXPECTED_LINK_DOMAINS = {
    "output_of_study": ("publications", "projects_studies"),
    "award_supports_study": ("funding", "projects_studies"),
    "author_of": ("people", "publications"),
    "affiliated_with": ("people", "organisations"),
    "award_supports_output": ("funding", "publications"),
}
OA_OPEN = frozenset(("gold", "green", "bronze", "hybrid"))
OA_KNOWN = OA_OPEN | {"closed"}


class PortfolioError(ValueError):
    pass


def _identity(value, label):
    if not isinstance(value, str) or not value.strip():
        raise PortfolioError("missing " + label)
    return value


def analyse_portfolio(domains, relationships, *, period, verify_entity=None,
                      verify_relationship=None):
    """Draft source-level portfolio evidence with protected denominators.

    Callback verification is a test seam; native release must independently
    verify rights, actor, current ledger and approved source snapshot.
    """
    if not isinstance(period, str) or not re.fullmatch(
        r"\d{4}-(0[1-9]|1[0-2])", period
    ):
        raise PortfolioError("period must be YYYY-MM")
    if not isinstance(domains, dict) or not isinstance(relationships, list):
        raise PortfolioError("invalid input collections")
    if set(domains) - set(DOMAINS):
        raise PortfolioError("unsupported domain")
    if verify_entity is not None and not callable(verify_entity):
        raise PortfolioError("invalid entity verifier")
    if verify_relationship is not None and not callable(verify_relationship):
        raise PortfolioError("invalid relationship verifier")

    indexes, source_counts, trusted = {}, {}, {}
    for domain in DOMAINS:
        rows = domains.get(domain, [])
        if not isinstance(rows, list):
            raise PortfolioError("invalid domain rows")
        index = {}
        for row in rows:
            if not isinstance(row, dict):
                raise PortfolioError("non-object entity")
            identifier = _identity(row.get("entity_id"), "entity_id")
            if identifier in index:
                raise PortfolioError("duplicate ID in domain")
            index[identifier] = row
        indexes[domain] = index
        source_counts[domain] = len(index)
        trusted[domain] = {
            identifier: row for identifier, row in index.items()
            if verify_entity is not None and
            verify_entity(domain, row) is True
        }

    reviewed_links, held_links, seen_links = [], 0, set()
    for item in relationships:
        if not isinstance(item, dict) or item.get("type") not in LINK_TYPES:
            raise PortfolioError("unqualified relationship type")
        identifier = _identity(item.get("relationship_id"), "relationship_id")
        if identifier in seen_links:
            raise PortfolioError("duplicate relationship")
        seen_links.add(identifier)
        source_domain = _identity(item.get("source_domain"), "source domain")
        target_domain = _identity(item.get("target_domain"), "target domain")
        source = _identity(item.get("source_id"), "relationship source")
        target = _identity(item.get("target_id"), "relationship target")
        if source_domain not in indexes or target_domain not in indexes:
            raise PortfolioError("unknown relationship domain")
        if (source_domain, target_domain) != EXPECTED_LINK_DOMAINS[item["type"]]:
            raise PortfolioError("relationship type/domain mismatch")
        if source not in indexes[source_domain] or target not in indexes[target_domain]:
            raise PortfolioError("dangling relationship")
        if not item.get("evidence_hash"):
            raise PortfolioError("relationship evidence required")
        if (
            source in trusted[source_domain] and target in trusted[target_domain]
            and verify_relationship is not None
            and verify_relationship(item) is True
        ):
            reviewed_links.append(item)
        else:
            held_links += 1

    outputs_by_study, studies_by_award = defaultdict(set), defaultdict(set)
    outputs_by_author, authors_by_output = defaultdict(set), defaultdict(set)
    people_by_organisation, outputs_by_award = defaultdict(set), defaultdict(set)
    for edge in reviewed_links:
        if (
            edge["type"] == "output_of_study"
            and edge["source_domain"] == "publications"
            and edge["target_domain"] == "projects_studies"
        ):
            outputs_by_study[edge["target_id"]].add(edge["source_id"])
        if (
            edge["type"] == "award_supports_study"
            and edge["source_domain"] == "funding"
            and edge["target_domain"] == "projects_studies"
        ):
            studies_by_award[edge["source_id"]].add(edge["target_id"])
        if (
            edge["type"] == "author_of"
            and edge["source_domain"] == "people"
            and edge["target_domain"] == "publications"
        ):
            outputs_by_author[edge["source_id"]].add(edge["target_id"])
            authors_by_output[edge["target_id"]].add(edge["source_id"])
        if (
            edge["type"] == "affiliated_with"
            and edge["source_domain"] == "people"
            and edge["target_domain"] == "organisations"
        ):
            people_by_organisation[edge["target_id"]].add(edge["source_id"])
        if (
            edge["type"] == "award_supports_output"
            and edge["source_domain"] == "funding"
            and edge["target_domain"] == "publications"
        ):
            outputs_by_award[edge["source_id"]].add(edge["target_id"])

    completed = {
        identifier for identifier, row in trusted["projects_studies"].items()
        if row.get("status") == "Completed"
    }
    studies_with_outputs = {
        identifier for identifier in completed
        if outputs_by_study.get(identifier)
    }
    awards = {
        identifier for identifier, row in trusted["funding"].items()
        if row.get("record_type") == "Award" and
        row.get("status") == "Awarded"
    }
    oa_known = [
        row["open_access_status"] for row in trusted["publications"].values()
        if row.get("open_access_status") in OA_KNOWN
    ]

    def metric(numerator, denominator):
        return {
            "numerator": numerator,
            "denominator": denominator,
            "value": None if not denominator else numerator / denominator,
        }

    metrics = {
        "trusted_completed_studies": metric(
            len(completed), len(trusted["projects_studies"])
        ),
        "completed_studies_with_reviewed_output": metric(
            len(studies_with_outputs), len(completed)
        ),
        "awarded_funding_linked_to_study": metric(
            len(set(studies_by_award) & awards), len(awards)
        ),
        "open_access_assessed": metric(
            sum(status in OA_OPEN for status in oa_known),
            len(oa_known),
        ),
        "researchers_with_reviewed_publication_link": metric(
            len(set(outputs_by_author) & set(trusted["people"])),
            len(trusted["people"]),
        ),
        "organisations_with_reviewed_person_affiliation": metric(
            len(set(people_by_organisation) & set(trusted["organisations"])),
            len(trusted["organisations"]),
        ),
        "publications_with_two_or_more_reviewed_authors": metric(
            sum(len(authors) >= 2 for authors in authors_by_output.values()),
            len(authors_by_output),
        ),
        "awards_linked_directly_to_reviewed_output": metric(
            len(set(outputs_by_award) & awards),
            len(awards),
        ),
    }
    return {
        "schema": "careops-rims.portfolio-intelligence/1",
        "period": period,
        "period_qualification": "caller_supplied_unverified",
        "source_counts": source_counts,
        "verified_counts": {
            domain: len(records) for domain, records in trusted.items()
        },
        "reviewed_relationship_count": len(reviewed_links),
        "held_relationship_count": held_links,
        "metrics": metrics,
        "method": "descriptive_reviewed_relations_no_causal_attribution",
        "limitations": [
            "Unverified source rows excluded from outcome metrics",
            "Missing outputs may reflect incomplete coverage, not no publication",
            "No causal funding or health impact inferred",
        ],
        "native_verified": False,
        "human_release_required": True,
        "contains_person_identifiers": False,
    }
