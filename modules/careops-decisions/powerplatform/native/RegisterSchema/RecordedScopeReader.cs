using System;
using System.Globalization;
using Microsoft.Crm.Sdk.Messages;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace CareOps.Decisions.RegisterSchema
{
    /// <summary>Recorded scope tied to the observed native root version; never clearance or reusable authority.</summary>
    public sealed class VersionedRecordedScope
    {
        internal VersionedRecordedScope(string version, RecordedScopeView view, DateTime? checkedAt, DateTime? currentUntil)
        {
            RootVersion = version; View = view; SourceCheckedAtUtc = checkedAt; SourceCurrentUntilUtc = currentUntil;
        }
        /// <summary>Version checked before and after history retrieval.</summary>
        public string RootVersion { get; }
        /// <summary>Immutable interpreted history with status and currentness kept separate.</summary>
        public RecordedScopeView View { get; }
        /// <summary>Source verification instant, absent when unavailable. Not the read time.</summary>
        public DateTime? SourceCheckedAtUtc { get; }
        /// <summary>Exclusive verification end, absent when unavailable. Not a scope extension.</summary>
        public DateTime? SourceCurrentUntilUtc { get; }
    }

    /// <summary>Native SDK adapter for a separately authenticated host. No endpoint is registered by this code.</summary>
    public static class RecordedScopeReader
    {
        /// <summary>Reserved direct bound read operation; an actual Custom API registration is still required.</summary>
        public const string ApiName = "dft_ReadRecordedScopeV1";
        private static readonly string[] RootColumns = { "dft_latestsequence", "dft_latestdecision", "dft_sourcecheckedat", "dft_sourcecurrentuntil" };

        /// <summary>
        /// Read one complete history under the supplied caller-scoped service. The host must first resolve the
        /// authenticated person and access. WhoAmI is a consistency check, not proof of human decision authority.
        /// </summary>
        public static VersionedRecordedScope Read(IPluginExecutionContext context, IOrganizationService service, Guid record)
        {
            if (context == null) throw new ArgumentNullException(nameof(context));
            if (service == null) throw new ArgumentNullException(nameof(service));
            if (record == Guid.Empty || context.MessageName != ApiName || context.Stage != 30 || context.Mode != 0 ||
                context.Depth != 1 || context.ParentContext != null || context.IsExecutingOffline || context.IsOfflinePlayback ||
                context.OrganizationId == Guid.Empty || context.InitiatingUserId == Guid.Empty || context.UserId != context.InitiatingUserId)
                throw Unavailable();
            if (context.InputParameters.Count != 1 || !context.InputParameters.TryGetValue("Target", out object supplied) ||
                !(supplied is EntityReference target) || target.LogicalName != RegisterSchemaPlan.RecordTable ||
                target.Id != record || target.KeyAttributes.Count != 0)
                throw Unavailable();
            if (!(service.Execute(new WhoAmIRequest()) is WhoAmIResponse who) ||
                who.UserId != context.InitiatingUserId || who.OrganizationId != context.OrganizationId)
                throw Unavailable();

            Frame before = Capture(service.Retrieve(RegisterSchemaPlan.RecordTable, record, new ColumnSet((string[])RootColumns.Clone())), record);
            DateTime at = DateTime.UtcNow; // Server-side read instant, never supplied by the browser/agent.
            var query = new QueryExpression(RegisterSchemaPlan.DecisionTable)
            {
                ColumnSet = new ColumnSet(RecordedScopeProjection.Columns),
                PageInfo = new PagingInfo { Count = RecordedScopeProjection.MaximumHistory + 1, PageNumber = 1 }
            };
            query.Criteria.AddCondition("dft_record", ConditionOperator.Equal, record);
            query.AddOrder("dft_sequence", OrderType.Ascending);
            EntityCollection history = service.RetrieveMultiple(query);
            if (history == null) throw Unavailable();
            // Freeze the view before a later SDK response can mutate shared response objects.
            RecordedScopeView view = RecordedScopeProjection.Project(record, before.Sequence, before.Latest,
                history, at, before.CheckedAt, before.CurrentUntil);
            Frame after = Capture(service.Retrieve(RegisterSchemaPlan.RecordTable, record, new ColumnSet((string[])RootColumns.Clone())), record);
            if (before.Version != after.Version || before.Sequence != after.Sequence ||
                !Nullable.Equals(before.Latest, after.Latest) || !Nullable.Equals(before.CheckedAt, after.CheckedAt) ||
                !Nullable.Equals(before.CurrentUntil, after.CurrentUntil))
                throw Unavailable();
            return new VersionedRecordedScope(before.Version, view, before.CheckedAt, before.CurrentUntil);
        }

        private sealed class Frame
        {
            internal Frame(string version, int sequence, Guid? latest, DateTime? checkedAt, DateTime? currentUntil)
            {
                Version = version; Sequence = sequence; Latest = latest; CheckedAt = checkedAt; CurrentUntil = currentUntil;
            }
            internal string Version { get; }
            internal int Sequence { get; }
            internal Guid? Latest { get; }
            internal DateTime? CheckedAt { get; }
            internal DateTime? CurrentUntil { get; }
        }

        private static Frame Capture(Entity row, Guid record)
        {
            if (row == null || row.LogicalName != RegisterSchemaPlan.RecordTable || row.Id != record ||
                !ulong.TryParse(row.RowVersion, NumberStyles.None, CultureInfo.InvariantCulture, out ulong version) || version == 0 ||
                row.RowVersion != version.ToString(CultureInfo.InvariantCulture) ||
                !row.Attributes.TryGetValue("dft_latestsequence", out object raw) || !(raw is int sequence) ||
                sequence < 0 || sequence > RecordedScopeProjection.MaximumHistory)
                throw Unavailable();
            Guid? latest = null;
            if (row.Attributes.TryGetValue("dft_latestdecision", out object pointer) && pointer != null)
            {
                if (!(pointer is EntityReference reference) || reference.LogicalName != RegisterSchemaPlan.DecisionTable ||
                    reference.Id == Guid.Empty || reference.KeyAttributes.Count != 0)
                    throw Unavailable();
                latest = reference.Id;
            }
            if ((sequence == 0) != !latest.HasValue) throw Unavailable();
            return new Frame(row.RowVersion, sequence, latest, OptionalInstant(row, "dft_sourcecheckedat"),
                OptionalInstant(row, "dft_sourcecurrentuntil"));
        }

        private static DateTime? OptionalInstant(Entity row, string name)
        {
            if (!row.Attributes.TryGetValue(name, out object raw) || raw == null) return null;
            if (!(raw is DateTime instant) || instant.Kind != DateTimeKind.Utc) throw Unavailable();
            return instant;
        }

        private static InvalidPluginExecutionException Unavailable() => new InvalidPluginExecutionException(
            "Recorded scope read unavailable or changed during retrieval. No decision or scope has been changed.");
    }
}
