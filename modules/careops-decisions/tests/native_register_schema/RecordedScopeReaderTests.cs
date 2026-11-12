using System;
using System.Collections.Generic;
using System.Linq;
using CareOps.Decisions.RegisterSchema;
using Microsoft.Crm.Sdk.Messages;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;
using Xunit;

namespace CareOps.Decisions.RegisterSchemaTests
{
    public sealed class RecordedScopeReaderTests
    {
        private sealed class Store : IOrganizationService
        {
            internal static readonly Guid Org = Guid.Parse("80000000-0000-0000-0000-000000000008");
            internal static readonly Guid User = Guid.Parse("90000000-0000-0000-0000-000000000009");
            internal readonly DateTime Now = DateTime.UtcNow;
            internal readonly RemoteExecutionContext Context = new RemoteExecutionContext
            {
                OrganizationId = Org, UserId = User, InitiatingUserId = User,
                MessageName = RecordedScopeReader.ApiName, Stage = 30, Mode = 0, Depth = 1
            };
            internal readonly List<string> Calls = new List<string>();
            internal readonly List<ColumnSet> RootReads = new List<ColumnSet>();
            internal Entity Root, FinalRoot;
            internal EntityCollection History;
            internal OrganizationResponse Identity = new WhoAmIResponse();
            internal QueryExpression? Query;
            internal string? FailAt;
            internal readonly TimeoutException Failure = new TimeoutException("synthetic read failure");
            internal Action? OnFinalRead;
            internal Store(int count = 1)
            {
                Context.InputParameters["Target"] = new EntityReference(RegisterSchemaPlan.RecordTable, DecisionAppendTests.Record);
                Root = new Entity(RegisterSchemaPlan.RecordTable, DecisionAppendTests.Record) { RowVersion = "42" };
                Root["dft_latestsequence"] = count;
                if (count > 0) Root["dft_latestdecision"] = new EntityReference(RegisterSchemaPlan.DecisionTable, new Guid(count, 0, 0, new byte[8]));
                Root["dft_sourcecheckedat"] = Now.AddDays(-1); Root["dft_sourcecurrentuntil"] = Now.AddDays(1);
                FinalRoot = Root;
                History = new EntityCollection();
                for (int i = 1; i <= count; i++)
                {
                    Entity row = RecordedScopeProjectionTests.Row(i);
                    row["dft_recordedat"] = Now.AddDays(-2); row["dft_effectiveat"] = Now.AddDays(-1);
                    row["dft_validfrom"] = Now.AddDays(-10); row["dft_validuntil"] = Now.AddDays(20);
                    History.Entities.Add(row);
                }
                Identity.Results["UserId"] = User; Identity.Results["OrganizationId"] = Org;
            }
            private void Call(string name) { Calls.Add(name); if (FailAt == name) throw Failure; }
            public OrganizationResponse Execute(OrganizationRequest request)
            {
                Assert.IsType<WhoAmIRequest>(request); Call("identity"); return Identity;
            }
            public Entity Retrieve(string table, Guid id, ColumnSet columns)
            {
                Assert.Equal(RegisterSchemaPlan.RecordTable, table); Assert.Equal(DecisionAppendTests.Record, id);
                RootReads.Add(columns); Call(RootReads.Count == 1 ? "root-before" : "root-after");
                if (RootReads.Count == 1) return Root;
                OnFinalRead?.Invoke(); return FinalRoot;
            }
            public EntityCollection RetrieveMultiple(QueryBase query)
            {
                Call("history"); Query = Assert.IsType<QueryExpression>(query); return History;
            }
            public Guid Create(Entity row) => throw new NotSupportedException("Read must not write");
            public void Update(Entity row) => throw new NotSupportedException("Read must not write");
            public void Delete(string table, Guid id) => throw new NotSupportedException("Read must not write");
            public void Associate(string table, Guid id, Relationship relation, EntityReferenceCollection rows) => throw new NotSupportedException();
            public void Disassociate(string table, Guid id, Relationship relation, EntityReferenceCollection rows) => throw new NotSupportedException();
            internal VersionedRecordedScope Read() => RecordedScopeReader.Read(Context, this, DecisionAppendTests.Record);
        }

        [Fact]
        public void ReadsOneBoundedHistoryBetweenTwoVersionedRootChecks()
        {
            var s = new Store(); DateTime earliest = DateTime.UtcNow; VersionedRecordedScope result = s.Read();
            Assert.Equal(new[] { "identity", "root-before", "history", "root-after" }, s.Calls);
            Assert.Equal("42", result.RootVersion); Assert.Equal(RecordedScopeStatus.ScopeRecorded, result.View.Status);
            Assert.Equal(1, result.View.SelectedSequence); Assert.True(result.View.CurrentnessVerified);
            Assert.Equal(s.Now.AddDays(-1), result.SourceCheckedAtUtc); Assert.Equal(s.Now.AddDays(1), result.SourceCurrentUntilUtc);
            Assert.InRange(result.View.AsOfUtc, earliest, DateTime.UtcNow);
            Assert.Equal("recorded-data-only-not-practice-clearance", result.View.Disposition);
            Assert.Equal(2, s.RootReads.Count);
            foreach (ColumnSet columns in s.RootReads)
            {
                Assert.False(columns.AllColumns);
                Assert.Equal(new[] { "dft_latestsequence", "dft_latestdecision", "dft_sourcecheckedat", "dft_sourcecurrentuntil" }, columns.Columns);
            }
            QueryExpression query = Assert.IsType<QueryExpression>(s.Query);
            Assert.Equal(RegisterSchemaPlan.DecisionTable, query.EntityName); Assert.Null(query.TopCount);
            Assert.False(query.Distinct); Assert.Empty(query.LinkEntities); Assert.False(query.ColumnSet.AllColumns);
            Assert.Equal(RecordedScopeProjection.Columns, query.ColumnSet.Columns);
            Assert.Equal(257, query.PageInfo.Count); Assert.Equal(1, query.PageInfo.PageNumber);
            Assert.Null(query.PageInfo.PagingCookie); Assert.False(query.PageInfo.ReturnTotalRecordCount);
            ConditionExpression filter = Assert.Single(query.Criteria.Conditions);
            Assert.Equal("dft_record", filter.AttributeName); Assert.Equal(ConditionOperator.Equal, filter.Operator);
            Assert.Equal(DecisionAppendTests.Record, Assert.Single(filter.Values));
            OrderExpression order = Assert.Single(query.Orders); Assert.Equal("dft_sequence", order.AttributeName); Assert.Equal(OrderType.Ascending, order.OrderType);
        }

        [Fact]
        public void EmptyHistoryStillRequiresAnActualQueryAndStableRoot()
        {
            var s = new Store(0); var result = s.Read();
            Assert.Equal(RecordedScopeStatus.NoEffectiveDecision, result.View.Status); Assert.Null(result.View.ToEntity());
            Assert.Equal(new[] { "identity", "root-before", "history", "root-after" }, s.Calls);
            s = new Store(0); s.Root["dft_latestdecision"] = null!;
            Assert.Equal(0, s.Read().View.SelectedSequence);
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)] [InlineData(4)] [InlineData(5)]
        public void PartialOrOversizedHistoryCannotProduceACleanRead(int change)
        {
            var s = new Store(2);
            if (change == 0) s.History = null!;
            if (change == 1) s.History.Entities.RemoveAt(1);
            if (change == 2) s.History.MoreRecords = true;
            if (change == 3) s.History.TotalRecordCountLimitExceeded = true;
            if (change == 4) s.History.Entities.Add(RecordedScopeProjectionTests.Row(3));
            if (change == 5) s.History.Entities[1].Attributes.Remove("dft_conditionstext");
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.DoesNotContain("root-after", s.Calls);
        }

        [Fact]
        public void OrphanRowsDoNotBecomeAnEmptyRegister()
        {
            var s = new Store(0); s.History.Entities.Add(RecordedScopeProjectionTests.Row());
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read());
        }

        [Theory]
        [InlineData("MessageName", "other")] [InlineData("Stage", 20)] [InlineData("Mode", 1)]
        [InlineData("Depth", 2)] [InlineData("IsExecutingOffline", true)] [InlineData("IsOfflinePlayback", true)]
        public void WrongExecutionContextNeverReachesTheService(string field, object value)
        {
            var s = new Store(); typeof(RemoteExecutionContext).GetProperty(field)!.SetValue(s.Context, value);
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Empty(s.Calls);
        }

        [Fact]
        public void NestedUnboundAndMismatchedPrincipalsFailBeforeReads()
        {
            foreach (string field in new[] { "OrganizationId", "InitiatingUserId", "UserId" })
            {
                var s = new Store(); typeof(RemoteExecutionContext).GetProperty(field)!.SetValue(s.Context, Guid.Empty);
                Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Empty(s.Calls);
            }
            var nested = new Store(); nested.Context.ParentContext = new RemoteExecutionContext();
            Assert.Throws<InvalidPluginExecutionException>(() => nested.Read()); Assert.Empty(nested.Calls);
            var other = new Store(); other.Context.UserId = Store.Org;
            Assert.Throws<InvalidPluginExecutionException>(() => other.Read()); Assert.Empty(other.Calls);
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)] [InlineData(4)] [InlineData(5)]
        public void ExactBoundTargetIsRequiredAndBrowserIdentityOrTimeIsRejected(int change)
        {
            var s = new Store(); var target = (EntityReference)s.Context.InputParameters["Target"];
            if (change == 0) s.Context.InputParameters.Clear();
            if (change == 1) { s.Context.InputParameters.Clear(); s.Context.InputParameters["Actor"] = Store.User; }
            if (change == 2) s.Context.InputParameters["Target"] = "untrusted";
            if (change == 3) target.LogicalName = "other";
            if (change == 4) target.Id = Guid.Empty;
            if (change == 5) target.KeyAttributes.Add("id", "x");
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Empty(s.Calls);
            s = new Store(); s.Context.InputParameters["AsOf"] = DateTime.UtcNow;
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Empty(s.Calls);
        }

        [Fact]
        public void MissingArgumentsAndRecordIdentityDoNotReadAnything()
        {
            var s = new Store();
            Assert.Throws<ArgumentNullException>(() => RecordedScopeReader.Read(null!, s, DecisionAppendTests.Record));
            Assert.Throws<ArgumentNullException>(() => RecordedScopeReader.Read(s.Context, null!, DecisionAppendTests.Record));
            Assert.Throws<InvalidPluginExecutionException>(() => RecordedScopeReader.Read(s.Context, s, Guid.Empty));
            Assert.Empty(s.Calls);
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)]
        public void MismatchedServiceResponsesCannotSubstituteAnElevatedPrincipal(int change)
        {
            var s = new Store();
            if (change == 0) s.Identity = null!; if (change == 1) s.Identity = new OrganizationResponse();
            if (change == 2) s.Identity.Results["UserId"] = Store.Org;
            if (change == 3) s.Identity.Results["OrganizationId"] = Store.User;
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Equal(new[] { "identity" }, s.Calls);
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)] [InlineData(4)] [InlineData(5)]
        [InlineData(6)] [InlineData(7)] [InlineData(8)] [InlineData(9)] [InlineData(10)] [InlineData(11)]
        public void InvalidRootIdentityVersionAndSequenceFailBeforeHistoryRead(int change)
        {
            var s = new Store();
            if (change == 0) s.Root = null!; if (change == 1) s.Root.LogicalName = "other";
            if (change == 2) s.Root.Id = Guid.Empty; if (change == 3) s.Root.RowVersion = null;
            if (change == 4) s.Root.RowVersion = "not-a-version"; if (change == 5) s.Root.RowVersion = "0";
            if (change == 6) s.Root.RowVersion = "042"; if (change == 7) s.Root.Attributes.Remove("dft_latestsequence");
            if (change == 8) s.Root["dft_latestsequence"] = "1"; if (change == 9) s.Root["dft_latestsequence"] = -1;
            if (change == 10) s.Root["dft_latestsequence"] = 257; if (change == 11) s.Root["dft_latestsequence"] = 0;
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.Equal(new[] { "identity", "root-before" }, s.Calls);
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)] [InlineData(4)] [InlineData(5)]
        public void MalformedMissingOrKeyBasedPointersCannotPassTheRootCheck(int change)
        {
            var s = new Store();
            if (change == 0) s.Root.Attributes.Remove("dft_latestdecision");
            if (change == 1) s.Root["dft_latestdecision"] = null!;
            if (change == 2) s.Root["dft_latestdecision"] = "untrusted";
            if (change == 3) ((EntityReference)s.Root["dft_latestdecision"]).LogicalName = "other";
            if (change == 4) ((EntityReference)s.Root["dft_latestdecision"]).Id = Guid.Empty;
            if (change == 5) ((EntityReference)s.Root["dft_latestdecision"]).KeyAttributes.Add("id", "x");
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read()); Assert.DoesNotContain("history", s.Calls);
        }

        [Theory]
        [InlineData("dft_sourcecheckedat")] [InlineData("dft_sourcecurrentuntil")]
        public void MissingLeaseIsUnknownButAmbiguousLeaseIsRejected(string field)
        {
            var s = new Store(); s.Root.Attributes.Remove(field); Assert.False(s.Read().View.CurrentnessVerified);
            s = new Store(); s.Root[field] = null!; Assert.False(s.Read().View.CurrentnessVerified);
            s = new Store(); s.Root[field] = "date"; Assert.Throws<InvalidPluginExecutionException>(() => s.Read());
            s = new Store(); s.Root[field] = DateTime.SpecifyKind(s.Now, DateTimeKind.Unspecified);
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read());
        }

        [Theory]
        [InlineData(0)] [InlineData(1)] [InlineData(2)] [InlineData(3)] [InlineData(4)]
        public void AnyRootChangeDuringRetrievalRejectsTheWholeResultWithoutRetry(int change)
        {
            var s = new Store();
            s.OnFinalRead = () =>
            {
                if (change == 0) s.Root.RowVersion = "43";
                if (change == 1) s.Root["dft_latestsequence"] = 2;
                if (change == 2) s.Root["dft_latestdecision"] = new EntityReference(RegisterSchemaPlan.DecisionTable, Store.Org);
                if (change == 3) s.Root["dft_sourcecheckedat"] = s.Now.AddHours(-2);
                if (change == 4) s.Root["dft_sourcecurrentuntil"] = null!;
            };
            Assert.Throws<InvalidPluginExecutionException>(() => s.Read());
            Assert.Equal(new[] { "identity", "root-before", "history", "root-after" }, s.Calls);
        }

        [Fact]
        public void FinalRootMustStillBeAccessibleAndValid()
        {
            var s = new Store { FinalRoot = null! }; Assert.Throws<InvalidPluginExecutionException>(() => s.Read());
            Assert.Equal("root-after", s.Calls.Last());
        }

        [Fact]
        public void SnapshotIsNotMutatedByLaterSdkResponseObjects()
        {
            var s = new Store(); s.OnFinalRead = () => s.History.Entities[0]["dft_scopetext"] = "later mutation";
            var result = s.Read(); Assert.Equal("Synthetic scope", result.View.ToEntity()!["dft_scopetext"]);
        }

        [Fact]
        public void StaleVerificationDoesNotHideAKnownRecordedRevocation()
        {
            var s = new Store(); s.Root["dft_sourcecurrentuntil"] = s.Now.AddHours(-1);
            s.History.Entities[0]["dft_recordedstate"] = new OptionSetValue(RegisterSchemaPlan.Unverified + 3);
            var result = s.Read(); Assert.False(result.View.CurrentnessVerified); Assert.Equal(RecordedScopeStatus.Revoked, result.View.Status);
        }

        [Theory]
        [InlineData("identity")] [InlineData("root-before")] [InlineData("history")] [InlineData("root-after")]
        public void SdkFaultsEscapeWithoutCachedFallbackRetryOrAdditionalCalls(string phase)
        {
            var s = new Store { FailAt = phase };
            Assert.Same(s.Failure, Assert.Throws<TimeoutException>(() => s.Read()));
            string[] order = { "identity", "root-before", "history", "root-after" };
            Assert.Equal(order.Take(Array.IndexOf(order, phase) + 1), s.Calls);
        }

        [Fact]
        public void NativeMaximumVersionAndHistoryBoundArePreserved()
        {
            var s = new Store(RecordedScopeProjection.MaximumHistory); s.Root.RowVersion = ulong.MaxValue.ToString(System.Globalization.CultureInfo.InvariantCulture);
            var result = s.Read(); Assert.Equal("18446744073709551615", result.RootVersion);
            Assert.Equal(256, result.View.SelectedSequence);
        }
    }
}
