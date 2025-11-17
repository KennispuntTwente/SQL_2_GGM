* Packages/dependencies
Potentially unnecessary or suspect deps; investigate/remove
Update authors for pyproject.toml; description; license; README wiring
Enable build system in pyproject.toml

* OData downloads silently truncate when $count is unavailable
The OData exporter relies on either ROW_LIMIT or a successful count() call to populate remaining. If both are absent (for example when the source does not support $count), remaining stays None. The pagination loop then breaks immediately after the first chunk because the stop condition next_url is None and (remaining is None …) becomes True even though more pages are available; next_url is None whenever the service expects the client to page via $skip/$top. In practice this means only the first page_size rows are ever written for such services.
Fix suggestion: Continue fetching when next_url is None but you’re using skip/top, and only break once the returned page is empty (or when you know you’ve reached the requested row limit).
