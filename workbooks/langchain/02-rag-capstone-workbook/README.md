# RAG Capstone Workbook

> **Status:** Draft offline guided RAG reference, chapters 00–13. Author-verified controls and extractive answers; unpiloted. No live-model quality or deployment claim.

Start with [W-RAG-00](00-project-brief.md), then [W-RAG-01](01-project-setup.md). One [evolving project](retrieval-lab/README.md) supplies retrieval mechanics, SQLite-backed tenant/role/freshness controls, reviewed extractive answers/citations, deletion and a separate retrieval/answer evaluation. [SG-RAG-00](../../../study-guides/retrieval-foundations/README.md) and [SG-RAG-01](../../../study-guides/retrieval-foundations/permissions-and-grounding.md) provide concepts. The [independent recall-notice brief](12-capstone-challenges.md) changes format, identity scope and time applicability; [public criteria](13-revision-and-assessment.md) require ownership evidence.

This completes the module's offline reference route, not program graduation. Learned embeddings, free-form model quality, production identity, distributed consistency and deployment require separate implementation/evidence. The original Fernwood framework route remains available; QuickCart is the new reference domain. Reference-only folders are outside this build.

Follow the [study guide style](../../../docs/study-guide-style.md).

## Chapters

- [W-RAG-00 — Project Brief](00-project-brief.md)
- [W-RAG-01 — Project Setup](01-project-setup.md)
- [W-RAG-02 — Architecture](02-architecture.md)
- [W-RAG-03 — Document Loading](03-document-loading.md)
- [W-RAG-04 — Chunking](04-chunking.md)
- [W-RAG-05 — Embeddings and Indexing](05-embeddings-and-indexing.md)
- [Knowledge lifecycle: publish, revise, quarantine and delete](retrieval-lab/knowledge-lifecycle.md) - after W-RAG-05; 150-195 minutes, same offline package
- [W-RAG-06 — Retrieval](06-retrieval.md)
- [W-RAG-07 — Answer Generation](07-answer-generation.md)
- [W-RAG-08 — User Interface](08-user-interface.md)
- [W-RAG-09 — Evaluation and Testing](09-evaluation-and-testing.md)
- [W-RAG-10 — Debugging and Improvements](10-debugging-and-improvements.md)
- [W-RAG-11 — Production Considerations](11-production-considerations.md)
- [W-RAG-12 — Capstone Challenges](12-capstone-challenges.md)
- [W-RAG-13 — Revision and Assessment](13-revision-and-assessment.md)

## Stage defense practice

Use the linked [W-DEFEND-01 stage prompts](../../defense/practice-bank.md#p05--retrieval-permissions-and-grounding) for coding, debugging, design and a drafted stakeholder update. Select within this module's existing reflection/independent-practice time; do not add every prompt as compulsory workload. Record prediction, actual checks, help used and evidence limits. Public practice/reference replay is distinct from the final reviewer-selected unseen modification.

**Optional retrieval depth:** [bounded reranking comparison](retrieval-lab/reranking-comparison.md), after W-RAG-06 and grounded permission controls. 60-90 min; fixes a diagnosed authored-fixture miss but exposes a regression and retains a reject-adoption decision. No learned-reranker or compulsory-depth claim.
