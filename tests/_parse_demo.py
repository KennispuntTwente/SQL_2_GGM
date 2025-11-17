from staging_to_silver.functions.queries_setup import parse_extra_query_paths

samples = [
    r'C:\Data Warehouse\ggm\queries;C:\Users\Luka\My Queries; "C:\Quoted Path\\With Space" , C:\NoSpace\Path',
    ";;  ;  , , C:/A;C:/B",
]
for s in samples:
    print("RAW:", s)
    print("PARSED:", parse_extra_query_paths(s))
    print("---")
