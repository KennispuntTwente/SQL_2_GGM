from sqlalchemy import (
    and_,
    case,
    cast,
    distinct,
    func,
    literal,
    select,
    String,
)
from staging_to_silver.functions.case_helpers import reflect_tables, get_table, col
from utils.database.date_helpers import (
    date_minus_one,
    format_date_yyyymmdd,
    incomplete_date_to_date,
)


def build_huwelijk(engine, source_schema=None):
    """Build the HUWELIJK select for Centric Burgerzaken (BRP)."""

    base_tables = [
        "gba_thuwhis",
        "gba_thuwakt",
        "gba_tovlakt",
        "gba_tinsgeg",
        "gba_tprsgeg",
        "gba_tarcgeg",
        "gba_tnamreg",
        "gba_tdomein",
    ]
    metadata = reflect_tables(engine, source_schema, base_tables)

    thuwhis = get_table(
        metadata,
        source_schema,
        "gba_thuwhis",
        required_cols=[
            "rsys_prs",
            "rvlg_hw",
            "rsys_nam",
            "dhw",
            "dhwo",
            "kakt",
            "khwo",
            "ksrt_vrb",
            "dgld",
            "dopn",
            "ionj",
        ],
    )
    thuwakt = get_table(
        metadata,
        source_schema,
        "gba_thuwakt",
        required_cols=[
            "rsys_prs",
            "rvlg_hw",
            "rsys_nam",
            "dhw",
            "dhwo",
            "kakt",
            "khwo",
            "ksrt_vrb",
            "dgld",
            "dopn",
        ],
    )
    tovlakt = get_table(
        metadata,
        source_schema,
        "gba_tovlakt",
        required_cols=["rsys_prs", "dovl_gba"],
    )
    tinsgeg = get_table(
        metadata,
        source_schema,
        "gba_tinsgeg",
        required_cols=["rsys_prs", "kbst"],
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
    tdomein = get_table(
        metadata,
        source_schema,
        "gba_tdomein",
        required_cols=["kode", "kveld", "oms"],
    )

    # Aliases for different domain joins
    tdomein_rdo = tdomein.alias("tdomein_rdo")
    tdomein_svb = tdomein.alias("tdomein_svb")
    tnamreg_par = tnamreg.alias("tnamreg_par")

    # CTE: basis – union of thuwhis (filtered ionj IS NULL) and thuwakt with overlijden logic
    thuwhis_select = (
        select(
            col(thuwhis, "rsys_prs").label("rsys_prs"),
            col(thuwhis, "rvlg_hw").label("rvlg_hw"),
            col(thuwhis, "rsys_nam").label("rsys_nam"),
            col(thuwhis, "dhw").label("dhw"),
            col(thuwhis, "dhwo").label("dhwo"),
            col(thuwhis, "kakt").label("kakt"),
            col(thuwhis, "khwo").label("khwo"),
            col(thuwhis, "ksrt_vrb").label("ksrt_vrb"),
            col(thuwhis, "dgld").label("dgld"),
            col(thuwhis, "dopn").label("dopn"),
        )
        .select_from(thuwhis)
        .join(
            thuwakt,
            and_(
                col(thuwakt, "rsys_prs") == col(thuwhis, "rsys_prs"),
                col(thuwakt, "rvlg_hw") == col(thuwhis, "rvlg_hw"),
            ),
        )
        .where(col(thuwhis, "ionj").is_(None))
    )

    dovl_gt_dhw = and_(
        col(tovlakt, "dovl_gba").isnot(None),
        col(tovlakt, "dovl_gba") > func.coalesce(col(thuwakt, "dhw"), literal(0)),
    )
    thuwakt_select = (
        select(
            col(thuwakt, "rsys_prs").label("rsys_prs"),
            col(thuwakt, "rvlg_hw").label("rvlg_hw"),
            col(thuwakt, "rsys_nam").label("rsys_nam"),
            col(thuwakt, "dhw").label("dhw"),
            case(
                (
                    and_(col(thuwakt, "dhwo").is_(None), dovl_gt_dhw),
                    col(tovlakt, "dovl_gba"),
                ),
                else_=col(thuwakt, "dhwo"),
            ).label("dhwo"),
            col(thuwakt, "kakt").label("kakt"),
            case(
                (
                    and_(col(thuwakt, "dhwo").is_(None), dovl_gt_dhw),
                    literal("OVL"),
                ),
                else_=col(thuwakt, "khwo"),
            ).label("khwo"),
            col(thuwakt, "ksrt_vrb").label("ksrt_vrb"),
            col(thuwakt, "dgld").label("dgld"),
            col(thuwakt, "dopn").label("dopn"),
        )
        .select_from(thuwakt)
        .outerjoin(tovlakt, col(tovlakt, "rsys_prs") == col(thuwakt, "rsys_prs"))
    )

    basis = thuwhis_select.union_all(thuwakt_select).cte("basis")

    # CTE: omzetting – min(dgld) where kakt[3] = 'H'
    omzetting = (
        select(
            basis.c.rsys_prs.label("rsys_prs"),
            basis.c.rvlg_hw.label("rvlg_hw"),
            func.min(basis.c.dgld).label("min_dgld"),
        )
        .where(func.substr(basis.c.kakt, 3, 1) == literal("H"))
        .group_by(basis.c.rsys_prs, basis.c.rvlg_hw)
        .cte("omzetting")
    )

    # CTE: with_thuwhis – compute rvlg_volg, omzetting flag, date conversions
    rvlg_volg_no_omz = func.lpad(
        cast(basis.c.rvlg_hw + literal(1), String(3)), 3, literal("0")
    )
    rvlg_volg_omz = func.lpad(
        func.concat(
            cast(omzetting.c.rvlg_hw + literal(1), String(3)),
            cast(basis.c.rvlg_hw + literal(1), String(3)),
        ),
        3,
        literal("0"),
    )
    rvlg_volg = case(
        (omzetting.c.rvlg_hw.is_(None), rvlg_volg_no_omz),
        else_=rvlg_volg_omz,
    )
    omzetting_flag = case(
        (omzetting.c.rvlg_hw.is_(None), literal("Nee")),
        else_=literal("Ja"),
    )

    with_thuwhis = (
        select(
            basis.c.rsys_prs.label("rsys_prs"),
            basis.c.rvlg_hw.label("rvlg_hw"),
            rvlg_volg.label("rvlg_volg"),
            omzetting_flag.label("omzetting"),
            basis.c.rsys_nam.label("rsys_nam"),
            incomplete_date_to_date(engine, basis.c.dhw).label("dhw"),
            incomplete_date_to_date(engine, basis.c.dhwo).label("dhwo"),
            basis.c.kakt.label("kakt"),
            basis.c.khwo.label("khwo"),
            basis.c.ksrt_vrb.label("ksrt_vrb"),
            basis.c.dgld.label("h_dgld"),
            incomplete_date_to_date(engine, basis.c.dgld).label("dgld"),
            incomplete_date_to_date(engine, basis.c.dopn).label("dopn"),
        )
        .select_from(basis)
        .outerjoin(
            omzetting,
            and_(
                omzetting.c.rsys_prs == basis.c.rsys_prs,
                omzetting.c.rvlg_hw == basis.c.rvlg_hw,
                omzetting.c.min_dgld <= basis.c.dgld,
            ),
        )
        .cte("with_thuwhis")
    )

    # CTE: pre_huwelijk – first_value to flatten mutations
    fv_kwargs = {
        "partition_by": [with_thuwhis.c.rsys_prs, with_thuwhis.c.rvlg_volg],
        "order_by": with_thuwhis.c.dopn.desc(),
    }
    # SQLAlchemy doesn't have ignore_nulls; we use first_value and rely on coalesce in data, acceptable approximation

    pre_huwelijk = (
        select(
            distinct(
                with_thuwhis.c.rsys_prs,
            ),
            with_thuwhis.c.rvlg_hw,
            with_thuwhis.c.rvlg_volg,
            func.first_value(with_thuwhis.c.rsys_nam)
            .over(**fv_kwargs)
            .label("rsys_nam"),
            func.first_value(with_thuwhis.c.dhw).over(**fv_kwargs).label("dhw"),
            func.first_value(with_thuwhis.c.dhwo).over(**fv_kwargs).label("dhwo"),
            func.first_value(with_thuwhis.c.kakt).over(**fv_kwargs).label("kakt"),
            func.first_value(with_thuwhis.c.khwo).over(**fv_kwargs).label("khwo"),
            func.first_value(with_thuwhis.c.ksrt_vrb)
            .over(**fv_kwargs)
            .label("ksrt_vrb"),
            func.first_value(with_thuwhis.c.omzetting)
            .over(**fv_kwargs)
            .label("omzetting"),
            func.first_value(with_thuwhis.c.dgld).over(**fv_kwargs).label("dgld"),
            func.first_value(with_thuwhis.c.dopn).over(**fv_kwargs).label("dopn"),
        )
        .select_from(with_thuwhis)
        .distinct()
        .cte("pre_huwelijk")
    )

    name_join_key = func.coalesce(col(tprsgeg, "rsys_nam"), col(tarcgeg, "rsys_nam"))

    lead_omzetting = func.lead(pre_huwelijk.c.omzetting).over(
        partition_by=[pre_huwelijk.c.rsys_prs, pre_huwelijk.c.rvlg_hw],
        order_by=pre_huwelijk.c.dgld,
    )
    lead_dhw = func.lead(pre_huwelijk.c.dhw).over(
        partition_by=[pre_huwelijk.c.rsys_prs, pre_huwelijk.c.rvlg_hw],
        order_by=pre_huwelijk.c.dgld,
    )

    datum_ontbinding = case(
        (lead_omzetting == literal("Ja"), date_minus_one(engine, lead_dhw)),
        else_=pre_huwelijk.c.dhwo,
    )

    reden_ontbinding = case(
        (lead_omzetting == literal("Ja"), literal("Omzetting")),
        else_=tdomein_rdo.c.oms,
    )

    partner_id = case(
        (
            tnamreg_par.c.radm.isnot(None),
            cast(tnamreg_par.c.radm, String(32)).concat(literal("-BRP")),
        ),
        else_=literal(None),
    )

    ingeschreven_persoon_id = cast(col(tnamreg, "radm"), String(32)).concat(
        literal("-BRP")
    )

    huwelijk_id = func.concat(
        func.greatest(col(tnamreg, "rsys_nam"), tnamreg_par.c.rsys_nam),
        literal("-"),
        func.least(col(tnamreg, "rsys_nam"), tnamreg_par.c.rsys_nam),
        literal("-"),
        func.coalesce(format_date_yyyymmdd(engine, pre_huwelijk.c.dhw), literal("x")),
    )

    dwh_identificatie = func.concat(
        cast(pre_huwelijk.c.rsys_prs, String(32)),
        literal("-"),
        cast(pre_huwelijk.c.rsys_nam, String(32)),
        literal("-"),
        pre_huwelijk.c.rvlg_volg,
        literal("-BRP"),
    )

    final_query = (
        select(
            pre_huwelijk.c.rvlg_hw.label("VolgnummerVerbintenis"),
            pre_huwelijk.c.rsys_prs.label("rsys_prs"),
            pre_huwelijk.c.dhw.label("DatumVerbintenis"),
            col(tinsgeg, "kbst").label("kbst"),
            col(tovlakt, "dovl_gba").label("dovl_gba"),
            datum_ontbinding.label("DatumOntbinding"),
            pre_huwelijk.c.kakt.label("Aktenummer"),
            reden_ontbinding.label("RedenOntbinding"),
            tdomein_svb.c.oms.label("SoortVerbintenis"),
            pre_huwelijk.c.dgld.label("Datumgeldigvanaf"),
            pre_huwelijk.c.dopn.label("DatumOpname"),
            partner_id.label("IngeschrevenPersoonId_partner"),
            ingeschreven_persoon_id.label("IngeschrevenPersoonId"),
            huwelijk_id.label("HuwelijkId"),
            dwh_identificatie.label("DWH_IDENTIFICATIE"),
        )
        .select_from(pre_huwelijk)
        .outerjoin(tinsgeg, col(tinsgeg, "rsys_prs") == pre_huwelijk.c.rsys_prs)
        .outerjoin(tovlakt, col(tovlakt, "rsys_prs") == pre_huwelijk.c.rsys_prs)
        .outerjoin(
            tprsgeg,
            and_(
                col(tprsgeg, "rsys_prs") == pre_huwelijk.c.rsys_prs,
                col(tprsgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(
            tarcgeg,
            and_(
                col(tarcgeg, "rsys_prs") == pre_huwelijk.c.rsys_prs,
                col(tarcgeg, "ireg") == literal("A"),
            ),
        )
        .outerjoin(tnamreg, col(tnamreg, "rsys_nam") == name_join_key)
        .outerjoin(
            tdomein_rdo,
            and_(
                tdomein_rdo.c.kode == pre_huwelijk.c.khwo,
                tdomein_rdo.c.kveld == literal("KHWO"),
            ),
        )
        .outerjoin(tnamreg_par, tnamreg_par.c.rsys_nam == pre_huwelijk.c.rsys_nam)
        .outerjoin(
            tdomein_svb,
            and_(
                tdomein_svb.c.kode == pre_huwelijk.c.ksrt_vrb,
                tdomein_svb.c.kveld == literal("KSRT_VRB"),
            ),
        )
    )

    return final_query


__query_exports__ = {
    "HUWELIJK": build_huwelijk,
}
