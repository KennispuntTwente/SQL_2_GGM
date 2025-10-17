from sqlalchemy import MetaData, select, and_, or_, func, cast, Date, literal
from utils.database.naming import normalize_table_name, get_table_column, normalize_column_name

def build_beschikte_voorziening(engine, source_schema=None):
    table_names = [
        normalize_table_name("wvind_b", kind="source"),
        normalize_table_name("szregel", kind="source"),
        normalize_table_name("wvbesl", kind="source"),
        normalize_table_name("wvdos", kind="source"),
        normalize_table_name("abc_refcod", kind="source"),
    ]

    metadata = MetaData()
    metadata.reflect(bind=engine, schema=source_schema, only=table_names)

    fq_names = [f"{source_schema + '.' if source_schema else ''}{n}" for n in table_names]
    wvind_b, szregel, wvbesl, wvdos, abc_refcod = (metadata.tables[name] for name in fq_names)

    return (
        select(
            # Timestamps normalized to Date; labels normalized as destination
            cast(
                func.timezone('Europe/Amsterdam', func.timezone('UTC', get_table_column(wvind_b, 'dd_eind'))),
                Date,
            ).label(normalize_column_name('datumeinde', kind='destination')),
            cast(
                func.timezone('Europe/Amsterdam', func.timezone('UTC', get_table_column(wvind_b, 'dd_begin'))),
                Date,
            ).label(normalize_column_name('datumstart', kind='destination')),

            get_table_column(wvind_b, 'volume').label(
                normalize_column_name('omvang', kind='destination')
            ),
            get_table_column(wvind_b, 'status_indicatie').label(
                normalize_column_name('status', kind='destination')
            ),
            func.concat(
                get_table_column(wvind_b, 'besluitnr'),
                get_table_column(wvind_b, 'volgnr_ind')
            ).label(normalize_column_name('beschikte_voorziening_id', kind='destination')),

            # 'redeneinde' (kept as NULL for now) – label normalized
            literal(None).label(normalize_column_name('redeneinde', kind='destination')),

            # Add missing columns as cast(null) with normalized destination labels
            literal(None).label(normalize_column_name('code', kind='destination')),
            literal(None).label(normalize_column_name('datumeindeoorspronkelijk', kind='destination')),
            literal(None).label(normalize_column_name('eenheid_enum_id', kind='destination')),
            literal(None).label(normalize_column_name('frequentie_enum_id', kind='destination')),
            literal(None).label(normalize_column_name('heeft_leveringsvorm_293_id', kind='destination')),
            literal(None).label(normalize_column_name('is_voorziening_voorziening_id', kind='destination')),
            literal(None).label(normalize_column_name('leveringsvorm_287_enum_id', kind='destination')),
            literal(None).label(normalize_column_name('toegewezen_product_toewijzing_id', kind='destination')),
            literal(None).label(normalize_column_name('wet_enum_id', kind='destination')),
        )
        .select_from(wvind_b)
    .outerjoin(szregel, get_table_column(wvind_b, 'kode_regeling') == get_table_column(szregel, 'kode_regeling'))
    .outerjoin(wvbesl, get_table_column(wvind_b, 'besluitnr') == get_table_column(wvbesl, 'besluitnr'))
        .outerjoin(
            wvdos,
            and_(
                get_table_column(wvind_b, 'besluitnr') == get_table_column(wvdos, 'besluitnr'),
                get_table_column(wvind_b, 'volgnr_ind') == get_table_column(wvdos, 'volgnr_ind'),
            ),
        )
        .outerjoin(
            abc_refcod,
            and_(
                get_table_column(wvdos, 'kode_reden_einde_voorz') == get_table_column(abc_refcod, 'code'),
                or_(
                    and_(
                        get_table_column(szregel, 'omschryving') == "JEUGDWET",
                        get_table_column(abc_refcod, 'domein') == "JZG_REDEN_EINDE_PRODUCT",
                    ),
                    and_(
                        get_table_column(szregel, 'omschryving') != "JEUGDWET",
                        get_table_column(abc_refcod, 'domein') == "WVRTEIND",
                    ),
                ),
            ),
        )
    )

# Map target table names to query builder functions
__query_exports__ = {
    "BESCHIKTE_VOORZIENING": build_beschikte_voorziening,
}
