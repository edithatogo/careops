using System;
using System.Collections.Generic;
using System.Globalization;
using System.Runtime.Remoting.Messaging;
using System.Runtime.Remoting.Proxies;
using CareOps.Decisions.DataverseIdentity;
using CareOps.Decisions.RegisterSchema;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Messages;
using Microsoft.Xrm.Sdk.Query;
using Xunit;

namespace CareOps.Decisions.DataverseIdentity.Tests
{
    public sealed class NativeConfirmationFenceTests
    {
        private const string Failure = "Original confirmation changed or could not be protected for recording. Abort this transaction; do not repeat the decision.";
        private sealed class Context : RealProxy
        {
            internal readonly Dictionary<string, object?> Values = new Dictionary<string, object?>
            {
                ["MessageName"] = RegisterJournalAppender.ApiName, ["Stage"] = 30, ["Mode"] = 0, ["IsInTransaction"] = true,
                ["Depth"] = 1, ["ParentContext"] = null, ["IsExecutingOffline"] = false, ["IsOfflinePlayback"] = false,
                ["OrganizationId"] = FakeDataverse.Org, ["UserId"] = FakeDataverse.UserId, ["InitiatingUserId"] = FakeDataverse.UserId,
                ["InputParameters"] = new ParameterCollection { ["Target"] = new EntityReference(RegisterSchemaPlan.RecordTable, NativeConfirmationSourceTests.RecordId) }
            };
            internal Context() : base(typeof(IPluginExecutionContext)) { }
            internal IPluginExecutionContext Value => (IPluginExecutionContext)GetTransparentProxy();
            public override IMessage Invoke(IMessage message)
            {
                var call = (IMethodCallMessage)message;
                return new ReturnMessage(Values[call.MethodName.Substring(4)], null, 0, call.LogicalCallContext, call);
            }
        }
        private sealed class Host : IOrganizationServiceFactory, IOrganizationService
        {
            internal readonly NativeConfirmationSourceTests.Store Store = new NativeConfirmationSourceTests.Store();
            internal readonly Context Context = new Context();
            internal readonly List<UpdateRequest> Updates = new List<UpdateRequest>();
            internal readonly List<string> Calls = new List<string>();
            internal Action? BeforeCompare, AfterUpdate, FirstRead;
            internal bool FailUpdate, SuppressVersionAdvance, IgnoreToken;
            internal OrganizationResponse Reply = new UpdateResponse();
            internal int FactoryCalls;
            internal CallerBinding Binding() => CallerResolver.ResolveBinding(Context.Value, this);
            internal NativeConfirmation Run() => NativeConfirmationFence.Acquire(Context.Value, Binding(), NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId);
            internal void Denied()
            {
                var error = Assert.Throws<InvalidPluginExecutionException>(() => Run());
                Assert.Equal(Failure, error.Message); Assert.Null(error.InnerException);
            }
            public IOrganizationService CreateOrganizationService(Guid? id)
            { FactoryCalls++; Assert.Equal(FakeDataverse.UserId, id); return this; }
            public OrganizationResponse Execute(OrganizationRequest request)
            {
                if (!(request is UpdateRequest update)) return Store.Execute(request);
                Calls.Add("conditional-update"); Updates.Add(update);
                Assert.Equal(ConcurrencyBehavior.IfRowVersionMatches, update.ConcurrencyBehavior);
                Assert.Equal(ConfirmationSourceSchema.Table, update.Target.LogicalName); Assert.Equal(NativeConfirmationSourceTests.SourceId, update.Target.Id);
                Assert.Equal("dft_fencetoken", Assert.Single(update.Target.Attributes).Key);
                Assert.Empty(update.Target.KeyAttributes); Assert.Empty(update.Target.RelatedEntities);
                string token = Assert.IsType<string>(update.Target["dft_fencetoken"]);
                Assert.True(Guid.TryParseExact(token, "N", out Guid marker)); Assert.NotEqual(Guid.Empty, marker);
                BeforeCompare?.Invoke();
                if (FailUpdate || update.Target.RowVersion != Store.Source.RowVersion)
                    throw new InvalidOperationException("private native version or permission fault");
                if (!IgnoreToken) Store.Source["dft_fencetoken"] = token;
                if (!SuppressVersionAdvance) Store.Source.RowVersion = (ulong.Parse(Store.Source.RowVersion, CultureInfo.InvariantCulture) + 1).ToString(CultureInfo.InvariantCulture);
                AfterUpdate?.Invoke(); return Reply;
            }
            public Entity Retrieve(string table, Guid id, ColumnSet columns)
            {
                if (table == ConfirmationSourceSchema.Table)
                {
                    Calls.Add("source-read");
                    if (Store.SourceReads == 0) FirstRead?.Invoke();
                }
                return Store.Retrieve(table, id, columns);
            }
            public EntityCollection RetrieveMultiple(QueryBase request) => Store.RetrieveMultiple(request);
            public Guid Create(Entity row) => throw new NotSupportedException("No capture or journal save by a fence");
            public void Update(Entity row) => throw new NotSupportedException("No unconditional update");
            public void Delete(string table, Guid id) => throw new NotSupportedException("No compensation");
            public void Associate(string table, Guid id, Relationship r, EntityReferenceCollection rows) => throw new NotSupportedException();
            public void Disassociate(string table, Guid id, Relationship r, EntityReferenceCollection rows) => throw new NotSupportedException();
        }

        [Fact]
        public void SameNativeServiceConditionallyUpdatesOnlyTheTokenAndReturnsUnchangedOriginalEvidence()
        {
            var h = new Host(); string digest = (string)h.Store.Source["dft_originaldigest"];
            NativeConfirmation result = h.Run();
            Assert.Equal(1, h.FactoryCalls); Assert.Equal(new[] { "source-read", "conditional-update", "source-read" }, h.Calls);
            Assert.Equal("12", Assert.Single(h.Updates).Target.RowVersion); Assert.Equal("13", result.RowVersion);
            Assert.Equal(h.Updates[0].Target["dft_fencetoken"], result.FenceToken);
            Assert.Equal(digest, result.Confirmation.Digest); Assert.True(h.Store.Intent.Matches(result.Intent.ToEntity()));
            Assert.Equal("synthetic-rule-v1", result.PolicyReference); Assert.Equal(NativeConfirmationSourceTests.SourceId, result.SourceId);
            h.Store.Source["dft_originaldocument"] = "changed after return";
            Assert.True(h.Store.Intent.Matches(result.Intent.ToEntity()));
        }
        [Fact]
        public void MissingComponentsAndIdsNeverIssueAConditionalUpdate()
        {
            var h = new Host(); CallerBinding binding = h.Binding();
            Assert.Throws<ArgumentNullException>(() => NativeConfirmationFence.Acquire(null!, binding, NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId));
            Assert.Throws<ArgumentNullException>(() => NativeConfirmationFence.Acquire(h.Context.Value, null!, NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId));
            Assert.Throws<ArgumentException>(() => NativeConfirmationFence.Acquire(h.Context.Value, binding, Guid.Empty, NativeConfirmationSourceTests.SourceId));
            Assert.Throws<ArgumentException>(() => NativeConfirmationFence.Acquire(h.Context.Value, binding, NativeConfirmationSourceTests.RecordId, Guid.Empty));
            Assert.Empty(h.Calls);
        }
        [Theory]
        [InlineData("MessageName", "Retrieve")] [InlineData("Stage", 20)] [InlineData("Mode", 1)]
        [InlineData("IsInTransaction", false)] [InlineData("Depth", 2)]
        [InlineData("IsExecutingOffline", true)] [InlineData("IsOfflinePlayback", true)]
        public void ReadOnlyOrDetachedPipelineCannotAcquireASourceFence(string field, object value)
        {
            var h = new Host(); CallerBinding binding = h.Binding(); h.Context.Values[field] = value;
            var error = Assert.Throws<InvalidPluginExecutionException>(() => NativeConfirmationFence.Acquire(h.Context.Value, binding,
                NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId));
            Assert.Equal(Failure, error.Message); Assert.Empty(h.Calls);
        }
        [Theory]
        [InlineData("OrganizationId")] [InlineData("UserId")] [InlineData("InitiatingUserId")]
        public void ABindingFromAnotherContextCannotBeSubstituted(string field)
        {
            var h = new Host(); CallerBinding binding = h.Binding(); h.Context.Values[field] = NativeConfirmationSourceTests.OwnerId;
            Assert.Throws<InvalidPluginExecutionException>(() => NativeConfirmationFence.Acquire(h.Context.Value, binding,
                NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId));
            Assert.Empty(h.Calls);
        }
        [Fact]
        public void NestedOrMalformedTargetContextsCannotStartSourceWork()
        {
            var h = new Host(); CallerBinding binding = h.Binding(); h.Context.Values["ParentContext"] = h.Context.Value;
            Assert.Throws<InvalidPluginExecutionException>(() => NativeConfirmationFence.Acquire(h.Context.Value, binding,
                NativeConfirmationSourceTests.RecordId, NativeConfirmationSourceTests.SourceId));
            Assert.Empty(h.Calls);
            object?[] bad = { null, "id", new Entity(RegisterSchemaPlan.RecordTable, NativeConfirmationSourceTests.RecordId),
                new EntityReference("wrong", NativeConfirmationSourceTests.RecordId),
                new EntityReference(RegisterSchemaPlan.RecordTable, NativeConfirmationSourceTests.OwnerId),
                new EntityReference(RegisterSchemaPlan.RecordTable, NativeConfirmationSourceTests.RecordId) { KeyAttributes = { ["name"] = "alias" } } };
            foreach (object? value in bad)
            { h = new Host(); ((ParameterCollection)h.Context.Values["InputParameters"]!)["Target"] = value!; h.Denied(); Assert.Empty(h.Calls); }
            h = new Host(); ((ParameterCollection)h.Context.Values["InputParameters"]!).Clear(); h.Denied(); Assert.Empty(h.Calls);
            h = new Host(); h.Context.Values["InputParameters"] = null; h.Denied(); Assert.Empty(h.Calls);
        }
        [Fact]
        public void AnUnavailableOrWithdrawnOriginalSourceIsNotRebuiltOrAutomaticallyReleased()
        {
            var h = new Host(); h.Store.Source["dft_withdrawn"] = true; h.Denied(); Assert.Empty(h.Updates);
            h = new Host(); h.Store.FailRead = true; h.Denied(); Assert.Empty(h.Updates);
            h = new Host(); h.Store.Source["dft_originaldigest"] = new string('c', 64); h.Denied(); Assert.Empty(h.Updates);
        }
        [Fact]
        public void AnInterveningNativeVersionChangeRejectsTheAttemptWithoutRetry()
        {
            var h = new Host(); h.BeforeCompare = () => { h.Store.Source.RowVersion = "99"; h.Store.Source["dft_withdrawn"] = true; };
            h.Denied(); Assert.Single(h.Updates); Assert.Equal("12", h.Updates[0].Target.RowVersion);
            Assert.Equal(1, h.Store.SourceReads); Assert.Equal(true, h.Store.Source["dft_withdrawn"]);
            Assert.Equal(NativeConfirmationSourceTests.TokenId.ToString("N"), h.Store.Source["dft_fencetoken"]);
        }
        [Fact]
        public void PermissionOrNativeConditionalUpdateFailureEscapesWithoutCompensation()
        {
            var h = new Host { FailUpdate = true }; h.Denied(); Assert.Single(h.Updates);
            Assert.Equal(new[] { "source-read", "conditional-update" }, h.Calls); Assert.Equal("12", h.Store.Source.RowVersion);
        }
        [Theory]
        [InlineData(false)] [InlineData(true)]
        public void MissingOrWrongSdkUpdateResponseCannotBeReportedAsProtected(bool missing)
        {
            var h = new Host { Reply = missing ? null! : new OrganizationResponse() }; h.Denied();
            Assert.Single(h.Updates); Assert.Equal(1, h.Store.SourceReads);
            // This fake applies a change but does not simulate rollback. The exception must escape in real Dataverse.
            Assert.Equal("13", h.Store.Source.RowVersion);
        }
        [Fact]
        public void SuccessfulSdkResponseNeedsANewVersionAndTheExactWrittenToken()
        {
            var noVersion = new Host { SuppressVersionAdvance = true }; noVersion.Denied(); Assert.Single(noVersion.Updates);
            var noToken = new Host { IgnoreToken = true }; noToken.Denied(); Assert.Single(noToken.Updates);
        }
        [Theory]
        [InlineData("digest")] [InlineData("policy")] [InlineData("pathway")] [InlineData("confirmed")] [InlineData("until")]
        public void APostUpdateExtensionCannotAlterOriginalEvidenceWhileAcquiringTheFence(string field)
        {
            var h = new Host(); h.AfterUpdate = () =>
            {
                if (field == "digest") { h.Store.Payload["dft_conditionstext"] = "changed"; h.Store.Intent = h.Store.NewIntent(); h.Store.SaveDocument(); }
                if (field == "policy") h.Store.Source["dft_policyref"] = "different-approved-looking-reference";
                if (field == "pathway") h.Store.Source["dft_pathway"] = "different";
                if (field == "confirmed") h.Store.Source["dft_confirmedutc"] = h.Store.At.AddMinutes(-3).ToString("O", CultureInfo.InvariantCulture);
                if (field == "until") h.Store.Source["dft_currentuntilutc"] = h.Store.At.AddHours(2).ToString("O", CultureInfo.InvariantCulture);
            };
            h.Denied(); Assert.Single(h.Updates); Assert.Equal(2, h.Store.SourceReads);
        }
        [Fact]
        public void WithdrawalOrLostReadAccessAfterTokenStagingStillAbortsTheWholeAttempt()
        {
            var h = new Host(); h.AfterUpdate = () => h.Store.Source["dft_withdrawn"] = true; h.Denied(); Assert.Single(h.Updates);
            h = new Host(); h.AfterUpdate = () => h.Store.FailRead = true; h.Denied(); Assert.Single(h.Updates);
            Assert.Equal(new[] { "source-read", "conditional-update", "source-read" }, h.Calls);
        }
        [Fact]
        public void MutatedIncomingTargetCannotRedirectTheConditionalWriteOrSourceReads()
        {
            var h = new Host(); h.FirstRead = () =>
                ((EntityReference)((ParameterCollection)h.Context.Values["InputParameters"]!)["Target"]).Id = NativeConfirmationSourceTests.OwnerId;
            NativeConfirmation result = h.Run(); Assert.Equal(NativeConfirmationSourceTests.RecordId, result.Intent.RecordId);
            Assert.Equal(NativeConfirmationSourceTests.SourceId, Assert.Single(h.Updates).Target.Id);
        }
    }
}
