from sqlalchemy import (
    and_,
    case,
    cast,
    func,
    Integer,
    literal,
    select,
    String,
    union_all,
)
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col
from utils.database.date_helpers import (
    current_date_yyyymmdd_minus_one,
    date_minus_one,
    right_n_chars,
    yyyymmdd_to_date,
)


def build_ingeschreven_persoon(engine, source_schema=None):
    """Build the INGESCHREVENPERSOON select for Centric Burgerzaken (BRP)."""

    base_tables = [
        "gba_tbwnhis",
        "gba_tvbpakt",
        "gba_tprsgeg",
        "gba_tarcgeg",
        "gba_tnamreg",
        "gba_tinsgeg",
        "gba_tovlakt",
        "gba_tgbaadr",
        "gba_tselbst",
    ]
    metadata = reflect_tables(engine, source_schema, base_tables)

    tbwnhis = get_table(
        metadata,
        source_schema,
        "gba_tbwnhis",
        required_cols=["rsys_prs", "rsys_adr", "dwon_bgn", "dwon_end", "kwon_end"],
    )
    tvbpakt = get_table(
        metadata,
        source_schema,
        "gba_tvbpakt",
        required_cols=["rsys_prs", "rsys_adr", "dadrh", "kigs_gzr"],
    )
    tprsgeg = get_table(
        metadata,
        source_schema,
        "gba_tprsgeg",
        required_cols=["rsys_prs", "ireg", "rsys_nam", "kgsl"],
    )
    tarcgeg = get_table(
        metadata,
        source_schema,
        "gba_tarcgeg",
        required_cols=["rsys_prs", "ireg", "rsys_nam", "kgsl"],
    )
    tnamreg = get_table(
        metadata,
        source_schema,
        "gba_tnamreg",
        required_cols=[
            "rsys_nam",
            "radm",
            "rsofi",
            "nvoor",
            "nvlr_gba",
            "nvgsl",
            "ngsl",
        ],
    )
    tinsgeg = get_table(
        metadata,
        source_schema,
        "gba_tinsgeg",
        required_cols=["rsys_prs", "kops", "dops"],
    )
    tovlakt = get_table(
        metadata,
        source_schema,
        "gba_tovlakt",
        required_cols=["rsys_prs", "dovl_gba"],
    )
    tgbaadr = get_table(
        metadata,
        source_schema,
        "gba_tgbaadr",
        required_cols=[
            "rsys_adr",
            "nid_nad",
            "nstr",
            "rhs",
            "nhsr_lt",
            "khsr_tv",
            "khsr_ad",
            "kpst_num",
            "kpst_alf",
            "nwpl_nm",
        ],
    )
    tselbst = get_table(
        metadata,
        source_schema,
        "gba_tselbst",
        required_cols=["rsys_prs", "khfd_bew"],
    )

    adreshistorie = (
        select(
            col(tbwnhis, "rsys_prs").label("rsys_prs"),
            col(tbwnhis, "rsys_adr").label("rsys_adr"),
            col(tbwnhis, "dwon_bgn").label("dwon_bgn"),
            col(tbwnhis, "dwon_end").label("dwon_end"),
            col(tbwnhis, "kwon_end").label("kwon_end"),
            literal(None).label("kigs_gzr"),
        )
        .where(col(tbwnhis, "dwon_end") >= literal(20000101))
        .where(col(tbwnhis, "kwon_end") != literal("F"))
        .union_all(
            select(
                col(tvbpakt, "rsys_prs"),
                col(tvbpakt, "rsys_adr"),
                col(tvbpakt, "dadrh").label("dwon_bgn"),
                literal(None).label("dwon_end"),
                literal(None).label("kwon_end"),
                col(tvbpakt, "kigs_gzr"),
            )
        )
        .cte("adreshistorie")
    )

    dwon_bgn_str = cast(adreshistorie.c.dwon_bgn, String(16))
    dwon_bgn_int = cast(adreshistorie.c.dwon_bgn, Integer)
    adjusted_dwon_bgn = case(
        (
            right_n_chars(engine, dwon_bgn_str, 2) == literal("00"),
            dwon_bgn_int + literal(1),
        ),
        (
            func.length(dwon_bgn_str) != literal(8),
            func.coalesce(
                adreshistorie.c.dwon_end, current_date_yyyymmdd_minus_one(engine)
            ),
        ),
        else_=adreshistorie.c.dwon_bgn,
    )

    address_order_value = func.coalesce(adreshistorie.c.dwon_end, literal(99991231))
    name_join_key = func.coalesce(col(tprsgeg, "rsys_nam"), col(tarcgeg, "rsys_nam"))

    adreshistorienetto = (
        select(
            adreshistorie.c.rsys_prs.label("rsys_prs"),
            col(tnamreg, "radm").label("radm"),
            adreshistorie.c.rsys_adr.label("rsys_adr"),
            adjusted_dwon_bgn.label("dwon_bgn"),
            adreshistorie.c.dwon_end.label("dwon_end"),
            adreshistorie.c.kwon_end.label("kwon_end"),
            adreshistorie.c.kigs_gzr.label("kigs_gzr"),
            func.row_number()
            .over(
                partition_by=[
                    col(tnamreg, "radm"),
                    func.coalesce(adreshistorie.c.dwon_bgn, literal(19000101)),
                ],
                order_by=address_order_value.desc(),
            )
            .label("volgnr"),
            func.max(adreshistorie.c.rsys_prs)
            .over(
                partition_by=col(tnamreg, "radm"),
                order_by=address_order_value.desc(),
            )
            .label("rsys_prs_max"),
        )
        .select_from(adreshistorie)
        .outerjoin(
            tprsgeg,
            and_(
                col(tprsgeg, "rsys_prs") == adreshistorie.c.rsys_prs,
                col(tprsgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(
            tarcgeg,
            and_(
                col(tarcgeg, "rsys_prs") == adreshistorie.c.rsys_prs,
                col(tarcgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(tnamreg, col(tnamreg, "rsys_nam") == name_join_key)
        .cte("adreshistorienetto")
    )

    gezins_rows = [
        (1, "Hoofd gezin zonder kind(eren)", "M"),
        (2, "Hoofd gezin met kind(eren)", "M"),
        (3, "Ouder met kind(eren)", "M of V"),
        (4, "Echtgenote binnen gezin", "V"),
        (5, "Kind", "M of V"),
        (6, "Alleenstaand/Samenwonend", "M of V"),
        (7, "Hoofd partnerrelatie", "M of V"),
        (8, "Hoofd huwelijk gelijk geslacht", "M of V "),
    ]
    gezins_selects = [
        select(
            literal(num).label("nummer"),
            literal(omschr).label("omschrijving"),
            literal(gesl).label("geslacht"),
        )
        for num, omschr, gesl in gezins_rows
    ]
    with_gezinsrelatie = union_all(*gezins_selects).cte("with_gezinsrelatie")

    lead_dwon_bgn = func.lead(adreshistorienetto.c.dwon_bgn).over(
        partition_by=col(tnamreg, "radm"),
        order_by=adreshistorienetto.c.dwon_bgn,
    )

    begindatum_verblijf = yyyymmdd_to_date(engine, adreshistorienetto.c.dwon_bgn)
    einddatum_raw = yyyymmdd_to_date(engine, adreshistorienetto.c.dwon_end)
    einddatum_verblijf = case(
        (
            lead_dwon_bgn == adreshistorienetto.c.dwon_end,
            date_minus_one(engine, einddatum_raw),
        ),
        else_=einddatum_raw,
    )

    nummeraanduiding_id = case(
        (
            col(tgbaadr, "nid_nad").isnot(None),
            cast(col(tgbaadr, "nid_nad"), String(32)).concat(literal("-BAG")),
        ),
        else_=literal(None),
    )

    locatiebeschrijving = func.concat(
        col(tgbaadr, "nstr"),
        literal(" "),
        col(tgbaadr, "rhs"),
        func.coalesce(func.concat(literal(" "), col(tgbaadr, "nhsr_lt")), literal("")),
        func.coalesce(func.concat(literal(" "), col(tgbaadr, "khsr_tv")), literal("")),
        func.coalesce(func.concat(literal(" "), col(tgbaadr, "khsr_ad")), literal("")),
        func.coalesce(func.concat(literal(" "), col(tgbaadr, "kpst_num")), literal("")),
        func.coalesce(col(tgbaadr, "kpst_alf"), literal("")),
        func.coalesce(func.concat(literal(","), col(tgbaadr, "nwpl_nm")), literal("")),
    )

    reden_einde_bewoning = case(
        (adreshistorienetto.c.kwon_end == literal("W"), literal("Adreswijziging")),
        (adreshistorienetto.c.kwon_end == literal("V"), literal("Vertrokken")),
        (adreshistorienetto.c.kwon_end == literal("O"), literal("Overleden")),
        (
            adreshistorienetto.c.kwon_end == literal("F"),
            literal("Foutieve persoonslijst"),
        ),
        (adreshistorienetto.c.kwon_end == literal("U"), literal("Vernummering")),
        (adreshistorienetto.c.kwon_end == literal("A"), literal("Vernaming")),
        (
            adreshistorienetto.c.kwon_end == literal("M"),
            literal("Ministerieel besluit"),
        ),
        (adreshistorienetto.c.kwon_end == literal("X"), literal("Geactualiseerd")),
        else_=literal(None),
    )

    reden_opschort_bijhouding = case(
        (
            col(tinsgeg, "kops") == literal("E"),
            literal("Geemigreerd op ").concat(col(tinsgeg, "dops")),
        ),
        (
            col(tinsgeg, "kops") == literal("M"),
            literal("Ministerieel besluit op ").concat(col(tinsgeg, "dops")),
        ),
        (
            col(tinsgeg, "kops") == literal("F"),
            literal("Foute PL op ").concat(col(tinsgeg, "dops")),
        ),
        (
            col(tinsgeg, "kops") == literal("."),
            literal("Opschorting onbekend op ").concat(col(tinsgeg, "dops")),
        ),
        (
            col(tovlakt, "dovl_gba").isnot(None),
            literal("Overleden op ").concat(col(tovlakt, "dovl_gba")),
        ),
        else_=col(tinsgeg, "kops"),
    )

    hoofdbewoner = case(
        (col(tselbst, "khfd_bew") == literal(1), literal("Ja")),
        (col(tselbst, "khfd_bew") == literal(0), literal("Nee")),
        else_=literal(None),
    )

    final_query = (
        select(
            col(tnamreg, "radm").label("IngeschrevenPersoonId"),
            col(tnamreg, "radm").label("A_nummer"),
            begindatum_verblijf.label("BegindatumVerblijf"),
            adreshistorienetto.c.dwon_bgn.label("dwon_bgn"),
            einddatum_verblijf.label("EinddatumVerblijf"),
            col(tinsgeg, "dops").label("dd_opschort_bijhouding"),
            case(
                (col(tinsgeg, "kops") == literal("E"), col(tinsgeg, "dops")),
                else_=literal(None),
            ).label("datumvertrekuitnederland"),
            nummeraanduiding_id.label("NummeraanduidingID"),
            reden_einde_bewoning.label("RedenEindeBewoning"),
            adreshistorienetto.c.kigs_gzr.label("gezinstrelatieid"),
            with_gezinsrelatie.c.omschrijving.label("gezinsrelatie"),
            locatiebeschrijving.label("locatiebeschrijving"),
            reden_opschort_bijhouding.label("Reden_Opschort_bijhouding"),
            hoofdbewoner.label("Hoofdbewoner"),
            cast(col(tnamreg, "radm"), String(64))
            .concat(literal("-BRP"))
            .label("DWH_IDENTIFICATIE"),
        )
        .select_from(tinsgeg)
        .outerjoin(tovlakt, col(tovlakt, "rsys_prs") == col(tinsgeg, "rsys_prs"))
        .outerjoin(
            tprsgeg,
            and_(
                col(tprsgeg, "rsys_prs") == col(tinsgeg, "rsys_prs"),
                col(tprsgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(
            tarcgeg,
            and_(
                col(tarcgeg, "rsys_prs") == col(tinsgeg, "rsys_prs"),
                col(tarcgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(tnamreg, col(tnamreg, "rsys_nam") == name_join_key)
        .join(
            adreshistorienetto,
            and_(
                adreshistorienetto.c.rsys_prs_max == col(tinsgeg, "rsys_prs"),
                adreshistorienetto.c.volgnr == literal(1),
            ),
        )
        .outerjoin(tgbaadr, col(tgbaadr, "rsys_adr") == adreshistorienetto.c.rsys_adr)
        .outerjoin(
            with_gezinsrelatie,
            with_gezinsrelatie.c.nummer == adreshistorienetto.c.kigs_gzr,
        )
        .outerjoin(
            tselbst,
            and_(
                col(tselbst, "rsys_prs") == col(tinsgeg, "rsys_prs"),
                adreshistorienetto.c.dwon_end.is_(None),
            ),
        )
        .where(func.coalesce(col(tinsgeg, "kops"), literal("x")) != literal("F"))
    )

    return final_query


__query_exports__ = {
    "INGESCHREVENPERSOON": build_ingeschreven_persoon,
}
