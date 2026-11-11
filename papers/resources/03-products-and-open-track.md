# Track 3: Epistemic Products and Track 4: Open Track

Checked against the linked sources on 9 November 2026. The notes cover five Track 3 and eight Track 4 sources, including items grouped under a single bullet in the sprint brief.

## Track 3: Epistemic Products

### Design Sketches: Angels-on-the-Shoulder

- Sprint link: [Forethought, Design Sketches: Angels-on-the-Shoulder](https://www.forethought.org/research/design-sketches-angels-on-the-shoulder), by Owen Cotton-Barratt, Lizka Vaintrob, Oly Sourbut, and Rose Hadshar (29 January 2026).
- Source and reading depth: original author page read, including the five design sketches, feasibility notes, and project starters. The sprint page calls this the track’s core menu.
- Local copy: [PDF](../design-sketches-angels-on-the-shoulder.pdf) · [text](../text/design-sketches-angels-on-the-shoulder.txt) · [Forethought download](https://www.forethought.org/api/article/design-sketches-angels-on-the-shoulder.pdf).
- Summary: the authors sketch aligned recommendation feeds, personalized learning, deep decision briefings, reflection scaffolds, and guardian agents. Each system aims to help users make choices they would endorse on reflection. The article stresses incentives, long-term feedback, reliability, privacy, crisis handling, and adoption. It is a design agenda, not an evaluation of deployed products.
- Project angle: use the deep-briefing model to show an evidence-lineage tree beside each claim. A handoff that repeats the same originating evidence should not raise the displayed corroboration count. Compare that interface with a simple “three agents agree” display and measure whether users can identify duplicated provenance.

### Guardian Angels: LLM Personalization for Productivity and Security

- Sprint link: [Gwern, Guardian Angels: LLM Personalization for Productivity and Security](https://gwern.net/guardian-angel) (2026).
- Source and reading depth: original author essay read. It develops a personal agent that learns a user’s preferences, spots likely mistakes or security risks, and intervenes at moments of action.
- Local copy: author-hosted HTML only. No public PDF of this essay was located; no local PDF or extracted text.
- Summary: the proposal gives a personal LLM agent persistent context and permission to warn or act when it detects choices that conflict with the user’s interests. The potential value depends on reliable personalization and useful timing. Persistent monitoring and delegated intervention create privacy, autonomy, false-positive, and security risks. The essay is conceptual and does not report an empirical product test.
- Project angle: build a “corroboration guardian” that flags repeated evidence across agent handoffs before a user accepts an apparently convergent recommendation. Test interventions at the decision point, with a reversible explanation and one-click provenance inspection.

### OpenAI’s GPT-4o sycophancy postmortem

- Sprint link: [OpenAI, Sycophancy in GPT-4o: What happened and what we’re doing about it](https://openai.com/index/sycophancy-in-gpt-4o/) (29 April 2025).
- Source and reading depth: original OpenAI postmortem read. It reports a product update rollback and the company’s account of the cause and response.
- Local copy: official HTML source only; no public report PDF found. No local PDF or extracted text.
- Summary: OpenAI says a GPT-4o update became overly affirming after the team weighted short-term user feedback too heavily and failed to account for longer-term interaction effects. It rolled back the update and described changes to training, evaluation, user feedback, and personalization. This is a first-party incident account, not a controlled causal study; it does not publish the affected model outputs, a measured harm rate, or a counterfactual evaluation.
- Project angle: separate agreement from evidence-grounded corroboration in user-facing evaluations. A model can sound supportive and mutually confirmed while its sources share one origin. Pair preference ratings with provenance accuracy and later user endorsement.

### Sycophantic AI Decreases Prosocial Intentions and Promotes Dependence

- Sprint link: [Cheng et al., Science (2026)](https://www.science.org/doi/10.1126/science.aec8352) · [2026 publication record](https://pubmed.ncbi.nlm.nih.gov/41886588/) · [arXiv preprint, first posted in 2025](https://arxiv.org/abs/2510.01395).
- Source and reading depth: arXiv manuscript checked against the sprint citation and the Science DOI. Abstract, method overview, and reported results read.
- Local copy: [PDF](../sycophantic-ai-decreases-prosocial-intentions-promotes-dependence.pdf), downloaded from arXiv and signature-checked as PDF. Extracted text: [TXT](../text/sycophantic-ai-decreases-prosocial-intentions-promotes-dependence.txt).
- Summary: the authors test social sycophancy, meaning affirmation of users’ actions and self-image, across 11 models and in two preregistered experiments with 1,604 participants. Sycophantic advice increased self-rated rightness and lowered willingness to repair interpersonal conflicts compared with non-sycophantic advice; participants also rated the affirming responses more favorably and expressed greater trust and return intent. The paper reports effects in both hypothetical scenarios and live chats about participants’ real past conflicts.
- Method, result, limits: model-output comparisons use personal-advice prompts and compare model affirmation with human advice judgments. The user studies randomize exposure to sycophantic versus non-sycophantic responses; one study uses a live interaction about a real conflict. The authors report lower repair intentions and higher conviction of being right in both studies. Outcomes are immediate self-reports, not observed relationship repair or durable behavior. Human comparison responses reflect crowdsourced Reddit and professional advice, with stated cultural and sampling limits. This directly motivates testing whether repeated agents add perceived independent authority to the same validating claim.
- Project angle: hold the advice content constant, then vary whether two agents share a source or independently retrieve evidence. Measure perceived correctness, trust, repair intention, and whether users notice duplicated evidence. Keep these outcomes distinct: preference does not establish decision quality.

### AI Can Help Humans Find Common Ground in Democratic Deliberation

- Sprint link: [Tessler et al., Science (2024)](https://www.science.org/doi/10.1126/science.adq2852); [Google DeepMind publication record](https://deepmind.google/research/publications/65220/).
- Source and reading depth: publisher page was checked and blocked full-text retrieval with HTTP 403. The author organization’s publication page and public full-text mirror were read. The mirror reproduces the nine-page Science article and DOI; the official Science download link remains the preferred source.
- Local copy: [public full-text PDF mirror](../ai-can-help-humans-find-common-ground.pdf), downloaded and signature-checked. [Extracted text](../text/ai-can-help-humans-find-common-ground.txt). The mirror is hosted by Rivista AI, rather than the publisher or authors; its provenance is recorded here.
- Summary: the Habermas Machine iteratively drafts and revises group statements from participants’ private opinions and critiques. Across structured experiments totaling 5,734 participants, participants preferred AI-written statements to human-mediator statements, rated them as clearer and more informative, and often converged toward a shared position. The authors also examine minority-view inclusion and a virtual UK citizens’ assembly.
- Method, result, limits: participants submit individual positions, rank candidate statements, critique a selected statement, then rank revised statements. In a 75-group human-mediator comparison involving 439 participants, Habermas Machine statements were preferred 56% to 44%. The paper reports reduced group division after AI-mediated deliberation and analyzes whether minority critiques appear in final statements. Outcomes are statement preference, ratings, and measured stance movement in structured discussion. They do not establish durable consensus, equal influence in high-stakes disputes, or that convergence is normatively good. Population representativeness and good-faith participation remain important conditions.
- Project angle: this is adjacent work on group synthesis and changing beliefs. Sharpen the distinction by tracking evidence lineage rather than opinion representation. Ask whether a group statement’s apparent support comes from separate observations or duplicated claims relayed across participants’ agents. Add a provenance audit to the synthesis loop and compare convergence, perceived consensus, and minority evidence retention.

## Track 4: Open Track, deployment, adoption, and impact

### The AI Adoption Gap: Preparing the US Government for Advanced AI

- Sprint link: [Forethought, The AI Adoption Gap](https://www.forethought.org/research/the-ai-adoption-gap) (Lizka Vaintrob, April 2025); [official PDF](https://www.forethought.org/research/the-ai-adoption-gap.pdf).
- Source and reading depth: original report page and 24-page PDF read. The report frames government adoption as a dual challenge: building capacity while managing the risks of rushed or unsafe integration.
- Local copy: [PDF](../ai-adoption-gap-us-government.pdf), downloaded from Forethought and signature-checked. [Extracted text](../text/ai-adoption-gap-us-government.txt).
- Summary: the report argues that US federal adoption is falling behind private-sector use and recommends strengthening technical capacity, procurement, infrastructure, and security. It also proposes contingency planning for prolonged state-capacity weakness or crisis-driven adoption.
- Method and limits: policy analysis synthesizing adoption indicators, government constraints, and risk scenarios. It is not a causal evaluation of procurement reforms, and the adoption-gap estimate is illustrative rather than a directly measured common scale. It centers US federal institutions.
- Project angle: treat provenance visibility as adoption infrastructure. Interview or audit whether agencies can distinguish independent support from copied assertions in AI-generated briefs, and map which records, procurement controls, and audit obligations make that check usable.

### AI Tools for Existential Security

- Sprint link: [Forethought, AI Tools for Existential Security](https://www.forethought.org/research/ai-tools-for-existential-security) (Lizka Vaintrob and Owen Cotton-Barratt, 2025); [appendices](https://www.forethought.org/research/appendices-to-ai-tools-for-existential-security).
- Source and reading depth: original essay and appendices checked. The essay’s epistemic-application section and adoption recommendations were read.
- Local copy: [PDF](../ai-tools-for-existential-security.pdf) · [text](../text/ai-tools-for-existential-security.txt) · [Forethought download](https://www.forethought.org/api/article/ai-tools-for-existential-security.pdf). The linked appendices remain on the author site.
- Summary: the authors map AI applications that could help people anticipate and respond to existential risks, with special emphasis on forecasting, coordination, and the barriers that delay beneficial use. They argue for preparing datasets, complementary tooling, institutional support, and adoption pathways before the relevant capabilities arrive. The work offers a strategic argument and application taxonomy; empirical tests of those applications are absent.
- Project angle: test whether provenance explanations help an epistemic product earn appropriate trust. Adoption metrics should distinguish users’ willingness to try a feature from whether they can audit its evidence and improve their decision.

### Did the Roll-Out of Community Notes Reduce Engagement With Misinformation on X/Twitter?

- Sprint link: [Chuai et al., arXiv:2307.07960](https://arxiv.org/abs/2307.07960), accepted at CSCW 2024.
- Source and reading depth: arXiv abstract and version history checked; full PDF downloaded and text-extracted. The paper uses platform-wide observational data and quasi-experimental designs.
- Local copy: [PDF](../community-notes-reduce-misinformation-engagement.pdf), from arXiv and signature-checked. [Extracted text](../text/community-notes-reduce-misinformation-engagement.txt).
- Summary: the paper examines whether the Community Notes rollout reduced engagement with misleading posts. Difference-in-differences and regression-discontinuity analyses find more notes, especially on posts by verified users with many followers, but no evidence of a significant overall reduction in engagement. The authors suggest notes may arrive too late to affect early, highly viral diffusion.
- Method, result, limits: the authors analyze the platform’s fact-check notes and corresponding source posts, using DiD and RDD. These designs improve on simple before-and-after comparisons, though causal interpretation depends on the identifying assumptions and the product rollout context. The paper’s result is about engagement with covered posts during the studied rollout, not the accuracy of every note or every platform’s fact-checking system.
- Project angle: Community Notes shows the difference between producing a signal and delivering it in time to change a decision. A provenance tool should be tested for both correctness and timing: does lineage arrive before a user relies on the apparent multi-agent consensus?

### Community Notes public dataset

- Sprint link: [X Community Notes data download guide](https://communitynotes.x.com/guide/en/under-the-hood/download-data).
- Source and reading depth: original data guide checked. It describes downloadable notes, ratings, and status history. The guide was reachable, though its text was not exposed to the browser text extractor.
- Local copy: data remains at the source; no dataset downloaded. The resource is a changing data product, so use the current source files and record retrieval date and schema version.
- Project angle: construct provenance clusters for claims and notes, then test whether source overlap predicts apparent cross-agent agreement. Keep note status and rating history as time-varying signals rather than treating final helpfulness as information available at the original posting time.

### Accuracy of Forecasts in Strategic Intelligence

- Sprint link: [Mandel and Barnes, PNAS (2014)](https://www.pnas.org/doi/10.1073/pnas.1406138111); [public PDF copy hosted by UC Berkeley Statistics](https://www.stat.berkeley.edu/users/aldous/157/Papers/mandel-barnes.pdf).
- Source and reading depth: PNAS DOI was checked; publisher page returned HTTP 403. The complete six-page article PDF was read from the Berkeley-hosted copy, including methods and results.
- Local copy: [PDF](../accuracy-forecasts-strategic-intelligence.pdf), downloaded from the public copy and signature-checked. [Extracted text](../text/accuracy-forecasts-strategic-intelligence.txt).
- Summary: the study scores 1,514 numeric forecasts extracted from roughly six years of one strategic assessment unit’s intelligence reports. Forecast discrimination and calibration were strong overall. Forecasts were mainly underconfident, especially on harder or policy-important questions; post-hoc recalibration reduced underconfidence.
- Method, result, limits: retrospective scoring of forecasts against resolved outcomes, with discrimination, calibration, and subgroup analyses. The sample comes from one unit and historical period, so it cannot establish present-day performance across intelligence organizations or forecasts that were not expressed numerically. The paper is a useful model for outcome-based audit, with a reminder that apparent precision depends on forecast resolution and inclusion rules.
- Project angle: apply scoring-rule discipline to claims of multi-agent corroboration. Record the forecast before additional agents see prior outputs, then score both calibration and independence judgments. Report when repeated agreement adds no independent evidence.

### FutureSearch

- Sprint link: [FutureSearch research and public writings](https://futuresearch.ai/writings/); [evaluation resources](https://evals.futuresearch.ai/); [published forecasts guide](https://futuresearch.ai/docs/guides/).
- Source and reading depth: original research index and linked evaluation/guidance pages checked. The writing page exposes live, updated and graded forecasts. Evals page describes forecasting and pastcasting benchmarks; guide documents practical forecast workflows.
- Local copy: web resources only. The sprint points to organizational writeups rather than a single report; no single PDF to archive.
- Summary: FutureSearch presents an operating forecasting organization with public forecasts, grading, and evaluation materials. Its examples offer a route to inspect how forecasts are framed, updated, and resolved. The landing pages do not amount to an independent evaluation of the organization’s forecasting skill.
- Project angle: compare agent handoff chains with independent forecaster runs. Preserve forecast timestamps and source exposure, then use later resolutions to test whether apparent team agreement predicts accuracy after controlling for evidence overlap.

### Swift Centre

- Sprint link: [Swift Centre](https://www.swiftcentre.org/); [research index](https://www.swiftcentre.org/research.html).
- Source and reading depth: original organization site and research page checked. The site describes scenario-based papers, living situation monitors combining horizon scanning, scenario analysis, causal modeling, and forecasting, plus organizational forecasting and capability-building. The sprint’s link is to the organization rather than a single named report.
- Local copy: web resources only. No single report PDF is specified by the sprint link. Public papers can be archived individually if a project selects one.
- Summary: Swift Centre presents forecasting as a client-facing decision process, including expert-network forecasts and live platform access for questions and clarification. Its site describes service design and selected engagements, not a full independent performance evaluation.
- Project angle: use the client-facing process as a template for provenance capture: who generated each forecast, which evidence they saw, what clarifications crossed the boundary, and whether later forecasters remained independent.

### Sentinel

- Sprint link: [Sentinel](https://sentinel-team.org/); [public track record](https://sentinel-team.org/track-record); [latest briefings](https://blog.sentinel-team.org/).
- Source and reading depth: original site checked. Sentinel describes its work as public, judged forecasting and curates weekly risk coverage. The home page links to the track record and recent briefs.
- Local copy: web resources only. The sprint gives the organization landing page, not one report; no PDF is specified.
- Summary: Sentinel positions itself as a global-catastrophe forecasting group with public track record and briefings. The landing page is not enough to assess accuracy. Review the track-record page for resolution criteria, forecast volume, selection policy, and comparison baselines before treating it as evidence of performance.
- Project angle: use a public track record as a template for an auditable multi-agent ledger. Include the resolved claim, initial timestamp, evidence lineage, handoff graph, and scoring rule so repeated reports of one source cannot inflate the apparent sample size.

## Project synthesis: when handoffs look like corroboration

The closest empirical anchors are the social-sycophancy experiments, the Habermas Machine deliberation study, and Mandel and Barnes’s forecast scoring. They answer different questions: how affirmation shifts a user’s immediate judgments, how iterative synthesis can change group statements and positions, and how forecasts can be scored against outcomes. None tests whether repeated agent handoffs create false impressions of independent corroboration.

A tight sprint study could generate matched synthetic cases with two evidence conditions. In the shared-lineage condition, multiple agents receive the same source claim through different handoffs. In the independent condition, agents obtain separately sourced observations. Hold claim content, agent count, and interface constant. Ask participants to estimate confidence and source independence, then provide the provenance graph and elicit revised estimates. Score confidence against the case ground truth and track whether users can distinguish repeated transmission from separate evidence. The primary contrast is the change in confidence caused by visible agent agreement when evidence lineage is shared rather than independent. This makes the project a direct provenance-and-decision eval, with a product-facing interface test.

## Access and file inventory

Seven PDFs and their plain-text extracts are stored locally for these tracks. The Habermas Machine article comes from the public Rivista AI mirror because the direct Science download returned HTTP 403. Gwern’s essay, the OpenAI postmortem, the live dataset guide, and the forecasting organization pages remain linked online.

