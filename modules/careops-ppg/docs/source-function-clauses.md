# Source function clauses

`project_function_clauses` in `scripts/ppg_function_clauses.py` produces an
offline graph preview for a source that explicitly places requirement clauses
under numbered functions. It does not migrate existing requirements, authenticate
source bytes, assign native identities or write to any service.

Use a complete selected source inventory: function records, definition records
and all located definition/function occurrences. Model the source functions as
root `action-group` nodes and their subordinate clauses consistently as
`subclause` nodes. This classification requires source review of the whole
selected class. A duplicate label alone is never a reason to select this model.
Do not pass existing action records, invent function parents, choose only the
colliding rows or use this adapter for an edition-wide action list without an
actual function hierarchy.

Definitions carry a local `DefinitionKey`, the unchanged `publisherCode`, a
source tuple/locator and any original definition fields. Bindings carry that key,
`FunctionKey`, the separately printed occurrence code and source tuple/locator.
A differing occurrence label additionally requires `discrepancyRationale`; it
is retained as a source discrepancy, never used to correct the definition code.
All selected definitions and functions must have bindings. A definition used by
several functions produces separate clauses sharing the preserved definition.
The stable clause key hashes framework/edition and the definition/function pair,
not a code or title.

The returned graph retains each complete definition and binding, including
unknown properties, and deep-copies all inputs. The ordinary graph validator
runs unchanged: codes for actions remain unique across the framework; repeated
subclause labels are allowed only beneath different parent functions. Two
different definitions with the same code beneath the same function still fail.
Duplicate bindings, missing definitions/functions, source identity differences
and attempted reclassification of existing graph requirements also fail.

The helper checks structural consistency. Callers must retain reviewed source
hierarchy evidence, complete selected-inventory accounting and original bytes
privately. Source definitions may have independent rights; this repository's
fictional tests grant no rights to external texts. A valid preview does not prove
source authority, catalogue membership, native field support or clinical
applicability/sufficiency. Native admission requires its own qualified bindings
and preservation/readback evidence.

Focused verification from the module root, using the qualified absolute
repo-local interpreter:

```sh
"$REPO_PYTHON" -m unittest discover -s tests -p test_function_clauses.py -v
```
