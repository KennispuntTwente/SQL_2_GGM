from sqlalchemy import (
    and_,
    case,
    cast,
    func,
    Integer,
    literal,
    select,
    String,
)
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col
from utils.database.date_helpers import (
    date_minus_one,
    right_n_chars,
    yyyymmdd_to_date,
)


def build_verblijfsadres_ingeschreven_persoon(engine, source_schema=None):
    """Build the VERBLIJFSADRESINGESCHREVENPERSOON select for Centric Burgerzaken (BRP)."""

    base_tables = [
        "gba_tbwnhis",
        "gba_tvbpakt",
        "gba_tdomein",
        "gba_tinsgeg",
        "gba_tprsgeg",
        "gba_tarcgeg",
        "gba_tnamreg",
        "gba_tgbaadr",
    ]
    metadata = reflect_tables(engine, source_schema, base_tables)

    tbwnhis = get_table(
        metadata,
        source_schema,
        "gba_tbwnhis",
        required_cols=[
            "rsys_prs",
            "rsys_adr",
            "dwon_bgn",
            "dwon_end",
            "kwon_end",
            "rvlg",
        ],
    )
    tvbpakt = get_table(
        metadata,
        source_schema,
        "gba_tvbpakt",
        required_cols=["rsys_prs", "rsys_adr", "dadrh", "kadrf"],
    )
    tdomein = get_table(
        metadata,
        source_schema,
        "gba_tdomein",
        required_cols=["kode", "kveld", "oms"],
    )
    tinsgeg = get_table(
        metadata,
        source_schema,
        "gba_tinsgeg",
        required_cols=["rsys_prs", "kops", "dtoe_gba"],
    )
    tprsgeg = get_table(
        metadata,
        source_schema,
        "gba_tprsgeg",
        required_cols=["rsys_prs", "ireg", "rsys_nam"],
    )
    tarcgeg = get_table(
        metadata,
        source_schema,
        "gba_tarcgeg",
        required_cols=["rsys_prs", "ireg", "rsys_nam"],
    )
    tnamreg = get_table(
        metadata,
        source_schema,
        "gba_tnamreg",
        required_cols=["rsys_nam", "radm"],
    )
    tgbaadr = get_table(
        metadata,
        source_schema,
        "gba_tgbaadr",
        required_cols=[
            "rsys_adr",
            "nid_vbo",
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

    # Alias for tdomein for adresherkomst join (kadrf)
    tdomein_adrf = tdomein.alias("tdomein_adrf")
    # Alias for tdomein for kwon_end join
    tdomein_wone = tdomein.alias("tdomein_wone")

    # CTE: adreshistorie
    adreshistorie = (
        select(
            col(tbwnhis, "rsys_prs").label("rsys_prs"),
            col(tbwnhis, "rsys_adr").label("rsys_adr"),
            col(tbwnhis, "dwon_bgn").label("dwon_bgn"),
            col(tbwnhis, "dwon_end").label("dwon_end"),
            col(tbwnhis, "kwon_end").label("kwon_end"),
            col(tbwnhis, "rvlg").label("rvlg"),
            literal("Woonadres").label("adresherkomst"),
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
                literal(-1).label("rvlg"),
                tdomein_adrf.c.oms.label("adresherkomst"),
            )
            .select_from(tvbpakt)
            .outerjoin(
                tdomein_adrf,
                and_(
                    tdomein_adrf.c.kode == col(tvbpakt, "kadrf"),
                    tdomein_adrf.c.kveld == literal("KADRF"),
                ),
            )
        )
        .cte("adreshistorie")
    )

    # CTE: adreshistorienetto
    adreshistorienetto = (
        select(
            adreshistorie.c.rsys_prs.label("rsys_prs"),
            adreshistorie.c.rsys_adr.label("rsys_adr"),
            adreshistorie.c.dwon_bgn.label("dwon_bgn"),
            adreshistorie.c.dwon_end.label("dwon_end"),
            tdomein_wone.c.oms.label("redeneindebewoning"),
            adreshistorie.c.rvlg.label("rvlg"),
            func.min(adreshistorie.c.rvlg)
            .over(
                partition_by=[
                    adreshistorie.c.rsys_prs,
                    adreshistorie.c.rsys_adr,
                    adreshistorie.c.dwon_bgn,
                ]
            )
            .label("minrvlg"),
            adreshistorie.c.adresherkomst.label("adresherkomst"),
        )
        .select_from(adreshistorie)
        .outerjoin(
            tdomein_wone,
            and_(
                tdomein_wone.c.kode == adreshistorie.c.kwon_end,
                tdomein_wone.c.kveld == literal("KWON_END"),
            ),
        )
        .cte("adreshistorienetto")
    )

    name_join_key = func.coalesce(col(tprsgeg, "rsys_nam"), col(tarcgeg, "rsys_nam"))

    # date helpers
    dwon_bgn_str = cast(adreshistorienetto.c.dwon_bgn, String(16))
    adjusted_datum_begin = case(
        (
            right_n_chars(engine, dwon_bgn_str, 2) == literal("00"),
            yyyymmdd_to_date(
                engine, cast(adreshistorienetto.c.dwon_bgn, Integer) + literal(1)
            ),
        ),
        (
            func.length(dwon_bgn_str) != literal(8),
            yyyymmdd_to_date(engine, col(tinsgeg, "dtoe_gba")),
        ),
        else_=yyyymmdd_to_date(engine, adreshistorienetto.c.dwon_bgn),
    )

    lead_dwon_bgn = func.lead(adreshistorienetto.c.dwon_bgn).over(
        partition_by=col(tnamreg, "radm"),
        order_by=adreshistorienetto.c.dwon_bgn,
    )
    einddatum_raw = yyyymmdd_to_date(engine, adreshistorienetto.c.dwon_end)
    datum_einde = case(
        (
            lead_dwon_bgn == adreshistorienetto.c.dwon_end,
            date_minus_one(engine, einddatum_raw),
        ),
        else_=einddatum_raw,
    )

    bagid_adresseerbaarobject = case(
        (
            col(tgbaadr, "nid_vbo").isnot(None),
            cast(col(tgbaadr, "nid_vbo"), String(32)).concat(literal("-BAG")),
        ),
        else_=literal(None),
    )

    beschrijving_locatie = func.concat(
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

    postcode = func.concat(col(tgbaadr, "kpst_num"), col(tgbaadr, "kpst_alf"))

    ingeschreven_persoon_id = cast(col(tnamreg, "radm"), String(32)).concat(
        literal("-BRP")
    )

    verblijfsadres_id = (
        cast(adreshistorienetto.c.rsys_prs, String(32))
        .concat(literal("-"))
        .concat(cast(adreshistorienetto.c.rsys_adr, String(32)))
        .concat(literal("-"))
        .concat(cast(adreshistorienetto.c.dwon_bgn, String(16)))
    )

    dwh_identificatie = verblijfsadres_id.concat(literal("-BRP"))

    final_query = (
        select(
            adreshistorienetto.c.adresherkomst.label("AdresHerkomst"),
            adjusted_datum_begin.label("datumBegin"),
            datum_einde.label("datumEinde"),
            bagid_adresseerbaarobject.label("BAGID_AdreseerbaarObject"),
            adreshistorienetto.c.redeneindebewoning.label("RedenEindeBewoning"),
            beschrijving_locatie.label("beschrijvingLocatie"),
            col(tgbaadr, "rhs").label("huisnummer"),
            col(tgbaadr, "nhsr_lt").label("huisletter"),
            col(tgbaadr, "khsr_tv").label("huisnummetoevoeging"),
            col(tgbaadr, "khsr_ad").label("huisnummeaanduiding"),
            postcode.label("postcode"),
            col(tgbaadr, "nstr").label("straatnaam"),
            col(tgbaadr, "nwpl_nm").label("plaats"),
            ingeschreven_persoon_id.label("IngeschrevenPersoonId"),
            verblijfsadres_id.label("VerblijfsAdresIngeschrevenPersoonId"),
            dwh_identificatie.label("DWH_IDENTIFICATIE"),
            literal("CEN_BRP").label("DWH_BRON"),
            literal(1).label("DWH_ACTUEEL"),
        )
        .select_from(tinsgeg)
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
                adreshistorienetto.c.rsys_prs == col(tinsgeg, "rsys_prs"),
                adreshistorienetto.c.minrvlg == adreshistorienetto.c.rvlg,
            ),
        )
        .outerjoin(tgbaadr, col(tgbaadr, "rsys_adr") == adreshistorienetto.c.rsys_adr)
        .where(func.coalesce(col(tinsgeg, "kops"), literal("x")) != literal("F"))
    )

    return final_query


__query_exports__ = {
    "VERBLIJFSADRESINGESCHREVENPERSOON": build_verblijfsadres_ingeschreven_persoon,
}
