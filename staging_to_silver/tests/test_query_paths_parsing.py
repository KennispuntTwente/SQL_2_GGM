# Tests for QUERY_PATHS parsing with semicolons, commas, and quoted paths
# Focuses on handling Windows paths with spaces and various separator combinations
# This ensures custom query directories can be specified reliably across platforms

from staging_to_silver.functions.queries_setup import parse_extra_query_paths


def test_query_paths_parsing_preserves_spaces_and_quotes():
    raw = r'C:\\Data Warehouse\\ggm\\queries;C:\\Users\\Luka\\My Queries; "C:\\Quoted Path\\With Space" , C:\\NoSpace\\Path'
    paths = parse_extra_query_paths(raw)
    assert paths == [
        r"C:\\Data Warehouse\\ggm\\queries",
        r"C:\\Users\\Luka\\My Queries",
        r"C:\\Quoted Path\\With Space",
        r"C:\\NoSpace\\Path",
    ]
    # Ensure no unintended splitting occurred on internal spaces
    for p in paths:
        assert " " in p or p.endswith(
            "Path"
        )  # heuristic sanity check retaining spaces where expected


def test_query_paths_parsing_ignores_empty_tokens():
    raw = ";;  ;  , , C:/A;C:/B"
    paths = parse_extra_query_paths(raw)
    assert paths == ["C:/A", "C:/B"]
