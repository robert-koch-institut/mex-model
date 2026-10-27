# Merging Logic

MEx aggregates metadata from many primary sources. Each Extracted item carries a `stableTargetId` that points to exactly one Merged item. When two independent primary sources describe the same real-world entity but point to different Merged items, those duplicates must be reconciled into a single canonical item.

One part of the deduplication mechanism is the `supersededBy` property. It is an optional reference — present on every Merged item and AdditiveX class — that holds a reference to the new item that supersedes this one, i.e. the canonical item a duplicate is merged into.

## Merging workflow

The workflow for "merge item B with 0-n Extracted items into item A" is:

1. Set AdditiveB.supersededBy = MergedA.identifier, using the supersededBy reference to point B at the canonical item A.
2. Re-link all items referencing B: change every reference (e.g. every stableTargetId) that pointed to B so that it points to A instead.
3. Migrate rules: move all rule values from B's rule set into A's rule set (deduplicated append).

After step 3, B retains no ExtractedItems and all rule values (except for the newly set supersededBy) have moved to A. The only non-default value left in B's rule set is AdditiveB.supersededBy. Merging B therefore yields a tombstone item whose only non-default field is supersededBy.

## Validation contract

MergedX model validation must accept an instance as valid when either condition holds:

- All required fields are present — existing behavior, unchanged.
- supersededBy is set — when supersededBy is a non-default value, no other field may be non-default; the model is only considered valid if no other field than supersededBy differs from its default.

Conversely, an instance with supersededBy unset (None) must still satisfy all required fields: if any required field is missing, it does not validate. The relaxation applies only to the tombstone branch.
This rule must be reflected in the generated JSON schemas for Merged* models, so that schema consumers (e.g. frontend applications, publishing pipelines) can statically determine the valid shapes of a merged item.
