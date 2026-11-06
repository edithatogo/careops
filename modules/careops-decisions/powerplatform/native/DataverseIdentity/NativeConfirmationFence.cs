using System;
using CareOps.Decisions.RegisterSchema;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Messages;

namespace CareOps.Decisions.DataverseIdentity
{
    /// <summary>Conditional native source update within the recording transaction, not an approval or session lock.</summary>
    public static class NativeConfirmationFence
    {
        private const string Failure = "Original confirmation changed or could not be protected for recording. Abort this transaction; do not repeat the decision.";

        /// <summary>
        /// Acquire the original source under the SAME verified caller service and ambient transaction.
        /// Updates only a technical token with exact row-version matching, then checks the still-current original contents.
        /// The caller must keep subsequent source/authority checks and journal writes in this same native transaction.
        /// Never use this method for a historical receipt read, automatic retry or independent web-service request.
        /// </summary>
        public static NativeConfirmation Acquire(IPluginExecutionContext context, CallerBinding binding, Guid recordId, Guid sourceId)
        {
            if (context == null) throw new ArgumentNullException(nameof(context));
            if (binding == null) throw new ArgumentNullException(nameof(binding));
            if (recordId == Guid.Empty || sourceId == Guid.Empty) throw new ArgumentException("Canonical record and original source identities are required.");
            try
            {
                if (context.MessageName != RegisterJournalAppender.ApiName || context.Stage != 30 || context.Mode != 0 ||
                    !context.IsInTransaction || context.Depth != 1 || context.ParentContext != null || context.IsExecutingOffline || context.IsOfflinePlayback ||
                    context.OrganizationId != binding.Caller.Organization || context.UserId != binding.Caller.PlatformUser ||
                    context.InitiatingUserId != binding.Caller.PlatformUser) throw Rejected();
                ParameterCollection parameters = context.InputParameters;
                if (parameters == null || !parameters.TryGetValue("Target", out object raw) || !(raw is EntityReference target) ||
                    target.LogicalName != RegisterSchemaPlan.RecordTable || target.Id != recordId || target.KeyAttributes.Count != 0) throw Rejected();

                NativeConfirmation before = NativeConfirmationSource.Read(binding, recordId, sourceId);
                // A new transport marker, not a secret, authorisation token, lease or replacement confirmation.
                string token = Guid.NewGuid().ToString("N");
                var patch = new Entity(ConfirmationSourceSchema.Table, sourceId) { RowVersion = before.RowVersion };
                patch["dft_fencetoken"] = token;
                var update = new UpdateRequest { Target = patch, ConcurrencyBehavior = ConcurrencyBehavior.IfRowVersionMatches };
                if (!(binding.Service.Execute(update) is UpdateResponse)) throw Rejected();
                // Re-read also detects synchronous extensions changing source content as part of the token update.
                NativeConfirmation after = NativeConfirmationSource.Read(binding, recordId, sourceId);
                if (after.RowVersion == before.RowVersion || after.FenceToken != token || !SameOriginal(before, after)) throw Rejected();
                return after;
            }
            catch (Exception)
            {
                // Escape the ambient transaction so native rollback occurs. Never retry, compensate or reapprove here.
                throw Rejected();
            }
        }

        private static bool SameOriginal(NativeConfirmation before, NativeConfirmation after) =>
            before.Confirmation.Digest == after.Confirmation.Digest &&
            before.PolicyReference == after.PolicyReference &&
            before.Confirmation.Pathway == after.Confirmation.Pathway &&
            before.Confirmation.ConfirmedAt == after.Confirmation.ConfirmedAt &&
            before.Confirmation.CurrentUntil == after.Confirmation.CurrentUntil;
        // The source reader already binds record, source, organisation, actor, evidence and explicit outcome/function.
        // The complete digest binds all original decision fields and both owners; these comparisons cover source-only values.
        private static InvalidPluginExecutionException Rejected() => new InvalidPluginExecutionException(Failure);
    }
}
