# KOL Radar — Product Charter

**Status:** Living draft  
**Purpose:** Preserve the product intent and the decisions behind KOL Radar as it evolves.

## 1. The problem

Mapping relevant investigators for a therapeutic area and territory is often a manual, time-intensive task for Medical Science Liaisons (MSLs). It requires searching fragmented public sources, reconciling names and affiliations, distinguishing current from historical activity, and explaining why certain people merit further research.

This also appears in MSL interview exercises: for example, mapping researchers in lung cancer across Chile and defending a first-priority set for scientific engagement.

## 2. Product objective

Help an MSL turn a broad question into a defensible, evidence-led research map:

> For a defined therapeutic area, territory, and time period, who should I investigate first, why, and what evidence supports that priority?

KOL Radar should reduce the time spent collecting and reconciling public information. It should not replace the MSL's scientific judgment or claim to determine professional value.

## 3. Primary user

An oncology MSL, or a candidate completing an MSL interview exercise, who needs to prepare country-level intelligence for Chile quickly and responsibly.

### Their core needs

1. Find relevant people, institutions, and clinical trials for a precise question.
2. Understand why each result is surfaced.
3. Inspect sources and distinguish verified evidence from uncertain matches.
4. Prioritize a small group for deeper research and engagement planning.
5. Explain the method clearly to a manager or interviewer.

### Entity model for the first use case

People are the primary research candidates and the primary unit of prioritization. For the first use case, these candidates are physicians relevant to lung cancer. Institutions are an essential second layer of context: they show where a physician is affiliated, where a trial is conducted, and which sites concentrate relevant activity.

A person may have more than one affiliation. KOL Radar must preserve those relationships with their evidence and date; it must not silently force one institution as the person's only workplace. A “main” or “current” affiliation may be shown only when a source explicitly supports that interpretation. Otherwise, the interface should state the affiliation as observed and retain uncertainty.

## 4. Job to be done

When I am preparing an interview exercise, territory plan, or scientific interaction plan, I want to map the relevant ecosystem from public evidence so that I can focus my research and justify my initial prioritization.

### The practical questions the user needs answered

For a defined disease area and territory, the user needs to answer three questions quickly and responsibly:

1. **Who should I investigate first?** A prioritized set of physicians, not a definitive KOL list.
2. **Why are they a priority?** The specific, relevant public signals behind the priority.
3. **What evidence supports it, and what remains uncertain?** Source links, evidence date, the nature of each association, and confidence limitations.

The desired outcome is a defensible first-pass map that focuses subsequent MSL research. It is useful in an interview because the user can explain both the method and its boundaries, rather than presenting an unsupported list of names.

### What the user values in the product

- A fast way to narrow a broad territory question into a manageable research shortlist.
- Clear separation between a physician, their multiple evidence-backed institutional affiliations, and related clinical trials.
- Peer-reviewed publications relevant to the disease area, rather than generic publication volume.
- Verifiable clinical-trial participation and role where publicly available.
- Recency, so that historical activity does not look equivalent to current activity.
- A visible evidence trail for every meaningful priority signal.
- An explicit statement that the product supports research prioritization; it does not determine professional quality, influence, or engagement decisions.

## 5. What the score means

The score is an **evidence-based priority signal**, not a declaration that a person is a KOL, the best clinician, or more professionally valuable than another person.

It should be:

- Comparable only within a clearly defined search scope.
- Explainable through visible components and linked sources.
- Time-aware: recent signals should be distinguishable from historic ones.
- Explicit about confidence, ambiguity, and missing evidence.

Potential public signals include relevant publications, documented roles in clinical trials, institutional links, and publicly sourced teaching or congress activity. Their weighting must be documented and reviewable.

For the first use case, the core priority signals are relevant peer-reviewed publications, verifiable clinical-trial participation, and recency. Institutional affiliation and network links provide essential context, but should not be used to claim that a physician has only one workplace or that an institution itself confers professional leadership.

### How the ranked output is used

One relevant public signal is enough for a physician to appear in the research map. The score then determines the **priority for further MSL research and contact preparation**:

| Priority | Interpretation | Suggested next step |
| --- | --- | --- |
| High | Multiple, relevant, recent, and well-supported signals | Research in depth and prepare for a possible scientific interaction. |
| Medium | Relevant evidence exists but requires contextual review or has less depth/recency | Review the evidence and determine fit with the medical strategy. |
| Monitor | Limited, old, incomplete, or uncertain evidence | Retain in the map and reassess when evidence changes. |

The ranking supports where to invest research time. A decision to initiate contact remains a deliberate MSL and compliance-governed decision, informed by medical strategy and the evidence shown in the profile.

## 5A. Draft signal framework for the ranking

The ranking should combine distinct, source-linked dimensions rather than equating a raw count with influence.

### A. Disease-relevant scientific and clinical research activity

- Authorship of peer-reviewed publications relevant to lung cancer, with author role shown where available.
- Verifiable involvement in clinical trials, with the public role distinguished (for example, principal investigator, site investigator, or listed contact).
- Participation in Chilean clinical guidelines, consensus documents, or other scientific guidance relevant to the disease area.

### B. Visible scientific influence among peers

- Invited speaker, chair, moderator, faculty, or programme-committee role in a relevant scientific congress, meeting, or course.
- Leadership or committee roles in a relevant professional or scientific society.
- Authorship or leadership in national scientific guidance.

These are public proxies for scientific recognition, not proof that peers universally view a physician as a KOL. A speaker role must retain its event, organiser, topic, date, and source; it must not be inferred from an unsupported claim or a commercial list.

### C. Current ecosystem activity and context

- Recency of each signal.
- Evidence-backed affiliations, including multiple institutions where applicable.
- Connections among physicians, institutions, publications, and trials.

Affiliation, network size, or working at a prominent institution should provide context, not automatically confer leadership.

### Explicit exclusions and uncertainty

Professional reputation and procedure volume may matter in real MSL judgment but are not consistently public or comparable. They must not be fabricated into the score. If credible, public, source-linked information becomes available, it can be displayed separately with its limitations; otherwise it remains a human-validation question.

For the first version, publicly verifiable procedure-volume or clinical-experience information may appear as supplementary context, with source and date, but will not receive points. This avoids privileging physicians merely because their activity is more publicly documented.

## 5B. Draft scoring design

The current prototype's simple point summation is not sufficient. The first scoring model should be interpretable, bounded, and resistant to raw-volume bias.

### Design principles

1. Score only disease-relevant, source-linked public evidence.
2. Use categories and caps so that repeated weak signals cannot outweigh one strong, relevant signal.
3. Apply recency to every signal; old evidence remains visible as history but contributes less to current priority.
4. Show evidence confidence separately from priority. A high score from uncertain identity matching must not look equally trustworthy.
5. Do not reward institution prestige, raw network size, or unsupported reputation as if they prove scientific leadership.

### Proposed scorecard: seven visible evidence dimensions

The user should see the components separately. We will assign point values only after each component has a clear public-evidence rule and a cap.

| Dimension | What it represents |
| --- | --- |
| Clinical-trial role | Documented, disease-relevant trial participation, with role and study status distinguished. |
| Peer-reviewed publications | Relevant scientific contribution, with topic, recency, and author role considered. |
| Guidelines and consensus documents | Authorship or formal contribution to relevant Chilean scientific guidance. |
| Congress and scientific speaking | Documented invited speaker, chair, moderator, faculty, or programme role; attendance alone is not equivalent. |
| Teaching and scientific education | Publicly documented academic teaching, courses, or faculty roles relevant to the disease area. |
| Society and research leadership | Relevant professional-society, research-network, editorial, or committee role when publicly documented. |
| Ecosystem activity and reach | Evidence-backed affiliations, research connections, and active sites, capped so prominence or network size cannot dominate. |

### Modifiers, not additional score buckets

- **Recency:** each signal's contribution declines with age. A suggested initial scale is full value within one year, reduced value from one to three years, lower value from three to five years, and historical display only after five years.
- **Confidence:** verified identity and source links receive full credit. Name-only or ambiguous associations receive reduced credit and a visible confidence label; unresolvable matches are not scored.

### Output shown to the user

The interface should present both:

- **Priority score and tier**: high, medium, or monitor.
- **Evidence confidence**: high, medium, or pending review.

This prevents a score from looking more certain or more absolute than the evidence allows. Detailed point rules for each trial role, publication, guideline, and congress role remain the next design decision.

## 6. What remains human judgment

Some meaningful aspects of opinion leadership cannot be reliably inferred from public data alone: peer trust, local influence, clinical practice volume, quality of scientific exchange, patient access, and fit with a particular medical strategy.

The product must support, not hide, this uncertainty. These factors may be recorded later as validated field intelligence only with an appropriate governance model.

## 7. Intended workflow

1. Define the question: therapeutic area, disease/subtopic, geography, and time window.
2. Gather and normalize evidence from named public sources.
3. Surface people, institutions, and studies with an explainable priority signal.
4. Let the user inspect the evidence and confidence for each association.
5. Produce a concise, defensible research shortlist for the user to refine.

## 8. Success criteria

- A user can complete a first-pass map materially faster than a manual search.
- Every displayed priority can be traced to evidence and a retrieval date.
- The user can articulate the method and its limitations in an interview.
- The interface does not imply that incomplete public evidence measures professional quality.

## 9. Non-goals for the first version

- Make a definitive KOL designation.
- Rank clinical quality or professional performance.
- Replace compliance-approved field intelligence processes.
- Infer private, sensitive, or unsupported information.

## 10. Decisions to make next

1. Define the exact first search scenario for the prototype.
2. Decide which public sources are in scope and how often they refresh.
3. Define the score components, weights, confidence rules, and freshness rules.
4. Define the ideal output for an interview exercise.
5. Compare the current page against that workflow and identify gaps.

## 11. Working method

We will progress through the following sequence. Each stage ends with a short documented decision before work begins on the next stage.

### Stage 1 — Frame the first use case

Specify the exact question KOL Radar must answer in its first credible scenario: disease area, geography, user context, time window, and desired output.

**Decision gate:** one written search brief.

### Stage 2 — Define the priority model

Choose only the signals that are appropriate to compare from public evidence. Define their meaning, weights, freshness treatment, confidence rules, and exclusions.

**Decision gate:** a transparent scoring specification, including limitations.

### Stage 3 — Define the evidence pipeline

Name the public sources, what each source contributes, how identities and affiliations are reconciled, refresh cadence, and the conditions that require human review.

**Decision gate:** an evidence and provenance map.

### Stage 4 — Design the user's workflow

Describe the inputs, result list, evidence review, shortlist, and interview-ready output. The experience must answer: “who, why, source, recency, and uncertainty.”

**Decision gate:** a user-flow and output specification.

### Stage 5 — Run a worked example

Use one bounded scenario to test the full method before expanding scope. Compare the result with a careful manual research pass and record mismatches.

**Decision gate:** validated example and corrections to the model.

### Stage 6 — Gap analysis and build plan

Evaluate the current KOL Radar page against the approved workflow. Separate required changes from later enhancements, then prioritize the smallest useful version.

**Decision gate:** a prioritized backlog with acceptance criteria.

### Stage 7 — Validate with the target user

Ask an MSL or MSL candidate to perform the scenario, explain the output, and identify where the tool saves time or creates uncertainty.

**Decision gate:** evidence that the product supports a real workflow rather than only a plausible demo.

## 12. First working session

We begin with Stage 1. The proposed initial scenario is:

> “Prepare an evidence-led first-pass map of people and institutions relevant to lung cancer across Chile, using public evidence from the last five years, in order to identify and prioritize a defensible shortlist for further MSL research.”

This is a draft, not yet an approved specification. It will be refined before scoring, data collection, or interface changes.

## 13. Landscape scan — public and open tools (2026-08-15)

### Closest references

| Tool or source | What it contributes | Limitation for KOL Radar Chile |
| --- | --- | --- |
| [findmyKOL](https://www.findmykol.com/) | A public, search-first KOL directory with cited profiles, filters for therapeutic area, geography, trials, publications, and public-web enrichment. | It describes itself as an open directory, not an openly reusable end-to-end codebase. Its core identity and enrichment sources are strongly U.S.-oriented (NPPES, CMS Open Payments, NIH RePORTER), so it is a design reference rather than a Chile-ready solution. |
| [VOSviewer](https://www.vosviewer.com/) | Freely available bibliometric and network-mapping software that can use PubMed, OpenAlex, Crossref, and related sources. | Useful for co-authorship and publication networks, but does not create MSL-ready physician profiles, validate identity, rank candidates, or add Chilean trial and congress context. |
| [ISP Chile — Estudios Clínicos](https://www.ispch.gob.cl/anamed/estudios-clinicos/) | The official authority states that it makes public informational databases available to support transparency and monitoring of studies in Chile. | It is a public clinical-trial source, not a KOL-mapping product; availability and detail need to be validated for each retrieval route. |
| [CIF Chile clinical-trial finder](https://estudiosclinicos.cl/) | Searchable Chilean information on ongoing studies, by therapeutic area, pathology, region, and status. | Its stated coverage is studies sponsored or requested by member companies and its purpose is patient-facing study discovery; it is not a complete researcher or KOL registry. |

### Conclusion

A focused search did not identify an open-source, end-to-end KOL-mapping platform specifically for Chile. The available building blocks support the KOL Radar approach, but they do not replace it: public literature/network tools cover publications, while Chilean trial sources cover part of the local trial landscape.

### Core limitations to design for

1. Name and affiliation disambiguation is difficult, especially for physicians with several institutions.
2. Public-source coverage is uneven; missing evidence is not evidence of low influence.
3. Trial registries may omit, delay, or inconsistently express investigator and site roles.
4. Congress, guideline, and society information is fragmented and often requires source-by-source collection.
5. Public activity is a proxy for scientific visibility, not proof of peer respect, clinical quality, procedure volume, or an appropriate engagement decision.

### Additional recommended source layers

| Source | Proposed use | Main limitation or safeguard |
| --- | --- | --- |
| [PubMed / NCBI E-utilities](https://www.ncbi.nlm.nih.gov/home/develop/api/) | Primary source for peer-reviewed biomedical publications and stable publication identifiers. | Relevance and author identity must be evaluated; a name match alone is insufficient. |
| [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-about-studies/learn-about-api) | Structured retrieval of trial records, study status, locations, and publicly named roles. | Refresh data and capture its timestamp; investigator/site fields are incomplete or inconsistent for some studies. |
| [ORCID public API](https://info.orcid.org/documentation/integration-and-api-faq/) | Strongest available public anchor for researcher identity and public works/affiliations. | ORCID coverage is voluntary and incomplete; lack of an ORCID must not exclude a physician. |
| [ROR](https://ror.org/registry/) | Normalize institutional names and distinguish research organisations, hospitals, and related entities. | It resolves organisations, not a physician's employment status or a main workplace. |
| [SciELO Chile](https://search.scielo.org/?lang=es) | Complement PubMed with Chilean and regional scientific literature. | Must be deduplicated with PubMed/DOI records and assessed for disease relevance. |
| Official society, congress, university, and hospital pages | Verify guidelines, programme roles, speaking, education, and leadership signals. | Fragmented, often non-standardised, and subject to change; retain source URL and retrieval date for each item. |
| [MINSAL National Cancer Plan](https://www.minsal.cl/wp-content/uploads/2024/03/Plan-Nacional-de-Cancer-2022-2027.pdf) | Context and a starting point for identifying national oncology governance and scientific bodies. | It is contextual evidence, not a KOL ranking source. |

## 14. Current KOL Radar page — observed limitations

The current page is a strong visual demo and already provides search, entity-type filters, cards, a network view, a detail sheet, individual source links, and a basic point breakdown. Its present limitations against the approved product charter are:

1. **Fixed demo scope:** it is presented as a lung-cancer demo rather than a user-defined Chile search brief with explicit disease, territory, and time-window inputs.
2. **Score too coarse:** it currently exposes a simple point total and a short breakdown; it does not represent the seven agreed evidence dimensions, category caps, recency treatment, or separate confidence.
3. **Weak priority explanation:** a user cannot yet understand why one physician outranks another through a complete, comparable evidence ledger.
4. **No dedicated MSL triage output:** high, medium, and monitor priority tiers; shortlist creation; comparison; and an interview-ready research summary are absent.
5. **Limited filtering for the target workflow:** there is no visible first-class filtering by Chilean region, evidence period, evidence type, priority tier, clinical-trial role, or source confidence.
6. **Affiliation model not explicit enough:** the product must visibly support several source-dated affiliations and distinguish observed, current, and main affiliations without assumptions.
7. **Evidence pipeline not visible:** refresh cadence, source coverage, identity matching rules, unresolved-match handling, and data-quality status are not yet communicated as product behaviour.
8. **Local signal coverage not yet integrated:** official Chilean trial, guideline, society, congress, university, and hospital sources are not yet represented as a defined source layer.
9. **Prototype safeguards remain unresolved:** the page states that the data are sample data, human review is pending, and a correction/removal channel is not defined.

## 15. Remaining work

### Product and evidence design

1. Finalise point rules, caps, and recency/confidence treatment for every one of the seven evidence dimensions.
2. Define the source-by-source evidence pipeline, identity-resolution rules, refresh policy, and human-review queue.
3. Define the Chile lung-cancer first-pass search flow and its interview-ready output.
4. Specify the affiliation and institution data model for multiple, dated relationships.

### Page changes after the design is approved

5. Replace the current score with an explainable priority and confidence presentation.
6. Add the filters, tiers, evidence ledger, shortlist, and comparison experience required by the agreed MSL workflow.
7. Add source freshness, methodology, correction, and removal handling.

### Validation

8. Run a bounded Chile lung-cancer example and compare it with a careful manual research pass.
9. Test the workflow with an MSL or MSL candidate and record where it saves time or introduces ambiguity.

### Draft initial search filters

| Filter | Draft value | Why it matters |
| --- | --- | --- |
| Candidate type | Physicians only | Keeps the first mapping aligned with the defined MSL interview scenario. |
| Clinical focus | Lung cancer | Establishes relevance for publications and clinical trials. |
| Territory | Chile | Enables a country-level view of relevant physicians, institutions, and geographic concentration of activity. |
| Evidence period | Last five years, with older evidence retained as historical context | Prevents old activity from looking equivalent to current activity. |
| Evidence threshold | At least one relevant, source-linked public signal | Keeps every candidate traceable while allowing the score to express depth of evidence. |

## Decision log

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-08-15 | Start from the user objective before adding features. | The design should serve a defensible MSL research workflow, not just display available data. |
| 2026-08-15 | Treat the score as a transparent evidence-based priority signal. | “Opinion leader” contains subjective and non-public elements that cannot be responsibly reduced to a definitive label. |
| 2026-08-15 | The first output is a prioritized shortlist of research candidates. | The ranking helps allocate research time; it does not make a final KOL designation or engagement decision. |
| 2026-08-15 | Prioritize people; use institutions as a linked context layer. | A doctor may work across several institutions. The product must retain multiple evidence-backed affiliations instead of assigning a single workplace by assumption. |
| 2026-08-15 | Limit the first use case to physicians. | Keep the initial scope focused on the MSL interview-mapping scenario; do not add non-physician profiles to the ranked candidate list. |
| 2026-08-15 | Use Chile as the territory for the first use case. | The initial map should compare relevant activity across the country, not only Santiago. |
| 2026-08-15 | Allow a physician with one relevant public signal into the map; use ranking to set research priority. | Inclusion preserves coverage, while the priority tier prevents a single signal from being treated as a strong contact candidate. |
| 2026-08-15 | Keep procedure volume outside the initial score. | Public evidence is too uneven to compare fairly; show it only as source-linked supplementary context when available. |
