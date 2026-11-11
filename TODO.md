# To do

## Urgent fixes

1. [x] Render ADS title MathML, such as the inline formula in `2026PhRvD.114b3023D`, instead of showing its markup literally.
2. [x] Highlight only the target-linked citation marker; do not highlight matching digits elsewhere in passages or math.

## Browser UI

1. [x] Let `workflow.py` send progress messages through a callback while preserving CLI output.
2. [x] Add an early progress message before the workflow's slow initial steps.
3. [x] Add a local web server with a form for the target bibcode and row limit; run the existing workflow in the background.
4. [x] Show live progress in the page by polling the server.
5. [x] Display the completed report or links to its saved HTML and JSON files.
6. [ ] Check the browser flow locally, then run a live ADS check manually.
7. [x] Reset page whenever a new bibcode is entered
8. [x] Display report on the same page.
9. [ ] Animate 'Processing...' message; perhaps blink or fade-out/in?
10. [ ] Add 'save report' button
11. [ ] Add 'stop run' button
12. [ ] 'View citation report' redudant now tha report loads automatically on same page
13. [ ] Bug: page reload clears bibcode field and resets row limit, but does not clear progress or report
14. [ ] Add console.log() feedback for developers

## Other open tasks, in priority order

1. [ ] Handle case where 0 citing papers are found; no need to write a report.
2. [ ] Review pipeline structure based on Mermaid diagram in PIPELINE.md; can we simplify?
3. [ ] Reconsider removing per-bibcode HTML reports: JSON plus the viewer avoids duplicate output, but standalone HTML is easy to share and open in any browser.
4. [ ] Discuss whether the agent can be made platform-agnostic, i.e. use other LLMs.
5. [ ] Consider using bold text instead of highlighting target citations in HTML passages.

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
- [x] Highlight target-linked citation labels in HTML passages.
