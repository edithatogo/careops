# CHHHS credentialing current-system read-only discovery checklist

Status: implementation planning; no source-system access approved

## Purpose

Prepare a short, controlled discovery of the end-of-life credentialing platform so the existing process can be understood, reconciled and improved without changing the source system or disrupting current credentialing decisions.

## People required

- credentialing business owner;
- credentialing officer or secretariat representative;
- medical workforce representative;
- Clinical Governance representative;
- Digital Health integration or application owner;
- Records Management;
- privacy and cyber security advisers;
- one Cairns Services user;
- one Rural and Remote Services user; and
- internal-audit liaison where audit evidence may be reused without affecting independence.

## Questions to settle before access

1. Who owns and supports the current application?
2. Is there a supported API, report, scheduled export or read-only data view?
3. Which HTML screens contain information not available through a supported interface?
4. Which fields are needed for routine renewal and expiry assurance?
5. Which system and record remain authoritative for each field and decision?
6. What authentication, session, rate-limit and monitoring controls apply?
7. What information classification, privacy, retention and access rules apply?
8. Which manual spreadsheets, email queues and local registers sit around the platform?
9. How are conditions, supervision, temporary approvals, expiry and review represented?
10. How is an approved decision translated into release-to-practise and workforce controls?

## Minimum first extract

The first read-only comparison should be limited to synthetic records or an approved, minimum-necessary set of de-identified routine-renewal records. Candidate fields are:

- stable source-local record identifier;
- professional stream;
- pathway;
- application and decision status;
- facility or service code;
- model or free-text scope reference;
- application, recommendation, decision and expiry dates;
- condition or supervision indicator;
- temporary-approval indicator;
- current source record version or change timestamp; and
- source-system provenance.

Names, contact details, registration numbers, qualifications, referee material, adverse information, clinical information, free-text reasons and attachments should be excluded unless a later approved test demonstrates that a particular field is necessary.

## Adapter order

1. supported API;
2. authoritative export;
3. approved read-only view;
4. controlled HTML extraction with versioned selectors and sentinels;
5. supervised desktop automation only as a temporary bridge with an exit date.

## Silent evaluation

The source system and current human process remain authoritative. The CareOps sequence should:

1. observe the source record;
2. validate provenance and stable ID;
3. reconcile the minimum fields;
4. route differences to a human reviewer;
5. record the comparison outcome;
6. emit privacy-minimised process events; and
7. stop before any register, roster, access or release-to-practise write.

## Measures

- completeness at first submission;
- missing and contradictory fields;
- duplicate records;
- status and date mismatch;
- time and manual touches by stage;
- rework and returned applications;
- temporary approvals nearing expiry;
- decision-to-register delay;
- false alerts and missed exceptions;
- staff burden;
- practitioner experience; and
- hours released for higher-value work.

## Stop conditions

Stop the discovery or adapter run if authority, source identity, stable record identifiers, page sentinels, authentication, minimum-necessary scope, privacy classification, records location, reviewer ownership or rollback arrangements are unclear. A missing source record must create an exception and must not be treated automatically as an expiry, refusal, withdrawal or restriction.

## Evidence ceiling

Completing this checklist authorises nothing by itself. Live read access, use of practitioner information, silent evaluation, production integration and any downstream write each require their own approval and evidence.
