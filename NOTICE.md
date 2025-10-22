# Project Notice – ggmpilot

Copyright © 2025 Kennispunt Twente and contributors
https://github.com/KennispuntTwente/ggmpilot

The ggmpilot project provides an open-source pipeline to load application data into the Gemeentelijk Gegevensmodel (GGM). It includes a source→staging transfer layer and a staging→silver mapping layer implemented with SQLAlchemy, plus example configurations, smoke tests, and developer tooling.

This work includes:
- application source code (Python) for data transfer and query-based mappings;
- configuration examples, Docker/Compose scripts, tests, and documentation;
- a curated selection of GGM DDLs and related materials under their original upstream licenses (see `ggm/` and `ggm_selectie/`).

## License terms

1) Project code and documentation

The code and documentation authored for ggmpilot (e.g., `source_to_staging`, `staging_to_silver`, `utils`, `docker`, `tests`, and top-level docs) are licensed under the GNU Affero General Public License, version 3 (AGPL-3.0). See the `LICENSE.md` file at the repository root for the full text.

2) GGM artifacts from the Municipality of Delft

The GGM materials included in this repository (see `ggm/` and any derived selections under `ggm_selectie/`) are third-party content from:
https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel

They are licensed by their original authors as follows:
- Core information model (UML files/repositories, JSON schemas, tables and definitions): European Union Public Licence (EUPL), version 1.2 — https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
- Visual elements (figures, diagrams, explanatory documentation): Creative Commons Attribution 4.0 International (CC-BY 4.0) — https://creativecommons.org/licenses/by/4.0/

When redistributing or creating derivatives of these GGM artifacts, comply with the upstream licenses and attribution requirements (e.g., “Source: Gemeentelijk Gegevensmodel, Municipality of Delft”).
