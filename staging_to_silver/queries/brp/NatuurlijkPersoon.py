from sqlalchemy import and_, cast, func, literal, select, String
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col
from utils.database.date_helpers import format_bsn


def build_natuurlijk_persoon(engine, source_schema=None):
    """Build the NATUURLIJKPERSOON select for Centric Burgerzaken (BRP)."""

    base_tables = [
        "gba_tbwnhis",
        "gba_tvbpakt",
        "gba_tprsgeg",
        "gba_tarcgeg",
        "gba_tnamreg",
        "gba_tinsgeg",
        "gba_tovlakt",
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
        required_cols=["rsys_prs", "kops"],
    )
    tovlakt = get_table(
        metadata,
        source_schema,
        "gba_tovlakt",
        required_cols=["rsys_prs", "dovl_gba"],
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
        .where(col(tbwnhis, "kwon_end") != literal("F"))
        .where(col(tbwnhis, "dwon_end") >= literal(20000101))
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

    address_order_value = func.coalesce(adreshistorie.c.dwon_end, literal(99991231))
    name_join_key = func.coalesce(col(tprsgeg, "rsys_nam"), col(tarcgeg, "rsys_nam"))

    adreshistorienetto = (
        select(
            adreshistorie.c.rsys_prs.label("rsys_prs"),
            col(tnamreg, "radm").label("radm"),
            adreshistorie.c.rsys_adr.label("rsys_adr"),
            adreshistorie.c.dwon_bgn.label("dwon_bgn"),
            adreshistorie.c.dwon_end.label("dwon_end"),
            adreshistorie.c.kwon_end.label("kwon_end"),
            adreshistorie.c.kigs_gzr.label("kigs_gzr"),
            func.row_number()
            .over(
                partition_by=col(tnamreg, "radm"),
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

    final_query = (
        select(
            col(tnamreg, "radm").label("NatuurlijkPersoonId"),
            format_bsn(engine, col(tnamreg, "rsofi")).label("BSN"),
            col(tnamreg, "dgeb_gba").label("datumgeboren"),
            col(tovlakt, "dovl_gba").label("datumoverlijden"),
            func.coalesce(col(tprsgeg, "kgsl"), col(tarcgeg, "kgsl")).label(
                "Enum_GeslachtID"
            ),
            col(tnamreg, "nvoor").label("Voornamen"),
            col(tnamreg, "nvlr_gba").label("Voorletters"),
            col(tnamreg, "nvgsl").label("Voorvoegselgeslachtsnaam"),
            col(tnamreg, "ngsl").label("Geslachtsnaam"),
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
        .where(func.coalesce(col(tinsgeg, "kops"), literal("x")) != literal("F"))
    )

    return final_query


__query_exports__ = {
    "NATUURLIJKPERSOON": build_natuurlijk_persoon,
}
