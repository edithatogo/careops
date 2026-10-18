// Power Query M starter queries for the incident dashboard MVP.
// Paste these queries into Power BI Desktop and adjust IncidentCsvPath if needed.

// Query: IncidentCsvPath
let
    Source = "../../data/cleaned_consolidated_incidents_clean_v1_20251108.csv"
in
    Source

// Query: Staging_IncidentsRaw
let
    Source = Csv.Document(
        File.Contents(IncidentCsvPath),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"encrypted_reference_id", type text},
            {"incident_date", type date},
            {"reported_date", type date},
            {"days_to_report", Int64.Type},
            {"reporting_delay_flag", type logical},
            {"incident_year", Int64.Type},
            {"incident_month", Int64.Type},
            {"incident_quarter", Int64.Type},
            {"incident_day_of_week", type text},
            {"weekend_flag", type logical},
            {"month_quarter", type text},
            {"organisation", type text},
            {"lhd", type text},
            {"facility", type text},
            {"unit", type text},
            {"subunit", type text},
            {"incident_classification_clean", type text},
            {"incident_type", type text},
            {"l2_incident_category", type text},
            {"l3_incident_detail", type text},
            {"initial_harm_score", type number},
            {"confirmed_harm_score", type number},
            {"harm_severity_category", type text},
            {"details_clean", type text},
            {"summary_of_incident_clean", type text},
            {"investigated_flag", type logical},
            {"investigation_and_findings", type text},
            {"age_band_clean", type text},
            {"gender_persons_people_affected", type text},
            {"time_band", type text},
            {"aboriginal_or_torres_strait_islander_people_affected", type text},
            {"incident_status", type text},
            {"encrypted_patient_identifier", type text},
            {"encrypted_first_name", type text},
            {"encrypted_surname", type text}
        },
        "en-AU"
    ),
    TrimmedText = Table.TransformColumns(
        TypedColumns,
        {
            {"organisation", each if _ = null then null else Text.Trim(_), type text},
            {"lhd", each if _ = null then null else Text.Trim(_), type text},
            {"facility", each if _ = null then null else Text.Trim(_), type text},
            {"unit", each if _ = null then null else Text.Trim(_), type text},
            {"subunit", each if _ = null then null else Text.Trim(_), type text},
            {"incident_classification_clean", each if _ = null then null else Text.Trim(_), type text},
            {"incident_type", each if _ = null then null else Text.Trim(_), type text},
            {"l2_incident_category", each if _ = null then null else Text.Trim(_), type text},
            {"l3_incident_detail", each if _ = null then null else Text.Trim(_), type text},
            {"harm_severity_category", each if _ = null then null else Text.Trim(_), type text},
            {"incident_status", each if _ = null then null else Text.Trim(_), type text}
        }
    ),
    AddedMonthStart = Table.AddColumn(
        TrimmedText,
        "incident_month_start",
        each Date.StartOfMonth([incident_date]),
        type date
    ),
    AddedHighHarm = Table.AddColumn(
        AddedMonthStart,
        "is_high_harm",
        each [harm_severity_category] = "High Harm",
        type logical
    ),
    AddedHeparinFlag = Table.AddColumn(
        AddedHighHarm,
        "is_heparin_text_match",
        each
            let
                Details = if [details_clean] = null then "" else Text.Lower([details_clean]),
                Summary = if [summary_of_incident_clean] = null then "" else Text.Lower([summary_of_incident_clean]),
                Findings = if [investigation_and_findings] = null then "" else Text.Lower([investigation_and_findings])
            in
                Text.Contains(Details, "heparin")
                or Text.Contains(Summary, "heparin")
                or Text.Contains(Findings, "heparin"),
        type logical
    ),
    AddedDelayBand = Table.AddColumn(
        AddedHeparinFlag,
        "reporting_delay_band",
        each
            let
                Days = [days_to_report]
            in
                if Days = null then "Unknown"
                else if Days <= 1 then "0-1 days"
                else if Days <= 3 then "2-3 days"
                else if Days <= 7 then "4-7 days"
                else if Days <= 14 then "8-14 days"
                else "15+ days",
        type text
    ),
    AddedDefaultAnalysisPeriod = Table.AddColumn(
        AddedDelayBand,
        "in_default_analysis_period",
        each [incident_date] >= #date(2020, 1, 1) and [incident_date] <= #date(2025, 12, 31),
        type logical
    )
in
    AddedDefaultAnalysisPeriod

// Query: DimOrganisation
let
    Source = Staging_IncidentsRaw,
    Selected = Table.SelectColumns(Source, {"organisation", "lhd", "facility", "unit", "subunit"}),
    Deduplicated = Table.Distinct(Selected),
    Sorted = Table.Sort(
        Deduplicated,
        {
            {"organisation", Order.Ascending},
            {"lhd", Order.Ascending},
            {"facility", Order.Ascending},
            {"unit", Order.Ascending},
            {"subunit", Order.Ascending}
        }
    ),
    AddedKey = Table.AddIndexColumn(Sorted, "organisation_key", 1, 1, Int64.Type)
in
    AddedKey

// Query: DimIncidentCategory
let
    Source = Staging_IncidentsRaw,
    Selected = Table.SelectColumns(
        Source,
        {
            "incident_classification_clean",
            "incident_type",
            "l2_incident_category",
            "l3_incident_detail"
        }
    ),
    Deduplicated = Table.Distinct(Selected),
    Sorted = Table.Sort(
        Deduplicated,
        {
            {"incident_classification_clean", Order.Ascending},
            {"incident_type", Order.Ascending},
            {"l2_incident_category", Order.Ascending},
            {"l3_incident_detail", Order.Ascending}
        }
    ),
    AddedKey = Table.AddIndexColumn(Sorted, "incident_category_key", 1, 1, Int64.Type)
in
    AddedKey

// Query: DimHarm
let
    Source = Staging_IncidentsRaw,
    Selected = Table.SelectColumns(Source, {"initial_harm_score", "confirmed_harm_score", "harm_severity_category"}),
    Deduplicated = Table.Distinct(Selected),
    Sorted = Table.Sort(
        Deduplicated,
        {
            {"confirmed_harm_score", Order.Ascending},
            {"initial_harm_score", Order.Ascending},
            {"harm_severity_category", Order.Ascending}
        }
    ),
    AddedKey = Table.AddIndexColumn(Sorted, "harm_key", 1, 1, Int64.Type)
in
    AddedKey

// Query: FactIncidents
let
    Source = Staging_IncidentsRaw,
    JoinedOrganisation = Table.NestedJoin(
        Source,
        {"organisation", "lhd", "facility", "unit", "subunit"},
        DimOrganisation,
        {"organisation", "lhd", "facility", "unit", "subunit"},
        "DimOrganisation",
        JoinKind.LeftOuter
    ),
    ExpandedOrganisationKey = Table.ExpandTableColumn(
        JoinedOrganisation,
        "DimOrganisation",
        {"organisation_key"},
        {"organisation_key"}
    ),
    JoinedCategory = Table.NestedJoin(
        ExpandedOrganisationKey,
        {"incident_classification_clean", "incident_type", "l2_incident_category", "l3_incident_detail"},
        DimIncidentCategory,
        {
            "incident_classification_clean",
            "incident_type",
            "l2_incident_category",
            "l3_incident_detail"
        },
        "DimIncidentCategory",
        JoinKind.LeftOuter
    ),
    ExpandedCategoryKey = Table.ExpandTableColumn(
        JoinedCategory,
        "DimIncidentCategory",
        {"incident_category_key"},
        {"incident_category_key"}
    ),
    JoinedHarm = Table.NestedJoin(
        ExpandedCategoryKey,
        {"initial_harm_score", "confirmed_harm_score", "harm_severity_category"},
        DimHarm,
        {"initial_harm_score", "confirmed_harm_score", "harm_severity_category"},
        "DimHarm",
        JoinKind.LeftOuter
    ),
    ExpandedHarmKey = Table.ExpandTableColumn(
        JoinedHarm,
        "DimHarm",
        {"harm_key"},
        {"harm_key"}
    ),
    RemovedReportUnsafeAndDimensionFields = Table.RemoveColumns(
        ExpandedHarmKey,
        {
            "encrypted_patient_identifier",
            "encrypted_first_name",
            "encrypted_surname",
            "details_clean",
            "summary_of_incident_clean",
            "investigation_and_findings",
            "organisation",
            "lhd",
            "facility",
            "unit",
            "subunit",
            "incident_classification_clean",
            "incident_type",
            "l2_incident_category",
            "l3_incident_detail",
            "initial_harm_score",
            "confirmed_harm_score",
            "harm_severity_category"
        }
    )
in
    RemovedReportUnsafeAndDimensionFields

// Query: DimDate
let
    Source = FactIncidents,
    MinDate = List.Min(Source[incident_date]),
    MaxActualDate = List.Max(Source[incident_date]),
    MaxDate = Date.AddMonths(MaxActualDate, 12),
    DateList = List.Dates(MinDate, Duration.Days(MaxDate - MinDate) + 1, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    AddedYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    AddedQuarter = Table.AddColumn(AddedYear, "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    AddedMonthNumber = Table.AddColumn(AddedQuarter, "Month Number", each Date.Month([Date]), Int64.Type),
    AddedMonthName = Table.AddColumn(AddedMonthNumber, "Month Name", each Date.MonthName([Date]), type text),
    AddedMonthStart = Table.AddColumn(AddedMonthName, "Month Start", each Date.StartOfMonth([Date]), type date),
    AddedMonthYear = Table.AddColumn(AddedMonthStart, "Month Year", each Date.ToText([Date], "yyyy-MM"), type text),
    AddedDayOfWeek = Table.AddColumn(AddedMonthYear, "Day Of Week", each Date.DayOfWeekName([Date]), type text),
    AddedWeekStart = Table.AddColumn(AddedDayOfWeek, "Week Start", each Date.StartOfWeek([Date], Day.Monday), type date),
    AddedIsFutureMonth = Table.AddColumn(AddedWeekStart, "Is Future Month", each [Date] > MaxActualDate, type logical)
in
    AddedIsFutureMonth

// Query: TextFieldRiskRegister
let
    Source = #table(
        type table [field_name = text, mvp_visibility = text, rationale = text],
        {
            {"encrypted_reference_id", "Model key only", "Pseudonymized incident key; avoid displaying on the MVP page."},
            {"encrypted_patient_identifier", "Hidden/removed", "Pseudonymized person reference; not needed for overview reporting."},
            {"encrypted_first_name", "Hidden/removed", "Encrypted person name field; not report-visible."},
            {"encrypted_surname", "Hidden/removed", "Encrypted person name field; not report-visible."},
            {"details_clean", "Not displayed in MVP", "Narrative text requires anonymization QA before visual use."},
            {"summary_of_incident_clean", "Not displayed in MVP", "Narrative text requires anonymization QA before visual use."},
            {"investigation_and_findings", "Not displayed in MVP", "Narrative text requires anonymization QA before visual use."}
        }
    )
in
    Source

// Query: RefreshValidation
let
    Source = FactIncidents,
    RowCount = Table.RowCount(Source),
    DistinctIncidentKeys = List.Count(List.Distinct(Source[encrypted_reference_id])),
    NullIncidentKeys = List.Count(List.Select(Source[encrypted_reference_id], each _ = null or _ = "")),
    NullOrganisationKeys = List.Count(List.Select(Source[organisation_key], each _ = null)),
    NullIncidentCategoryKeys = List.Count(List.Select(Source[incident_category_key], each _ = null)),
    NullHarmKeys = List.Count(List.Select(Source[harm_key], each _ = null)),
    MinIncidentDate = List.Min(Source[incident_date]),
    MaxIncidentDate = List.Max(Source[incident_date]),
    HighHarmCount = Table.RowCount(Table.SelectRows(Source, each [is_high_harm] = true)),
    HeparinTextMatchCount = Table.RowCount(Table.SelectRows(Source, each [is_heparin_text_match] = true)),
    Result = #table(
        type table [check_name = text, check_value = any, expected_or_note = text],
        {
            {"Row count", RowCount, "Configure the expected row count in the private deployment profile."},
            {"Distinct encrypted incident keys", DistinctIncidentKeys, "Should be close to row count; duplicate keys may be legitimate if source records differ."},
            {"Null encrypted incident keys", NullIncidentKeys, "Expected 0 or documented source-data exception."},
            {"Null organisation keys", NullOrganisationKeys, "Expected 0 after dimension key join."},
            {"Null incident category keys", NullIncidentCategoryKeys, "Expected 0 after dimension key join."},
            {"Null harm keys", NullHarmKeys, "Expected 0 after dimension key join."},
            {"Minimum incident date", MinIncidentDate, "Review against source coverage."},
            {"Maximum incident date", MaxIncidentDate, "Review against source coverage."},
            {"High harm incidents", HighHarmCount, "Review against harm-score documentation after confirming high-harm definition."},
            {"Heparin text matches", HeparinTextMatchCount, "Configure the independently reconciled cohort target in the private deployment profile."}
        }
    )
in
    Result

// Query: NarrativeTokens
let
    Source = Csv.Document(
        File.Contents(IncidentCsvPath),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Selected = Table.SelectColumns(
        PromotedHeaders,
        {"encrypted_reference_id", "details_clean", "summary_of_incident_clean", "investigation_and_findings"}
    ),
    AddedText = Table.AddColumn(
        Selected,
        "combined_text",
        each Text.Combine(
            List.Transform(
                { [details_clean], [summary_of_incident_clean], [investigation_and_findings] },
                (value) => if value = null then "" else Text.Lower(Text.From(value))
            ),
            " "
        ),
        type text
    ),
    Normalized = Table.TransformColumns(
        AddedText,
        {
            {
                "combined_text",
                each Text.Select(_, {"a".."z", "0".."9", " "}),
                type text
            }
        }
    ),
    AddedTokens = Table.AddColumn(
        Normalized,
        "token",
        each List.Select(
            Text.SplitAny([combined_text], " "),
            (value) =>
                value <> null
                and value <> ""
                and Text.Length(value) >= 3
                and Text.Select(value, {"0".."9"}) = ""
        ),
        type list
    ),
    ExpandedTokens = Table.ExpandListColumn(AddedTokens, "token"),
    StopWords = {
        "the", "and", "for", "with", "from", "that", "this", "was", "were", "are", "has", "have",
        "had", "not", "but", "due", "into", "out", "too", "its", "any", "all", "can", "may",
        "patient", "staff", "clinician", "nurse", "doctor", "name", "incident", "report"
    },
    Filtered = Table.SelectRows(
        ExpandedTokens,
        each not List.Contains(StopWords, [token])
    ),
    Grouped = Table.Group(
        Filtered,
        {"token"},
        {
            {"token_count", each Table.RowCount(_), Int64.Type}
        }
    ),
    Sorted = Table.Sort(Grouped, {{"token_count", Order.Descending}, {"token", Order.Ascending}})
in
    Sorted

// Query: NarrativeKeyPhrases
let
    Source = Csv.Document(
        File.Contents(IncidentCsvPath),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Selected = Table.SelectColumns(
        PromotedHeaders,
        {"details_clean", "summary_of_incident_clean", "investigation_and_findings"}
    ),
    AddedText = Table.AddColumn(
        Selected,
        "combined_text",
        each Text.Combine(
            List.Transform(
                { [details_clean], [summary_of_incident_clean], [investigation_and_findings] },
                (value) => if value = null then "" else Text.Lower(Text.From(value))
            ),
            " "
        ),
        type text
    ),
    Normalized = Table.TransformColumns(
        AddedText,
        {
            {
                "combined_text",
                each Text.Select(_, {"a".."z", "0".."9", " "}),
                type text
            }
        }
    ),
    AddedTokens = Table.AddColumn(
        Normalized,
        "tokens",
        each List.Select(
            Text.SplitAny([combined_text], " "),
            (value) =>
                value <> null
                and value <> ""
                and Text.Length(value) >= 3
                and Text.Select(value, {"0".."9"}) = ""
        ),
        type list
    ),
    StopWords = {
        "the", "and", "for", "with", "from", "that", "this", "was", "were", "are", "has", "have",
        "had", "not", "but", "due", "into", "out", "too", "its", "any", "all", "can", "may",
        "patient", "staff", "clinician", "nurse", "doctor", "name", "incident", "report"
    },
    FilteredTokens = Table.AddColumn(
        AddedTokens,
        "filtered_tokens",
        each List.Select([tokens], (token) => not List.Contains(StopWords, token)),
        type list
    ),
    AddedBigrams = Table.AddColumn(
        FilteredTokens,
        "bigrams",
        each
            let
                Tokens = [filtered_tokens],
                TokenCount = List.Count(Tokens)
            in
                if TokenCount < 2 then {}
                else List.Transform({0..(TokenCount - 2)}, (index) => Tokens{index} & " " & Tokens{index + 1}),
        type list
    ),
    AddedTrigrams = Table.AddColumn(
        AddedBigrams,
        "trigrams",
        each
            let
                Tokens = [filtered_tokens],
                TokenCount = List.Count(Tokens)
            in
                if TokenCount < 3 then {}
                else List.Transform(
                    {0..(TokenCount - 3)},
                    (index) => Tokens{index} & " " & Tokens{index + 1} & " " & Tokens{index + 2}
                ),
        type list
    ),
    BigramRows = Table.AddColumn(
        Table.ExpandListColumn(AddedTrigrams, "bigrams"),
        "phrase_word_count",
        each 2,
        Int64.Type
    ),
    BigramSelected = Table.SelectColumns(BigramRows, {"bigrams", "phrase_word_count"}),
    BigramRenamed = Table.RenameColumns(BigramSelected, {{"bigrams", "phrase"}}),
    TrigramRows = Table.AddColumn(
        Table.ExpandListColumn(AddedTrigrams, "trigrams"),
        "phrase_word_count",
        each 3,
        Int64.Type
    ),
    TrigramSelected = Table.SelectColumns(TrigramRows, {"trigrams", "phrase_word_count"}),
    TrigramRenamed = Table.RenameColumns(TrigramSelected, {{"trigrams", "phrase"}}),
    Combined = Table.Combine({BigramRenamed, TrigramRenamed}),
    NonBlank = Table.SelectRows(Combined, each [phrase] <> null and [phrase] <> ""),
    Grouped = Table.Group(
        NonBlank,
        {"phrase", "phrase_word_count"},
        {
            {"phrase_count", each Table.RowCount(_), Int64.Type}
        }
    ),
    Sorted = Table.Sort(
        Grouped,
        {
            {"phrase_count", Order.Descending},
            {"phrase_word_count", Order.Ascending},
            {"phrase", Order.Ascending}
        }
    )
in
    Sorted

// Query: NarrativeSentiment
let
    Source = Csv.Document(
        File.Contents(IncidentCsvPath),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Selected = Table.SelectColumns(
        PromotedHeaders,
        {"encrypted_reference_id", "details_clean", "summary_of_incident_clean", "investigation_and_findings"}
    ),
    Combined = Table.AddColumn(
        Selected,
        "combined_text",
        each Text.Lower(
            Text.Combine(
                List.Transform(
                    { [details_clean], [summary_of_incident_clean], [investigation_and_findings] },
                    (value) => if value = null then "" else Text.From(value)
                ),
                " "
            )
        ),
        type text
    ),
    Cleaned = Table.TransformColumns(
        Combined,
        {
            {
                "combined_text",
                each Text.Select(_, {"a".."z", "0".."9", " "}),
                type text
            }
        }
    ),
    Tokenized = Table.AddColumn(
        Cleaned,
        "tokens",
        each List.Select(
            Text.SplitAny([combined_text], " "),
            (value) =>
                value <> null
                and value <> ""
                and Text.Length(value) >= 3
                and Text.Select(value, {"0".."9"}) = ""
        ),
        type list
    ),
    PositiveWords = {
        "improved", "stable", "resolved", "resolved", "safe", "appropriate", "normal", "effective",
        "good", "recovered", "clear", "successful", "maintained", "managed", "completed"
    },
    NegativeWords = {
        "delay", "delayed", "error", "missed", "incorrect", "wrong", "poor", "harm", "adverse",
        "failure", "failed", "incident", "bleed", "infection", "complication", "concern", "deterioration"
    },
    WithCounts = Table.AddColumn(
        Tokenized,
        "positive_count",
        each List.Count(List.Select([tokens], (token) => List.Contains(PositiveWords, token))),
        Int64.Type
    ),
    WithNegative = Table.AddColumn(
        WithCounts,
        "negative_count",
        each List.Count(List.Select([tokens], (token) => List.Contains(NegativeWords, token))),
        Int64.Type
    ),
    WithScore = Table.AddColumn(
        WithNegative,
        "sentiment_score",
        each [positive_count] - [negative_count],
        Int64.Type
    ),
    WithLabel = Table.AddColumn(
        WithScore,
        "sentiment_label",
        each
            if [sentiment_score] > 0 then "Positive"
            else if [sentiment_score] < 0 then "Negative"
            else "Neutral",
        type text
    ),
    Trimmed = Table.SelectColumns(
        WithLabel,
        {"encrypted_reference_id", "positive_count", "negative_count", "sentiment_score", "sentiment_label"}
    )
in
    Trimmed

// Query: NarrativeAnonymizationQA
let
    Source = Csv.Document(
        File.Contents(IncidentCsvPath),
        [
            Delimiter = ",",
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Selected = Table.SelectColumns(
        PromotedHeaders,
        {"encrypted_reference_id", "details_clean", "summary_of_incident_clean", "investigation_and_findings"}
    ),
    Combined = Table.AddColumn(
        Selected,
        "raw_text",
        each Text.Lower(
            Text.Combine(
                List.Transform(
                    { [details_clean], [summary_of_incident_clean], [investigation_and_findings] },
                    (value) => if value = null then "" else Text.From(value)
                ),
                " "
            )
        ),
        type text
    ),
    Flags = Table.AddColumn(
        Combined,
        "contains_identifier_hint",
        each
            Text.Contains([raw_text], "@")
            or Text.Contains([raw_text], "dob")
            or Text.Contains([raw_text], "mrn")
            or Text.Contains([raw_text], "date of birth")
            or Text.Contains([raw_text], "phone")
            or Text.Contains([raw_text], "mobile")
            or Text.Contains([raw_text], "address")
            or Text.Contains([raw_text], "incident number"),
        type logical
    ),
    CountDigits = Table.AddColumn(
        Flags,
        "long_digit_run_count",
        each
            List.Count(
                List.Select(
                    Text.SplitAny([raw_text], " ,.;:/\()[]{}<>-_"),
                    (token) => Text.Length(Text.Select(token, {"0".."9"})) >= 6 and Text.Select(token, {"0".."9"}) = token
                )
            ),
        Int64.Type
    ),
    Sampled = Table.SelectRows(CountDigits, each [contains_identifier_hint] = true or [long_digit_run_count] > 0),
    Result = Table.SelectColumns(
        Sampled,
        {"encrypted_reference_id", "contains_identifier_hint", "long_digit_run_count"}
    )
in
    Result

// Query: MvpPrivacyValidation
let
    Source = FactIncidents,
    ColumnNames = Table.ColumnNames(Source),
    DisallowedColumns = {
        "encrypted_patient_identifier",
        "encrypted_first_name",
        "encrypted_surname",
        "details_clean",
        "summary_of_incident_clean",
        "investigation_and_findings"
    },
    PresentDisallowedColumns = List.Intersect({ColumnNames, DisallowedColumns}),
    Result = #table(
        type table [check_name = text, status = text, detail = text],
        {
            {
                "MVP report-visible unsafe columns removed",
                if List.Count(PresentDisallowedColumns) = 0 then "Pass" else "Fail",
                if List.Count(PresentDisallowedColumns) = 0 then "No unsafe columns found in FactIncidents." else Text.Combine(PresentDisallowedColumns, ", ")
            }
        }
    )
in
    Result
