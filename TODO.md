# To do

## Open tasks, in priority order

1. [ ] Discuss whether users should be able to run the pipeline through a browser UI.
2. [ ] Review pipeline structure based on Mermaid diagram in PIPELINE.md; can we simplify?
3. [ ] Reconsider removing per-bibcode HTML reports: JSON plus the viewer avoids duplicate output, but standalone HTML is easy to share and open in any browser.
4. [ ] Discuss whether the agente can be made platform-agnostic, i.e. use other LLMs
5. [ ] Highlight target paper (author+year) in HTML citation passages

## Completed

- [x] Add a personality section to `AGENTS.md`.
- [x] Open ADS paper links in a new tab (`target="_blank"`) and add `rel="noopener"`.
- [x] Investigate missing citing papers for `2024MNRAS.535..187T`; use it as a test case.
- [x] Discuss summary variability and record compact generation metadata for provenance.
- [x] Add an acknowledgement to `README.md` for Aeon.
- [x] Add an architecture sketch of the citation agent to `PIPELINE.md`.
- [x] Generate and display a summary of the target paper from its ADS abstract.
- [x] Save generated HTML reports in a `citation_reports` folder.
- [x] Save workflow results as per-bibcode JSON files alongside HTML reports.
- [x] Create a template-driven JSON report viewer with file-picker and local-server loading.
- [x] Render accents, special characters, and LaTeX math correctly in both HTML report paths.
- [x] Discuss and implement guardrails for citation attribution, evidence use, and data flow.
