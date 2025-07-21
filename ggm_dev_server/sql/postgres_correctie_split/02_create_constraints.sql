ALTER TABLE "Activiteit" ADD CONSTRAINT "PK_Activiteit"
	PRIMARY KEY ("ActiviteitID");

ALTER TABLE "Aomstatus" ADD CONSTRAINT "PK_Aomstatus"
	PRIMARY KEY ("AomstatusID");

ALTER TABLE "Bevinding" ADD CONSTRAINT "PK_Bevinding"
	PRIMARY KEY ("BevindingID");

ALTER TABLE "Boa" ADD CONSTRAINT "PK_Boa"
	PRIMARY KEY ("BoaID");

ALTER TABLE "Combibon" ADD CONSTRAINT "PK_Combibon"
	PRIMARY KEY ("CombibonID");

ALTER TABLE "Enum_beoordelingsoort" ADD CONSTRAINT "PK_Enum_beoordelingsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_heffingsoort" ADD CONSTRAINT "PK_Enum_heffingsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusopenbareactiviteit" ADD CONSTRAINT "PK_Enum_statusopenbareactiviteit"
	PRIMARY KEY ("ID");

ALTER TABLE "Fietsregistratie" ADD CONSTRAINT "PK_Fietsregistratie"
	PRIMARY KEY ("FietsregistratieID");

ALTER TABLE "Grondslag" ADD CONSTRAINT "PK_Grondslag"
	PRIMARY KEY ("GrondslagID");

ALTER TABLE "Heffinggrondslag" ADD CONSTRAINT "PK_Heffinggrondslag"
	PRIMARY KEY ("HeffinggrondslagID");

ALTER TABLE "Heffingsverordening" ADD CONSTRAINT "PK_Heffingsverordening"
	PRIMARY KEY ("HeffingsverordeningID");

ALTER TABLE "Indiener" ADD CONSTRAINT "PK_Indiener"
	PRIMARY KEY ("IndienerID");

ALTER TABLE "Inspectie" ADD CONSTRAINT "PK_Inspectie"
	PRIMARY KEY ("InspectieID");

ALTER TABLE "Kosten" ADD CONSTRAINT "PK_Kosten"
	PRIMARY KEY ("KostenID");

ALTER TABLE "Leges_grondslag" ADD CONSTRAINT "PK_Leges_grondslag"
	PRIMARY KEY ("Leges_grondslagID");

ALTER TABLE "Ligplaatsontheffing" ADD CONSTRAINT "PK_Ligplaatsontheffing"
	PRIMARY KEY ("LigplaatsontheffingID");

ALTER TABLE "Moraanvraagofmelding" ADD CONSTRAINT "PK_Moraanvraagofmelding"
	PRIMARY KEY ("MoraanvraagofmeldingID");

ALTER TABLE "Openbareactiviteit" ADD CONSTRAINT "PK_Openbareactiviteit"
	PRIMARY KEY ("OpenbareactiviteitID");

ALTER TABLE "Precario" ADD CONSTRAINT "PK_Precario"
	PRIMARY KEY ("PrecarioID");

ALTER TABLE "Producttype" ADD CONSTRAINT "PK_Producttype"
	PRIMARY KEY ("ProducttypeID");

ALTER TABLE "Subproducttype" ADD CONSTRAINT "PK_Subproducttype"
	PRIMARY KEY ("SubproducttypeID");

ALTER TABLE "Vaartuig" ADD CONSTRAINT "PK_Vaartuig"
	PRIMARY KEY ("VaartuigID");

ALTER TABLE "Vomaanvraagofmelding" ADD CONSTRAINT "PK_Vomaanvraagofmelding"
	PRIMARY KEY ("VomaanvraagofmeldingID");

ALTER TABLE "Vordering" ADD CONSTRAINT "PK_Vordering"
	PRIMARY KEY ("VorderingID");

ALTER TABLE "Vorderingregel" ADD CONSTRAINT "PK_Vorderingregel"
	PRIMARY KEY ("VorderingregelID");

ALTER TABLE "Vth_aanvraagofmelding" ADD CONSTRAINT "PK_Vth_aanvraagofmelding"
	PRIMARY KEY ("Vth-aanvraagofmeldingID");

ALTER TABLE "Vth_melding" ADD CONSTRAINT "PK_Vth_melding"
	PRIMARY KEY ("Vth-meldingID");

ALTER TABLE "Vthzaak" ADD CONSTRAINT "PK_Vthzaak"
	PRIMARY KEY ("VthzaakID");

ALTER TABLE "Waarneming" ADD CONSTRAINT "PK_Waarneming"
	PRIMARY KEY ("WaarnemingID");

ALTER TABLE "Waboaanvraagofmelding" ADD CONSTRAINT "PK_Waboaanvraagofmelding"
	PRIMARY KEY ("WaboaanvraagofmeldingID");

ALTER TABLE "Woonfraudeaanvraagofmelding" ADD CONSTRAINT "PK_Woonfraudeaanvraagofmelding"
	PRIMARY KEY ("WoonfraudeaanvraagofmeldingID");

ALTER TABLE "Woonoverlastaanvraagofmelding" ADD CONSTRAINT "PK_Woonoverlastaanvraagofmelding"
	PRIMARY KEY ("WoonoverlastaanvraagofmeldingID");

ALTER TABLE "Aomstatus" ADD CONSTRAINT fk_heeft_aanvraagofmelding
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bevinding" ADD CONSTRAINT fk_bevinding_bevinding
	FOREIGN KEY ("BevindingID") REFERENCES "Bevinding" ("BevindingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Combibon" ADD CONSTRAINT "Fk_combibon_vth_melding"
	FOREIGN KEY ("CombibonID") REFERENCES "Vth_melding" ("Vth-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Fietsregistratie" ADD CONSTRAINT "Fk_fietsregistratie_vth_melding"
	FOREIGN KEY ("FietsregistratieID") REFERENCES "Vth_melding" ("Vth-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffinggrondslag" ADD CONSTRAINT "fk_vermeldIn_heffingsverordeni"
	FOREIGN KEY ("HeffingsverordeningID") REFERENCES "Heffingsverordening" ("HeffingsverordeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffinggrondslag" ADD CONSTRAINT fk_heeft_zaaktype
	FOREIGN KEY ("ZaaktypeID") REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffingsverordening" ADD CONSTRAINT "Fk_heffingsverordening_document"
	FOREIGN KEY ("HeffingsverordeningID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Indiener" ADD CONSTRAINT "Fk_indiener_rechtspersoon"
	FOREIGN KEY ("IndienerID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_activiteit_vthzaak" ADD CONSTRAINT "Fk_kp_activiteit_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_activiteit_vthzaak" ADD CONSTRAINT "Fk_kp_activiteit_vthzaak_activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bevinding_inspectie" ADD CONSTRAINT "Fk_kp_bevinding_inspectie_inspectie"
	FOREIGN KEY ("InspectieID") REFERENCES "Inspectie" ("InspectieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bevinding_inspectie" ADD CONSTRAINT "Fk_kp_bevinding_inspectie_bevinding"
	FOREIGN KEY ("BevindingID") REFERENCES "Bevinding" ("BevindingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_grondslag_zaak" ADD CONSTRAINT "Fk_kp_grondslag_zaak_grondslag"
	FOREIGN KEY ("GrondslagID") REFERENCES "Grondslag" ("GrondslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_grondslag_zaak" ADD CONSTRAINT "Fk_kp_grondslag_zaak_zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inspectie_vthzaak" ADD CONSTRAINT "Fk_kp_inspectie_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inspectie_vthzaak" ADD CONSTRAINT "Fk_kp_inspectie_vthzaak_inspectie"
	FOREIGN KEY ("InspectieID") REFERENCES "Inspectie" ("InspectieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kosten_vthzaak" ADD CONSTRAINT "Fk_kp_kosten_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kosten_vthzaak" ADD CONSTRAINT "Fk_kp_kosten_vthzaak_kosten"
	FOREIGN KEY ("KostenID") REFERENCES "Kosten" ("KostenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leges_grondslag_vthzaak" ADD CONSTRAINT "Fk_kp_leges_grondslag_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leges_grondslag_vthzaak" ADD CONSTRAINT "Fk_kp_leges_grondslag_vthzaak_leges_grondslag"
	FOREIGN KEY ("Leges_grondslagID") REFERENCES "Leges_grondslag" ("Leges_grondslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_subproducttype_vthzaak" ADD CONSTRAINT "Fk_kp_subproducttype_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_subproducttype_vthzaak" ADD CONSTRAINT "Fk_kp_subproducttype_vthzaak_subproducttype"
	FOREIGN KEY ("SubproducttypeID") REFERENCES "Subproducttype" ("SubproducttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vordering_vorderingregel" ADD CONSTRAINT "Fk_kp_vordering_vorderingregel_vorderingregel"
	FOREIGN KEY ("VorderingregelID") REFERENCES "Vorderingregel" ("VorderingregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vordering_vorderingregel" ADD CONSTRAINT "Fk_kp_vordering_vorderingregel_vordering"
	FOREIGN KEY ("VorderingID") REFERENCES "Vordering" ("VorderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vordering_vthzaak" ADD CONSTRAINT "Fk_kp_vordering_vthzaak_vthzaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Vthzaak" ("VthzaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vordering_vthzaak" ADD CONSTRAINT "Fk_kp_vordering_vthzaak_vordering"
	FOREIGN KEY ("VorderingID") REFERENCES "Vordering" ("VorderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vth_melding_object" ADD CONSTRAINT "Fk_kp_vth_melding_object_vth_melding"
	FOREIGN KEY ("Vth_meldingID") REFERENCES "Vth_melding" ("Vth-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vth_melding_object" ADD CONSTRAINT "Fk_kp_vth_melding_object_object"
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leges_grondslag" ADD CONSTRAINT fk_heeft_activiteit
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leges_grondslag" ADD CONSTRAINT fk_heeft_grondslag
	FOREIGN KEY ("GrondslagID") REFERENCES "Grondslag" ("GrondslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Moraanvraagofmelding" ADD CONSTRAINT "Fk_moraanvraagofmelding_aanvraagofmelding"
	FOREIGN KEY ("MoraanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Producttype" ADD CONSTRAINT fk_heeft_bedrijfsprocestype
	FOREIGN KEY ("BedrijfsprocestypeID") REFERENCES "Bedrijfsprocestype" ("BedrijfsprocestypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Producttype" ADD CONSTRAINT "fk_heeftProduct_zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Producttype" ADD CONSTRAINT fk_heeft_zaaktype
	FOREIGN KEY ("ZaaktypeID") REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subproducttype" ADD CONSTRAINT "FK_Subproducttype_Producttype"
	FOREIGN KEY ("ProducttypeID") REFERENCES "Producttype" ("ProducttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vaartuig" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vomaanvraagofmelding" ADD CONSTRAINT "Fk_vomaanvraagofmelding_aanvraagofmelding"
	FOREIGN KEY ("VomaanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vorderingregel" ADD CONSTRAINT "FK_Vorderingregel_Kosten"
	FOREIGN KEY ("KostenID") REFERENCES "Kosten" ("KostenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vth_aanvraagofmelding" ADD CONSTRAINT "Fk_vth_aanvraagofmelding_vomaanvraagofmelding"
	FOREIGN KEY ("Vth_aanvraagofmeldingID") REFERENCES "Vomaanvraagofmelding" ("VomaanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vth_melding" ADD CONSTRAINT fk_verbalisant_boa
	FOREIGN KEY ("BoaID") REFERENCES "Boa" ("BoaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vth_melding" ADD CONSTRAINT "Fk_vth_melding_aanvraagofmelding"
	FOREIGN KEY ("Vth_meldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vthzaak" ADD CONSTRAINT fk_heeft_producttype
	FOREIGN KEY ("ProducttypeID") REFERENCES "Producttype" ("ProducttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vthzaak" ADD CONSTRAINT "Fk_vthzaak_zaak"
	FOREIGN KEY ("VthzaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waarneming" ADD CONSTRAINT "Fk_waarneming_vth_melding"
	FOREIGN KEY ("WaarnemingID") REFERENCES "Vth_melding" ("Vth-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waboaanvraagofmelding" ADD CONSTRAINT "Fk_waboaanvraagofmelding_vomaanvraagofmelding"
	FOREIGN KEY ("WaboaanvraagofmeldingID") REFERENCES "Vomaanvraagofmelding" ("VomaanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woonfraudeaanvraagofmelding" ADD CONSTRAINT "Fk_woonfraudeaanvraagofmelding_aanvraagofmelding"
	FOREIGN KEY ("WoonfraudeaanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woonoverlastaanvraagofmelding" ADD CONSTRAINT "Fk_woonoverlastaanvraagofmeldin_aanvraagofmelding"
	FOREIGN KEY ("WoonoverlastaanvraagofmeldinID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagdata" ADD CONSTRAINT "PK_Aanvraagdata"
	PRIMARY KEY ("AanvraagdataID");

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "PK_Aanvraagofmelding"
	PRIMARY KEY ("AanvraagofmeldingID");

ALTER TABLE "Afspraakstatus" ADD CONSTRAINT "PK_Afspraakstatus"
	PRIMARY KEY ("AfspraakstatusID");

ALTER TABLE "Artikel" ADD CONSTRAINT "PK_Artikel"
	PRIMARY KEY ("ArtikelID");

ALTER TABLE "Balieafspraak" ADD CONSTRAINT "PK_Balieafspraak"
	PRIMARY KEY ("BalieafspraakID");

ALTER TABLE "Externebron" ADD CONSTRAINT "PK_Externebron"
	PRIMARY KEY ("ExternebronID");

ALTER TABLE "Formuliersoort" ADD CONSTRAINT "PK_Formuliersoort"
	PRIMARY KEY ("FormuliersoortID");

ALTER TABLE "Formuliersoortveld" ADD CONSTRAINT "PK_Formuliersoortveld"
	PRIMARY KEY ("FormuliersoortveldID");

ALTER TABLE "Klantbeoordeling" ADD CONSTRAINT "PK_Klantbeoordeling"
	PRIMARY KEY ("KlantbeoordelingID");

ALTER TABLE "Klantbeoordelingreden" ADD CONSTRAINT "PK_Klantbeoordelingreden"
	PRIMARY KEY ("KlantbeoordelingredenID");

ALTER TABLE "Mor_aanvraagofmelding" ADD CONSTRAINT "PK_Mor_aanvraagofmelding"
	PRIMARY KEY ("Mor-aanvraagofmeldingID");

ALTER TABLE "Onderwerp" ADD CONSTRAINT "PK_Onderwerp"
	PRIMARY KEY ("OnderwerpID");

ALTER TABLE "Productofdienst" ADD CONSTRAINT "PK_Productofdienst"
	PRIMARY KEY ("ProductofdienstID");

ALTER TABLE "Telefoononderwerp" ADD CONSTRAINT "PK_Telefoononderwerp"
	PRIMARY KEY ("TelefoononderwerpID");

ALTER TABLE "Telefoonstatus" ADD CONSTRAINT "PK_Telefoonstatus"
	PRIMARY KEY ("TelefoonstatusID");

ALTER TABLE "Telefoontje" ADD CONSTRAINT "PK_Telefoontje"
	PRIMARY KEY ("TelefoontjeID");

ALTER TABLE "Aanvraagdata" ADD CONSTRAINT "FK_Aanvraagdata_Formuliersoortveld"
	FOREIGN KEY ("FormuliersoortveldID") REFERENCES "Formuliersoortveld" ("FormuliersoortveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagdata" ADD CONSTRAINT "fk_heeftData_aanvraagofmelding"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "FK_Aanvraagofmelding_Formuliersoort"
	FOREIGN KEY ("FormuliersoortID") REFERENCES "Formuliersoort" ("FormuliersoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "FK_Aanvraagofmelding_Indiener"
	FOREIGN KEY ("IndienerID") REFERENCES "Indiener" ("IndienerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "fk_kanLeidenTot_klantcontact"
	FOREIGN KEY ("KlantcontactID") REFERENCES "Klantcontact" ("KlantcontactID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "FK_Aanvraagofmelding_Rechtspersoon"
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieafspraak" ADD CONSTRAINT "FK_Balieafspraak_Afspraakstatus"
	FOREIGN KEY ("AfspraakstatusID") REFERENCES "Afspraakstatus" ("AfspraakstatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieafspraak" ADD CONSTRAINT "FK_Balieafspraak_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieafspraak" ADD CONSTRAINT "FK_Balieafspraak_Vestigingvanzaakbehandelendeor"
	FOREIGN KEY ("VestigingvanzaakbehandelendeID") REFERENCES "Vestigingvanzaakbehandelendeor" ("VestigingvanzaakbehandelendeorganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieafspraak" ADD CONSTRAINT "FK_Balieafspraak_Zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formuliersoortveld" ADD CONSTRAINT "fk_heeftVelden_formuliersoort"
	FOREIGN KEY ("FormuliersoortID") REFERENCES "Formuliersoort" ("FormuliersoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantbeoordeling" ADD CONSTRAINT fk_doet_betrokkene
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantbeoordeling" ADD CONSTRAINT fk_heeft_zaak
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantbeoordelingreden" ADD CONSTRAINT fk_heeft_klantbeoordeling
	FOREIGN KEY ("KlantbeoordelingID") REFERENCES "Klantbeoordeling" ("KlantbeoordelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_aanvraagofmelding_onderwerp" ADD CONSTRAINT "Fk_kp_aanvraagofmelding_onderwerp_onderwerp"
	FOREIGN KEY ("OnderwerpID") REFERENCES "Onderwerp" ("OnderwerpID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_aanvraagofmelding_onderwerp" ADD CONSTRAINT "Fk_kp_aanvraagofmelding_onderwerp_aanvraagofmelding"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_balieafspraak_productofdien" ADD CONSTRAINT "Fk_kp_balieafspraak_productofdien_productofdienst"
	FOREIGN KEY ("ProductofdienstID") REFERENCES "Productofdienst" ("ProductofdienstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_balieafspraak_productofdien" ADD CONSTRAINT "Fk_kp_balieafspraak_productofdien_balieafspraak"
	FOREIGN KEY ("BalieafspraakID") REFERENCES "Balieafspraak" ("BalieafspraakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_formuliersoort_zaaktype" ADD CONSTRAINT "Fk_kp_formuliersoort_zaaktype_formuliersoort"
	FOREIGN KEY ("FormuliersoortID") REFERENCES "Formuliersoort" ("FormuliersoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_formuliersoort_zaaktype" ADD CONSTRAINT "Fk_kp_formuliersoort_zaaktype_zaaktype"
	FOREIGN KEY ("ZaaktypeID") REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_klantcontact_productofdiens" ADD CONSTRAINT "Fk_kp_klantcontact_productofdiens_productofdienst"
	FOREIGN KEY ("ProductofdienstID") REFERENCES "Productofdienst" ("ProductofdienstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_klantcontact_productofdiens" ADD CONSTRAINT "Fk_kp_klantcontact_productofdiens_klantcontact"
	FOREIGN KEY ("KlantcontactID") REFERENCES "Klantcontact" ("KlantcontactID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_organisatorischeeenheid_kla" ADD CONSTRAINT "Fk_kp_organisatorischeeenheid_kla_klantbeoordeling"
	FOREIGN KEY ("KlantbeoordelingID") REFERENCES "Klantbeoordeling" ("KlantbeoordelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_organisatorischeeenheid_kla" ADD CONSTRAINT "Fk_kp_organisatorischeeenheid_kla_organisatorischeeenheid"
	FOREIGN KEY ("OrganisatorischeeenheidID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_productofdienst_klantbeoord" ADD CONSTRAINT "Fk_kp_productofdienst_klantbeoord_klantbeoordeling"
	FOREIGN KEY ("KlantbeoordelingID") REFERENCES "Klantbeoordeling" ("KlantbeoordelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_productofdienst_klantbeoord" ADD CONSTRAINT "Fk_kp_productofdienst_klantbeoord_productofdienst"
	FOREIGN KEY ("ProductofdienstID") REFERENCES "Productofdienst" ("ProductofdienstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mor_aanvraagofmelding" ADD CONSTRAINT "Fk_mor_aanvraagofmelding_aanvraagofmelding"
	FOREIGN KEY ("Mor_aanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onderwerp" ADD CONSTRAINT "FK_Onderwerp_Onderwerp"
	FOREIGN KEY ("OnderwerpID") REFERENCES "Onderwerp" ("OnderwerpID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Telefoontje" ADD CONSTRAINT fk_heeft_telefoononderwerp
	FOREIGN KEY ("TelefoononderwerpID") REFERENCES "Telefoononderwerp" ("TelefoononderwerpID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Telefoontje" ADD CONSTRAINT "FK_Telefoontje_Telefoonstatus"
	FOREIGN KEY ("TelefoonstatusID") REFERENCES "Telefoonstatus" ("TelefoonstatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Belprovider" ADD CONSTRAINT "PK_Belprovider"
	PRIMARY KEY ("BelproviderID");

ALTER TABLE "Enum_doelgroepenplaatsen" ADD CONSTRAINT "PK_Enum_doelgroepenplaatsen"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_zonesoort" ADD CONSTRAINT "PK_Enum_zonesoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Mulderfeit" ADD CONSTRAINT "PK_Mulderfeit"
	PRIMARY KEY ("MulderfeitID");

ALTER TABLE "Naheffing" ADD CONSTRAINT "PK_Naheffing"
	PRIMARY KEY ("NaheffingID");

ALTER TABLE "Parkeergarage" ADD CONSTRAINT "PK_Parkeergarage"
	PRIMARY KEY ("ParkeergarageID");

ALTER TABLE "Parkeerrecht" ADD CONSTRAINT "PK_Parkeerrecht"
	PRIMARY KEY ("ParkeerrechtID");

ALTER TABLE "Parkeerscan" ADD CONSTRAINT "PK_Parkeerscan"
	PRIMARY KEY ("ParkeerscanID");

ALTER TABLE "Parkeervergunning" ADD CONSTRAINT "PK_Parkeervergunning"
	PRIMARY KEY ("ParkeervergunningID");

ALTER TABLE "Parkeervlak" ADD CONSTRAINT "PK_Parkeervlak"
	PRIMARY KEY ("ParkeervlakID");

ALTER TABLE "Perkeerzone" ADD CONSTRAINT "PK_Perkeerzone"
	PRIMARY KEY ("PerkeerzoneID");

ALTER TABLE "Productgroep" ADD CONSTRAINT "PK_Productgroep"
	PRIMARY KEY ("ProductgroepID");

ALTER TABLE "Productsoort" ADD CONSTRAINT "PK_Productsoort"
	PRIMARY KEY ("ProductsoortID");

ALTER TABLE "Straatsectie" ADD CONSTRAINT "PK_Straatsectie"
	PRIMARY KEY ("StraatsectieID");

ALTER TABLE "Voertuig" ADD CONSTRAINT "PK_Voertuig"
	PRIMARY KEY ("VoertuigID");

ALTER TABLE "Belprovider" ADD CONSTRAINT "Fk_belprovider_leverancier"
	FOREIGN KEY ("BelproviderID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_parkeerrecht_perkeerzone" ADD CONSTRAINT "Fk_kp_parkeerrecht_perkeerzone_perkeerzone"
	FOREIGN KEY ("PerkeerzoneID") REFERENCES "Perkeerzone" ("PerkeerzoneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_parkeerrecht_perkeerzone" ADD CONSTRAINT "Fk_kp_parkeerrecht_perkeerzone_parkeerrecht"
	FOREIGN KEY ("ParkeerrechtID") REFERENCES "Parkeerrecht" ("ParkeerrechtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_parkeervergunning_perkeerzo" ADD CONSTRAINT "Fk_kp_parkeervergunning_perkeerzo_perkeerzone"
	FOREIGN KEY ("PerkeerzoneID") REFERENCES "Perkeerzone" ("PerkeerzoneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_parkeervergunning_perkeerzo" ADD CONSTRAINT "Fk_kp_parkeervergunning_perkeerzo_parkeervergunning"
	FOREIGN KEY ("ParkeervergunningID") REFERENCES "Parkeervergunning" ("ParkeervergunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mulderfeit" ADD CONSTRAINT "FK_Mulderfeit_Voertuig"
	FOREIGN KEY ("VoertuigID") REFERENCES "Voertuig" ("VoertuigID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Naheffing" ADD CONSTRAINT "fk_komtVoortUit_parkeerscan"
	FOREIGN KEY ("ParkeerscanID") REFERENCES "Parkeerscan" ("ParkeerscanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeergarage" ADD CONSTRAINT "Fk_parkeergarage_perkeerzone"
	FOREIGN KEY ("ParkeergarageID") REFERENCES "Perkeerzone" ("PerkeerzoneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerrecht" ADD CONSTRAINT "FK_Parkeerrecht_Belprovider"
	FOREIGN KEY ("BelproviderID") REFERENCES "Belprovider" ("BelproviderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerrecht" ADD CONSTRAINT "FK_Parkeerrecht_Voertuig"
	FOREIGN KEY ("VoertuigID") REFERENCES "Voertuig" ("VoertuigID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerrecht" ADD CONSTRAINT fk_verificatie_parkeerscan
	FOREIGN KEY ("ParkeerscanID") REFERENCES "Parkeerscan" ("ParkeerscanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerrecht" ADD CONSTRAINT fk_resulteert_parkeervergunnin
	FOREIGN KEY ("ParkeervergunningID") REFERENCES "Parkeervergunning" ("ParkeervergunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerscan" ADD CONSTRAINT "FK_Parkeerscan_Voertuig"
	FOREIGN KEY ("VoertuigID") REFERENCES "Voertuig" ("VoertuigID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerscan" ADD CONSTRAINT "FK_Parkeerscan_Parkeervlak"
	FOREIGN KEY ("ParkeervlakID") REFERENCES "Parkeervlak" ("ParkeervlakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeerscan" ADD CONSTRAINT "FK_Parkeerscan_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervergunning" ADD CONSTRAINT fk_soort_productgroep
	FOREIGN KEY ("ProductgroepID") REFERENCES "Productgroep" ("ProductgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervergunning" ADD CONSTRAINT fk_soort_productsoort
	FOREIGN KEY ("ProductsoortID") REFERENCES "Productsoort" ("ProductsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervergunning" ADD CONSTRAINT "FK_Parkeervergunning_Ingezetene"
	FOREIGN KEY ("IngezeteneID") REFERENCES "Ingezetene" ("IngezeteneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervergunning" ADD CONSTRAINT "FK_Parkeervergunning_Rechtspersoon"
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervlak" ADD CONSTRAINT fk_bevat_perkeerzone
	FOREIGN KEY ("PerkeerzoneID") REFERENCES "Perkeerzone" ("PerkeerzoneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Parkeervlak" ADD CONSTRAINT fk_bevat_straatsectie
	FOREIGN KEY ("StraatsectieID") REFERENCES "Straatsectie" ("StraatsectieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Productsoort" ADD CONSTRAINT "FK_Productsoort_Productgroep"
	FOREIGN KEY ("ProductgroepID") REFERENCES "Productgroep" ("ProductgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Straatsectie" ADD CONSTRAINT fk_bevat_perkeerzone
	FOREIGN KEY ("PerkeerzoneID") REFERENCES "Perkeerzone" ("PerkeerzoneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Voertuig" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_aantalGehinderden" ADD CONSTRAINT "PK_Enum_aantalGehinderden"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_hindercategorie" ADD CONSTRAINT "PK_Enum_hindercategorie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_hinderklasse" ADD CONSTRAINT "PK_Enum_hinderklasse"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_stremmingstatus" ADD CONSTRAINT "PK_Enum_stremmingstatus"
	PRIMARY KEY ("ID");

ALTER TABLE "Stremming" ADD CONSTRAINT "PK_Stremming"
	PRIMARY KEY ("StremmingID");

ALTER TABLE "Strooidag" ADD CONSTRAINT "PK_Strooidag"
	PRIMARY KEY ("StrooidagID");

ALTER TABLE "Strooiroute" ADD CONSTRAINT "PK_Strooiroute"
	PRIMARY KEY ("StrooirouteID");

ALTER TABLE "Strooirouteuitvoering" ADD CONSTRAINT "PK_Strooirouteuitvoering"
	PRIMARY KEY ("StrooirouteuitvoeringID");

ALTER TABLE "Verkeersbesluit" ADD CONSTRAINT "PK_Verkeersbesluit"
	PRIMARY KEY ("VerkeersbesluitID");

ALTER TABLE "Verkeerstelling" ADD CONSTRAINT "PK_Verkeerstelling"
	PRIMARY KEY ("VerkeerstellingID");

ALTER TABLE "Vloginfo" ADD CONSTRAINT "PK_Vloginfo"
	PRIMARY KEY ("VloginfoID");

ALTER TABLE "Kp_stremming_wegdeel" ADD CONSTRAINT "Fk_kp_stremming_wegdeel_stremming"
	FOREIGN KEY ("StremmingID") REFERENCES "Stremming" ("StremmingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stremming_wegdeel" ADD CONSTRAINT "Fk_kp_stremming_wegdeel_wegdeel"
	FOREIGN KEY ("WegdeelID") REFERENCES "Wegdeel" ("WegdeelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stremming" ADD CONSTRAINT "fk_gewijzigdDoor_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stremming" ADD CONSTRAINT "fk_ingevoerdDoor_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Strooirouteuitvoering" ADD CONSTRAINT "FK_Strooirouteuitvoering_Strooidag"
	FOREIGN KEY ("StrooidagID") REFERENCES "Strooidag" ("StrooidagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Strooirouteuitvoering" ADD CONSTRAINT "FK_Strooirouteuitvoering_Strooiroute"
	FOREIGN KEY ("StrooirouteID") REFERENCES "Strooiroute" ("StrooirouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verkeerstelling" ADD CONSTRAINT "fk_gegenereerdDoor_sensor"
	FOREIGN KEY ("SensorID") REFERENCES "Sensor" ("SensorID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vloginfo" ADD CONSTRAINT "FK_Vloginfo_Kast"
	FOREIGN KEY ("KastID") REFERENCES "Kast" ("KastID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vloginfo" ADD CONSTRAINT "FK_Vloginfo_Paal"
	FOREIGN KEY ("PaalID") REFERENCES "Paal" ("PaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vloginfo" ADD CONSTRAINT "FK_Vloginfo_Sensor"
	FOREIGN KEY ("SensorID") REFERENCES "Sensor" ("SensorID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Contact" ADD CONSTRAINT "PK_Contact"
	PRIMARY KEY ("ContactID");

ALTER TABLE "Hotel" ADD CONSTRAINT "PK_Hotel"
	PRIMARY KEY ("HotelID");

ALTER TABLE "Hotelbezoek" ADD CONSTRAINT "PK_Hotelbezoek"
	PRIMARY KEY ("HotelbezoekID");

ALTER TABLE "Verkooppunt" ADD CONSTRAINT "PK_Verkooppunt"
	PRIMARY KEY ("VerkooppuntID");

ALTER TABLE "Werkgelegenheid" ADD CONSTRAINT "PK_Werkgelegenheid"
	PRIMARY KEY ("WerkgelegenheidID");

ALTER TABLE "Winkelvloeroppervlak" ADD CONSTRAINT "PK_Winkelvloeroppervlak"
	PRIMARY KEY ("WinkelvloeroppervlakID");

ALTER TABLE "Contact" ADD CONSTRAINT "FK_Contact_Vestiging"
	FOREIGN KEY ("VestigingID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hotel" ADD CONSTRAINT "Fk_hotel_vestiging"
	FOREIGN KEY ("HotelID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hotelbezoek" ADD CONSTRAINT fk_heeft_hotel
	FOREIGN KEY ("HotelID") REFERENCES "Hotel" ("HotelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_contact_natuurlijkpersoon" ADD CONSTRAINT "Fk_kp_contact_natuurlijkpersoon_contact"
	FOREIGN KEY ("ContactID") REFERENCES "Contact" ("ContactID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_contact_natuurlijkpersoon" ADD CONSTRAINT "Fk_kp_contact_natuurlijkpersoon_natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verkooppunt" ADD CONSTRAINT "Fk_verkooppunt_vestiging"
	FOREIGN KEY ("VerkooppuntID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Werkgelegenheid" ADD CONSTRAINT fk_heeft_vestiging
	FOREIGN KEY ("VestigingID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Winkelvloeroppervlak" ADD CONSTRAINT fk_heeft_gebouwdobject
	FOREIGN KEY ("GebouwdobjectID") REFERENCES "Gebouwdobject" ("GebouwdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagLeerlingenvervoer" ADD CONSTRAINT "PK_AanvraagLeerlingenvervoer"
	PRIMARY KEY ("AanvraagLeerlingenvervoerID");

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "PK_Aanvraagofmelding"
	PRIMARY KEY ("AanvraagofmeldingID");

ALTER TABLE "Aanvraagvrijstelling" ADD CONSTRAINT "PK_Aanvraagvrijstelling"
	PRIMARY KEY ("AanvraagvrijstellingID");

ALTER TABLE "BeschikkingLeerlingenvervoer" ADD CONSTRAINT "PK_BeschikkingLeerlingenvervoer"
	PRIMARY KEY ("BeschikkingLeerlingenvervoerID");

ALTER TABLE "Beslissing" ADD CONSTRAINT "PK_Beslissing"
	PRIMARY KEY ("BeslissingID");

ALTER TABLE "DoorgeleidingOm" ADD CONSTRAINT "PK_DoorgeleidingOm"
	PRIMARY KEY ("DoorgeleidingOmID");

ALTER TABLE "Enum_sanctiesoort" ADD CONSTRAINT "PK_Enum_sanctiesoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_verzuimsoort" ADD CONSTRAINT "PK_Enum_verzuimsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vrijstellingsoort" ADD CONSTRAINT "PK_Enum_vrijstellingsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Halt_verwijzing" ADD CONSTRAINT "PK_Halt_verwijzing"
	PRIMARY KEY ("Halt-verwijzingID");

ALTER TABLE "KlachtLeerlingenvervoer" ADD CONSTRAINT "PK_KlachtLeerlingenvervoer"
	PRIMARY KEY ("KlachtLeerlingenvervoerID");

ALTER TABLE "Leerplichtambtenaar" ADD CONSTRAINT "PK_Leerplichtambtenaar"
	PRIMARY KEY ("LeerplichtambtenaarID");

ALTER TABLE "ProcesverbaalOnderwijs" ADD CONSTRAINT "PK_ProcesverbaalOnderwijs"
	PRIMARY KEY ("ProcesverbaalOnderwijsID");

ALTER TABLE "Verlofaanvraag" ADD CONSTRAINT "PK_Verlofaanvraag"
	PRIMARY KEY ("VerlofaanvraagID");

ALTER TABLE "Vervoerder" ADD CONSTRAINT "PK_Vervoerder"
	PRIMARY KEY ("VervoerderID");

ALTER TABLE "Verzuimmelding" ADD CONSTRAINT "PK_Verzuimmelding"
	PRIMARY KEY ("VerzuimmeldingID");

ALTER TABLE "Vrijstelling" ADD CONSTRAINT "PK_Vrijstelling"
	PRIMARY KEY ("VrijstellingID");

ALTER TABLE "ZiekmeldingLeerlingenvervoer" ADD CONSTRAINT "PK_ZiekmeldingLeerlingenvervoer"
	PRIMARY KEY ("ZiekmeldingLeerlingenvervoerID");

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "FK_Aanvraagofmelding_Leerling"
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "FK_Aanvraagofmelding_School"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagofmelding" ADD CONSTRAINT "Fk_aanvraagofmelding_aanvraagofmelding"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraagvrijstelling" ADD CONSTRAINT "Fk_aanvraagvrijstelling_aanvraagofmelding"
	FOREIGN KEY ("AanvraagvrijstellingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikkingLeerlingenvervoer" ADD CONSTRAINT "Fk_beschikkingLeerlingenvervoe_beslissing"
	FOREIGN KEY ("BeschikkingLeerlingenvervoeID") REFERENCES "Beslissing" ("BeslissingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beslissing" ADD CONSTRAINT "fk_leidtTot_aanvraagofmelding"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beslissing" ADD CONSTRAINT "FK_Beslissing_Leerplichtambtenaar"
	FOREIGN KEY ("LeerplichtambtenaarID") REFERENCES "Leerplichtambtenaar" ("LeerplichtambtenaarID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beslissing" ADD CONSTRAINT "FK_Beslissing_Leerling"
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beslissing" ADD CONSTRAINT "FK_Beslissing_School"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "DoorgeleidingOm" ADD CONSTRAINT "Fk_doorgeleidingOm_beslissing"
	FOREIGN KEY ("DoorgeleidingOmID") REFERENCES "Beslissing" ("BeslissingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Halt_verwijzing" ADD CONSTRAINT "Fk_halt_verwijzing_beslissing"
	FOREIGN KEY ("Halt_verwijzingID") REFERENCES "Beslissing" ("BeslissingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "KlachtLeerlingenvervoer" ADD CONSTRAINT "FK_KlachtLeerlingenvervoer_Leerling"
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "KlachtLeerlingenvervoer" ADD CONSTRAINT "FK_KlachtLeerlingenvervoer_Vervoerder"
	FOREIGN KEY ("VervoerderID") REFERENCES "Vervoerder" ("VervoerderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschikkingLeerlingenvervo" ADD CONSTRAINT "Fk_kp_beschikkingleerlingenvervo_vervoerder"
	FOREIGN KEY ("VervoerderID") REFERENCES "Vervoerder" ("VervoerderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschikkingLeerlingenvervo" ADD CONSTRAINT "Fk_kp_beschikkingleerlingenvervo_beschikkingLeerlingenvervoe"
	FOREIGN KEY ("BeschikkingLeerlingenvervoeID") REFERENCES "BeschikkingLeerlingenvervoer" ("BeschikkingLeerlingenvervoerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leerplichtambtenaar" ADD CONSTRAINT "Fk_leerplichtambtenaar_medewerker"
	FOREIGN KEY ("LeerplichtambtenaarID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ProcesverbaalOnderwijs" ADD CONSTRAINT "Fk_procesverbaalOnderwijs_beslissing"
	FOREIGN KEY ("ProcesverbaalOnderwijsID") REFERENCES "Beslissing" ("BeslissingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ProcesverbaalOnderwijs" ADD CONSTRAINT "fk_opgelegdDoor_leerplichtambt"
	FOREIGN KEY ("LeerplichtambtenaarID") REFERENCES "Leerplichtambtenaar" ("LeerplichtambtenaarID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ProcesverbaalOnderwijs" ADD CONSTRAINT "fk_betreftLeerling_leerling"
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verlofaanvraag" ADD CONSTRAINT "Fk_verlofaanvraag_aanvraagofmelding"
	FOREIGN KEY ("VerlofaanvraagID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vervoerder" ADD CONSTRAINT "Fk_vervoerder_leverancier"
	FOREIGN KEY ("VervoerderID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzuimmelding" ADD CONSTRAINT "Fk_verzuimmelding_aanvraagofmelding"
	FOREIGN KEY ("VerzuimmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzuimmelding" ADD CONSTRAINT "FK_Verzuimmelding_School"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzuimmelding" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vrijstelling" ADD CONSTRAINT "Fk_vrijstelling_beslissing"
	FOREIGN KEY ("VrijstellingID") REFERENCES "Beslissing" ("BeslissingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vrijstelling" ADD CONSTRAINT "FK_Vrijstelling_School"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vrijstelling" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ZiekmeldingLeerlingenvervoer" ADD CONSTRAINT fk_betreft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_onderwijstype" ADD CONSTRAINT "PK_Enum_onderwijstype"
	PRIMARY KEY ("ID");

ALTER TABLE "Inschrijving" ADD CONSTRAINT "PK_Inschrijving"
	PRIMARY KEY ("InschrijvingID");

ALTER TABLE "Leerjaar" ADD CONSTRAINT "PK_Leerjaar"
	PRIMARY KEY ("LeerjaarID");

ALTER TABLE "Leerling" ADD CONSTRAINT "PK_Leerling"
	PRIMARY KEY ("LeerlingID");

ALTER TABLE "Locatie" ADD CONSTRAINT "PK_Locatie"
	PRIMARY KEY ("LocatieID");

ALTER TABLE "Loopbaanstap" ADD CONSTRAINT "PK_Loopbaanstap"
	PRIMARY KEY ("LoopbaanstapID");

ALTER TABLE "Onderwijsloopbaan" ADD CONSTRAINT "PK_Onderwijsloopbaan"
	PRIMARY KEY ("OnderwijsloopbaanID");

ALTER TABLE "Onderwijsniveau" ADD CONSTRAINT "PK_Onderwijsniveau"
	PRIMARY KEY ("OnderwijsniveauID");

ALTER TABLE "Onderwijssoort" ADD CONSTRAINT "PK_Onderwijssoort"
	PRIMARY KEY ("OnderwijssoortID");

ALTER TABLE "OuderOfVerzorger" ADD CONSTRAINT "PK_OuderOfVerzorger"
	PRIMARY KEY ("OuderOfVerzorgerID");

ALTER TABLE "School" ADD CONSTRAINT "PK_School"
	PRIMARY KEY ("SchoolID");

ALTER TABLE "Startkwalificatie" ADD CONSTRAINT "PK_Startkwalificatie"
	PRIMARY KEY ("StartkwalificatieID");

ALTER TABLE "Uitschrijving" ADD CONSTRAINT "PK_Uitschrijving"
	PRIMARY KEY ("UitschrijvingID");

ALTER TABLE "Inschrijving" ADD CONSTRAINT "FK_Inschrijving_School"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inschrijving" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_doorgeleidingOm_ouderOfV" ADD CONSTRAINT "Fk_kp_doorgeleidingom_ouderofv_ouderOfVerzorger"
	FOREIGN KEY ("OuderOfVerzorgerID") REFERENCES "OuderOfVerzorger" ("OuderOfVerzorgerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_doorgeleidingOm_ouderOfV" ADD CONSTRAINT "Fk_kp_doorgeleidingom_ouderofv_doorgeleidingOm"
	FOREIGN KEY ("DoorgeleidingOmID") REFERENCES "DoorgeleidingOm" ("DoorgeleidingOmID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_procesverbaalOnderwijs_oud" ADD CONSTRAINT "Fk_kp_procesverbaalonderwijs_oud_ouderOfVerzorger"
	FOREIGN KEY ("OuderOfVerzorgerID") REFERENCES "OuderOfVerzorger" ("OuderOfVerzorgerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_procesverbaalOnderwijs_oud" ADD CONSTRAINT "Fk_kp_procesverbaalonderwijs_oud_procesverbaalOnderwijs"
	FOREIGN KEY ("ProcesverbaalOnderwijsID") REFERENCES "ProcesverbaalOnderwijs" ("ProcesverbaalOnderwijsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_onderwijsloopbaan" ADD CONSTRAINT "Fk_kp_school_onderwijsloopbaan_onderwijsloopbaan"
	FOREIGN KEY ("OnderwijsloopbaanID") REFERENCES "Onderwijsloopbaan" ("OnderwijsloopbaanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_onderwijsloopbaan" ADD CONSTRAINT "Fk_kp_school_onderwijsloopbaan_school"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_onderwijssoort" ADD CONSTRAINT "Fk_kp_school_onderwijssoort_onderwijssoort"
	FOREIGN KEY ("OnderwijssoortID") REFERENCES "Onderwijssoort" ("OnderwijssoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_onderwijssoort" ADD CONSTRAINT "Fk_kp_school_onderwijssoort_school"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_sportlocatie" ADD CONSTRAINT "Fk_kp_school_sportlocatie_school"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_school_sportlocatie" ADD CONSTRAINT "Fk_kp_school_sportlocatie_sportlocatie"
	FOREIGN KEY ("SportlocatieID") REFERENCES "Sportlocatie" ("SportlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leerling" ADD CONSTRAINT "Fk_leerling_ingeschrevenpersoon"
	FOREIGN KEY ("LeerlingID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Locatie" ADD CONSTRAINT "fk_schoolHeeft_school"
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Loopbaanstap" ADD CONSTRAINT "FK_Loopbaanstap_Onderwijsloopbaan"
	FOREIGN KEY ("OnderwijsloopbaanID") REFERENCES "Onderwijsloopbaan" ("OnderwijsloopbaanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onderwijsloopbaan" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "OuderOfVerzorger" ADD CONSTRAINT "Fk_ouderOfVerzorger_ingeschrevenpersoon"
	FOREIGN KEY ("OuderOfVerzorgerID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "School" ADD CONSTRAINT "Fk_school_nietnatuurlijkpersoon"
	FOREIGN KEY ("SchoolID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Startkwalificatie" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitschrijving" ADD CONSTRAINT fk_heeft_leerling
	FOREIGN KEY ("LeerlingID") REFERENCES "Leerling" ("LeerlingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitschrijving" ADD CONSTRAINT fk_heeft_school
	FOREIGN KEY ("SchoolID") REFERENCES "School" ("SchoolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archeologiebesluit" ADD CONSTRAINT "PK_Archeologiebesluit"
	PRIMARY KEY ("ArcheologiebesluitID");

ALTER TABLE "Artefact" ADD CONSTRAINT "PK_Artefact"
	PRIMARY KEY ("ArtefactID");

ALTER TABLE "Artefactsoort" ADD CONSTRAINT "PK_Artefactsoort"
	PRIMARY KEY ("ArtefactsoortID");

ALTER TABLE "Boring" ADD CONSTRAINT "PK_Boring"
	PRIMARY KEY ("BoringID");

ALTER TABLE "Doos" ADD CONSTRAINT "PK_Doos"
	PRIMARY KEY ("DoosID");

ALTER TABLE "Kaart" ADD CONSTRAINT "PK_Kaart"
	PRIMARY KEY ("KaartID");

ALTER TABLE "Locatie" ADD CONSTRAINT "PK_Locatie"
	PRIMARY KEY ("LocatieID");

ALTER TABLE "Magazijnlocatie" ADD CONSTRAINT "PK_Magazijnlocatie"
	PRIMARY KEY ("MagazijnlocatieID");

ALTER TABLE "Magazijnplaatsing" ADD CONSTRAINT "PK_Magazijnplaatsing"
	PRIMARY KEY ("MagazijnplaatsingID");

ALTER TABLE "Project" ADD CONSTRAINT "PK_Project"
	PRIMARY KEY ("ProjectID");

ALTER TABLE "Put" ADD CONSTRAINT "PK_Put"
	PRIMARY KEY ("PutID");

ALTER TABLE "Spoor" ADD CONSTRAINT "PK_Spoor"
	PRIMARY KEY ("SpoorID");

ALTER TABLE "Stelling" ADD CONSTRAINT "PK_Stelling"
	PRIMARY KEY ("StellingID");

ALTER TABLE "Vindplaats" ADD CONSTRAINT "PK_Vindplaats"
	PRIMARY KEY ("VindplaatsID");

ALTER TABLE "Vlak" ADD CONSTRAINT "PK_Vlak"
	PRIMARY KEY ("VlakID");

ALTER TABLE "Vondst" ADD CONSTRAINT "PK_Vondst"
	PRIMARY KEY ("VondstID");

ALTER TABLE "Vulling" ADD CONSTRAINT "PK_Vulling"
	PRIMARY KEY ("VullingID");

ALTER TABLE "Archeologiebesluit" ADD CONSTRAINT fk_heeft_project
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Artefact" ADD CONSTRAINT "FK_Artefact_Doos"
	FOREIGN KEY ("DoosID") REFERENCES "Doos" ("DoosID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Artefact" ADD CONSTRAINT "FK_Artefact_Magazijnplaatsing"
	FOREIGN KEY ("MagazijnplaatsingID") REFERENCES "Magazijnplaatsing" ("MagazijnplaatsingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Artefact" ADD CONSTRAINT "FK_Artefact_Artefactsoort"
	FOREIGN KEY ("ArtefactsoortID") REFERENCES "Artefactsoort" ("ArtefactsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Artefact" ADD CONSTRAINT fk_bevat_vondst
	FOREIGN KEY ("VondstID") REFERENCES "Vondst" ("VondstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Boring" ADD CONSTRAINT fk_heeft_project
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doos" ADD CONSTRAINT "FK_Doos_Magazijnlocatie"
	FOREIGN KEY ("MagazijnlocatieID") REFERENCES "Magazijnlocatie" ("MagazijnlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doos" ADD CONSTRAINT "fk_zitIn_magazijnplaatsing"
	FOREIGN KEY ("MagazijnplaatsingID") REFERENCES "Magazijnplaatsing" ("MagazijnplaatsingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_project_locatie" ADD CONSTRAINT "Fk_kp_project_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_project_locatie" ADD CONSTRAINT "Fk_kp_project_locatie_project"
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_put_locatie" ADD CONSTRAINT "Fk_kp_put_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_put_locatie" ADD CONSTRAINT "Fk_kp_put_locatie_put"
	FOREIGN KEY ("PutID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Magazijnlocatie" ADD CONSTRAINT fk_heeft_stelling
	FOREIGN KEY ("StellingID") REFERENCES "Stelling" ("StellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Magazijnplaatsing" ADD CONSTRAINT "FK_Magazijnplaatsing_Magazijnlocatie"
	FOREIGN KEY ("MagazijnlocatieID") REFERENCES "Magazijnlocatie" ("MagazijnlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Magazijnplaatsing" ADD CONSTRAINT "FK_Magazijnplaatsing_Project"
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Project" ADD CONSTRAINT "fk_hoortBij_vindplaats"
	FOREIGN KEY ("VindplaatsID") REFERENCES "Vindplaats" ("VindplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Put" ADD CONSTRAINT fk_heeft_project
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Spoor" ADD CONSTRAINT fk_heeft_vlak
	FOREIGN KEY ("VlakID") REFERENCES "Vlak" ("VlakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vlak" ADD CONSTRAINT fk_heeft_put
	FOREIGN KEY ("PutID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vondst" ADD CONSTRAINT fk_heeft_vulling
	FOREIGN KEY ("VullingID") REFERENCES "Vulling" ("VullingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vulling" ADD CONSTRAINT fk_heeft_spoor
	FOREIGN KEY ("SpoorID") REFERENCES "Spoor" ("SpoorID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraag" ADD CONSTRAINT "PK_Aanvraag"
	PRIMARY KEY ("AanvraagID");

ALTER TABLE "Archief" ADD CONSTRAINT "PK_Archief"
	PRIMARY KEY ("ArchiefID");

ALTER TABLE "Archiefcategorie" ADD CONSTRAINT "PK_Archiefcategorie"
	PRIMARY KEY ("ArchiefcategorieID");

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "PK_Archiefstuk"
	PRIMARY KEY ("ArchiefstukID");

ALTER TABLE "Auteur" ADD CONSTRAINT "PK_Auteur"
	PRIMARY KEY ("AuteurID");

ALTER TABLE "Bezoeker" ADD CONSTRAINT "PK_Bezoeker"
	PRIMARY KEY ("BezoekerID");

ALTER TABLE "Depot" ADD CONSTRAINT "PK_Depot"
	PRIMARY KEY ("DepotID");

ALTER TABLE "Digitaalbestand" ADD CONSTRAINT "PK_Digitaalbestand"
	PRIMARY KEY ("DigitaalbestandID");

ALTER TABLE "Indeling" ADD CONSTRAINT "PK_Indeling"
	PRIMARY KEY ("IndelingID");

ALTER TABLE "Index" ADD CONSTRAINT "PK_Index"
	PRIMARY KEY ("IndexID");

ALTER TABLE "Kast" ADD CONSTRAINT "PK_Kast"
	PRIMARY KEY ("KastID");

ALTER TABLE "NadereToegang" ADD CONSTRAINT "PK_NadereToegang"
	PRIMARY KEY ("NadereToegangID");

ALTER TABLE "Ordeningsschema" ADD CONSTRAINT "PK_Ordeningsschema"
	PRIMARY KEY ("OrdeningsschemaID");

ALTER TABLE "Plank" ADD CONSTRAINT "PK_Plank"
	PRIMARY KEY ("PlankID");

ALTER TABLE "Rechthebbende" ADD CONSTRAINT "PK_Rechthebbende"
	PRIMARY KEY ("RechthebbendeID");

ALTER TABLE "Stelling" ADD CONSTRAINT "PK_Stelling"
	PRIMARY KEY ("StellingID");

ALTER TABLE "Uitgever" ADD CONSTRAINT "PK_Uitgever"
	PRIMARY KEY ("UitgeverID");

ALTER TABLE "Vindplaats" ADD CONSTRAINT "PK_Vindplaats"
	PRIMARY KEY ("VindplaatsID");

ALTER TABLE "Aanvraag" ADD CONSTRAINT fk_doet_bezoeker
	FOREIGN KEY ("BezoekerID") REFERENCES "Bezoeker" ("BezoekerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archief" ADD CONSTRAINT "FK_Archief_Rechthebbende"
	FOREIGN KEY ("RechthebbendeID") REFERENCES "Rechthebbende" ("RechthebbendeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "FK_Archiefstuk_Archief"
	FOREIGN KEY ("ArchiefID") REFERENCES "Archief" ("ArchiefID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "FK_Archiefstuk_Vindplaats"
	FOREIGN KEY ("VindplaatsID") REFERENCES "Vindplaats" ("VindplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "FK_Archiefstuk_Uitgever"
	FOREIGN KEY ("UitgeverID") REFERENCES "Uitgever" ("UitgeverID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "fk_valtBinnen_indeling"
	FOREIGN KEY ("IndelingID") REFERENCES "Indeling" ("IndelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "Fk_archiefstuk_erfgoedObject"
	FOREIGN KEY ("ArchiefstukID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Archiefstuk" ADD CONSTRAINT "Fk_archiefstuk_document"
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Auteur" ADD CONSTRAINT "Fk_auteur_historischPersoon"
	FOREIGN KEY ("AuteurID") REFERENCES "HistorischPersoon" ("HistorischPersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bezoeker" ADD CONSTRAINT "Fk_bezoeker_natuurlijkpersoon"
	FOREIGN KEY ("BezoekerID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Digitaalbestand" ADD CONSTRAINT fk_heeft_archiefstuk
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Archiefstuk" ("ArchiefstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Indeling" ADD CONSTRAINT "FK_Indeling_Archief"
	FOREIGN KEY ("ArchiefID") REFERENCES "Archief" ("ArchiefID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Indeling" ADD CONSTRAINT "fk_valtBinnen_indeling"
	FOREIGN KEY ("IndelingID") REFERENCES "Indeling" ("IndelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Index" ADD CONSTRAINT "fk_wordtBeschreven_nadereToega"
	FOREIGN KEY ("NadereToegangID") REFERENCES "NadereToegang" ("NadereToegangID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kast" ADD CONSTRAINT fk_heeft_stelling
	FOREIGN KEY ("StellingID") REFERENCES "Stelling" ("StellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_aanvraag_archiefstuk" ADD CONSTRAINT "Fk_kp_aanvraag_archiefstuk_archiefstuk"
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Archiefstuk" ("ArchiefstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_aanvraag_archiefstuk" ADD CONSTRAINT "Fk_kp_aanvraag_archiefstuk_aanvraag"
	FOREIGN KEY ("AanvraagID") REFERENCES "Aanvraag" ("AanvraagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archief_archiefcategorie" ADD CONSTRAINT "Fk_kp_archief_archiefcategorie_archiefcategorie"
	FOREIGN KEY ("ArchiefcategorieID") REFERENCES "Archiefcategorie" ("ArchiefcategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archief_archiefcategorie" ADD CONSTRAINT "Fk_kp_archief_archiefcategorie_archief"
	FOREIGN KEY ("ArchiefID") REFERENCES "Archief" ("ArchiefID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archief_periode" ADD CONSTRAINT "Fk_kp_archief_periode_archief"
	FOREIGN KEY ("ArchiefID") REFERENCES "Archief" ("ArchiefID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archief_periode" ADD CONSTRAINT "Fk_kp_archief_periode_periode"
	FOREIGN KEY ("PeriodeID") REFERENCES "Periode" ("PeriodeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archiefstuk_ordeningsschema" ADD CONSTRAINT "Fk_kp_archiefstuk_ordeningsschema_ordeningsschema"
	FOREIGN KEY ("OrdeningsschemaID") REFERENCES "Ordeningsschema" ("OrdeningsschemaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archiefstuk_ordeningsschema" ADD CONSTRAINT "Fk_kp_archiefstuk_ordeningsschema_archiefstuk"
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Archiefstuk" ("ArchiefstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archiefstuk_periode" ADD CONSTRAINT "Fk_kp_archiefstuk_periode_archiefstuk"
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Archiefstuk" ("ArchiefstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_archiefstuk_periode" ADD CONSTRAINT "Fk_kp_archiefstuk_periode_periode"
	FOREIGN KEY ("PeriodeID") REFERENCES "Periode" ("PeriodeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "NadereToegang" ADD CONSTRAINT fk_heeft_archiefstuk
	FOREIGN KEY ("ArchiefstukID") REFERENCES "Archiefstuk" ("ArchiefstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Plank" ADD CONSTRAINT fk_heeft_kast
	FOREIGN KEY ("KastID") REFERENCES "Kast" ("KastID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rechthebbende" ADD CONSTRAINT "Fk_rechthebbende_rechtspersoon"
	FOREIGN KEY ("RechthebbendeID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stelling" ADD CONSTRAINT fk_heeft_depot
	FOREIGN KEY ("DepotID") REFERENCES "Depot" ("DepotID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitgever" ADD CONSTRAINT "Fk_uitgever_rechtspersoon"
	FOREIGN KEY ("UitgeverID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vindplaats" ADD CONSTRAINT "FK_Vindplaats_Depot"
	FOREIGN KEY ("DepotID") REFERENCES "Depot" ("DepotID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vindplaats" ADD CONSTRAINT "FK_Vindplaats_Kast"
	FOREIGN KEY ("KastID") REFERENCES "Kast" ("KastID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vindplaats" ADD CONSTRAINT "FK_Vindplaats_Plank"
	FOREIGN KEY ("PlankID") REFERENCES "Plank" ("PlankID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vindplaats" ADD CONSTRAINT "FK_Vindplaats_Stelling"
	FOREIGN KEY ("StellingID") REFERENCES "Stelling" ("StellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ErfgoedObject" ADD CONSTRAINT "PK_ErfgoedObject"
	PRIMARY KEY ("ErfgoedObjectID");

ALTER TABLE "HistorischeRol" ADD CONSTRAINT "PK_HistorischeRol"
	PRIMARY KEY ("HistorischeRolID");

ALTER TABLE "HistorischPersoon" ADD CONSTRAINT "PK_HistorischPersoon"
	PRIMARY KEY ("HistorischPersoonID");

ALTER TABLE "Objectclassificatie" ADD CONSTRAINT "PK_Objectclassificatie"
	PRIMARY KEY ("ObjectclassificatieID");

ALTER TABLE "HistorischeRol" ADD CONSTRAINT "FK_HistorischeRol_Historisch Persoon"
	FOREIGN KEY ("HistorischPersoonID") REFERENCES "HistorischPersoon" ("HistorischPersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "HistorischeRol" ADD CONSTRAINT "Fk_historischerol_erfgoedObject"
	FOREIGN KEY ("ErfgoedObjectID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "HistorischPersoon" ADD CONSTRAINT "Fk_historischPersoon_natuurlijkpersoon"
	FOREIGN KEY ("HistorischPersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_erfgoedObject_objectclassi" ADD CONSTRAINT "Fk_kp_erfgoedobject_objectclassi_objectclassificatie"
	FOREIGN KEY ("ObjectclassificatieID") REFERENCES "Objectclassificatie" ("ObjectclassificatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_erfgoedObject_objectclassi" ADD CONSTRAINT "Fk_kp_erfgoedobject_objectclassi_erfgoedObject"
	FOREIGN KEY ("ErfgoedObjectID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_foto_erfgoedObject" ADD CONSTRAINT "Fk_kp_foto_erfgoedobject_erfgoedObject"
	FOREIGN KEY ("ErfgoedObjectID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_foto_erfgoedObject" ADD CONSTRAINT "Fk_kp_foto_erfgoedobject_foto"
	FOREIGN KEY ("FotoID") REFERENCES "Foto" ("FotoID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_tentoonstelling_historisch" ADD CONSTRAINT "Fk_kp_tentoonstelling_historisch_historischPersoon"
	FOREIGN KEY ("HistorischPersoonID") REFERENCES "HistorischPersoon" ("HistorischPersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_tentoonstelling_historisch" ADD CONSTRAINT "Fk_kp_tentoonstelling_historisch_tentoonstelling"
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_video_opname_erfgoedObject" ADD CONSTRAINT "Fk_kp_video_opname_erfgoedobject_erfgoedObject"
	FOREIGN KEY ("ErfgoedObjectID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_video_opname_erfgoedObject" ADD CONSTRAINT "Fk_kp_video_opname_erfgoedobject_video_opname"
	FOREIGN KEY ("Video_opnameID") REFERENCES "Video_opname" ("Video-opnameID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ambacht" ADD CONSTRAINT "PK_Ambacht"
	PRIMARY KEY ("AmbachtID");

ALTER TABLE "BeschermdeStatus" ADD CONSTRAINT "PK_BeschermdeStatus"
	PRIMARY KEY ("BeschermdeStatusID");

ALTER TABLE "Bouwactiviteit" ADD CONSTRAINT "PK_Bouwactiviteit"
	PRIMARY KEY ("BouwactiviteitID");

ALTER TABLE "Bouwstijl" ADD CONSTRAINT "PK_Bouwstijl"
	PRIMARY KEY ("BouwstijlID");

ALTER TABLE "Bouwtype" ADD CONSTRAINT "PK_Bouwtype"
	PRIMARY KEY ("BouwtypeID");

ALTER TABLE "Enum_typemonument" ADD CONSTRAINT "PK_Enum_typemonument"
	PRIMARY KEY ("ID");

ALTER TABLE "Oorspronkelijkefunctie" ADD CONSTRAINT "PK_Oorspronkelijkefunctie"
	PRIMARY KEY ("OorspronkelijkefunctieID");

ALTER TABLE "Kp_beschermdeStatus_ambacht" ADD CONSTRAINT "Fk_kp_beschermdestatus_ambacht_ambacht"
	FOREIGN KEY ("AmbachtID") REFERENCES "Ambacht" ("AmbachtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_ambacht" ADD CONSTRAINT "Fk_kp_beschermdestatus_ambacht_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwactiv" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwactiv_bouwactiviteit"
	FOREIGN KEY ("BouwactiviteitID") REFERENCES "Bouwactiviteit" ("BouwactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwactiv" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwactiv_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwstijl" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwstijl_bouwstijl"
	FOREIGN KEY ("BouwstijlID") REFERENCES "Bouwstijl" ("BouwstijlID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwstijl" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwstijl_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwtype" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwtype_bouwtype"
	FOREIGN KEY ("BouwtypeID") REFERENCES "Bouwtype" ("BouwtypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_bouwtype" ADD CONSTRAINT "Fk_kp_beschermdestatus_bouwtype_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_oorspronk" ADD CONSTRAINT "Fk_kp_beschermdestatus_oorspronk_oorspronkelijkefunctie"
	FOREIGN KEY ("OorspronkelijkefunctieID") REFERENCES "Oorspronkelijkefunctie" ("OorspronkelijkefunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_beschermdeStatus_oorspronk" ADD CONSTRAINT "Fk_kp_beschermdestatus_oorspronk_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "PK_Activiteit"
	PRIMARY KEY ("ActiviteitID");

ALTER TABLE "Activiteitsoort" ADD CONSTRAINT "PK_Activiteitsoort"
	PRIMARY KEY ("ActiviteitsoortID");

ALTER TABLE "Balieverkoop" ADD CONSTRAINT "PK_Balieverkoop"
	PRIMARY KEY ("BalieverkoopID");

ALTER TABLE "BalieverkoopEntreekaart" ADD CONSTRAINT "PK_BalieverkoopEntreekaart"
	PRIMARY KEY ("BalieverkoopEntreekaartID");

ALTER TABLE "Belanghebbende" ADD CONSTRAINT "PK_Belanghebbende"
	PRIMARY KEY ("BelanghebbendeID");

ALTER TABLE "Belangtype" ADD CONSTRAINT "PK_Belangtype"
	PRIMARY KEY ("BelangtypeID");

ALTER TABLE "Bruikleen" ADD CONSTRAINT "PK_Bruikleen"
	PRIMARY KEY ("BruikleenID");

ALTER TABLE "Collectie" ADD CONSTRAINT "PK_Collectie"
	PRIMARY KEY ("CollectieID");

ALTER TABLE "Doelgroep" ADD CONSTRAINT "PK_Doelgroep"
	PRIMARY KEY ("DoelgroepID");

ALTER TABLE "Entreekaart" ADD CONSTRAINT "PK_Entreekaart"
	PRIMARY KEY ("EntreekaartID");

ALTER TABLE "Incident" ADD CONSTRAINT "PK_Incident"
	PRIMARY KEY ("IncidentID");

ALTER TABLE "Lener" ADD CONSTRAINT "PK_Lener"
	PRIMARY KEY ("LenerID");

ALTER TABLE "Mailing" ADD CONSTRAINT "PK_Mailing"
	PRIMARY KEY ("MailingID");

ALTER TABLE "Museumobject" ADD CONSTRAINT "PK_Museumobject"
	PRIMARY KEY ("MuseumobjectID");

ALTER TABLE "Museumrelatie" ADD CONSTRAINT "PK_Museumrelatie"
	PRIMARY KEY ("MuseumrelatieID");

ALTER TABLE "Omzetgroep" ADD CONSTRAINT "PK_Omzetgroep"
	PRIMARY KEY ("OmzetgroepID");

ALTER TABLE "Prijs" ADD CONSTRAINT "PK_Prijs"
	PRIMARY KEY ("PrijsID");

ALTER TABLE "Product" ADD CONSTRAINT "PK_Product"
	PRIMARY KEY ("ProductID");

ALTER TABLE "Productgroep" ADD CONSTRAINT "PK_Productgroep"
	PRIMARY KEY ("ProductgroepID");

ALTER TABLE "Productie_eenheid" ADD CONSTRAINT "PK_Productie_eenheid"
	PRIMARY KEY ("Productie-eenheidID");

ALTER TABLE "Programma" ADD CONSTRAINT "PK_Programma"
	PRIMARY KEY ("ProgrammaID");

ALTER TABLE "Programmasoort" ADD CONSTRAINT "PK_Programmasoort"
	PRIMARY KEY ("ProgrammasoortID");

ALTER TABLE "Reservering" ADD CONSTRAINT "PK_Reservering"
	PRIMARY KEY ("ReserveringID");

ALTER TABLE "Rol" ADD CONSTRAINT "PK_Rol"
	PRIMARY KEY ("RolID");

ALTER TABLE "Rondleiding" ADD CONSTRAINT "PK_Rondleiding"
	PRIMARY KEY ("RondleidingID");

ALTER TABLE "Samensteller" ADD CONSTRAINT "PK_Samensteller"
	PRIMARY KEY ("SamenstellerID");

ALTER TABLE "Standplaats" ADD CONSTRAINT "PK_Standplaats"
	PRIMARY KEY ("StandplaatsID");

ALTER TABLE "Tentoonstelling" ADD CONSTRAINT "PK_Tentoonstelling"
	PRIMARY KEY ("TentoonstellingID");

ALTER TABLE "Voorziening" ADD CONSTRAINT "PK_Voorziening"
	PRIMARY KEY ("VoorzieningID");

ALTER TABLE "Winkelverkoopgroep" ADD CONSTRAINT "PK_Winkelverkoopgroep"
	PRIMARY KEY ("WinkelverkoopgroepID");

ALTER TABLE "Winkelvoorraaditem" ADD CONSTRAINT "PK_Winkelvoorraaditem"
	PRIMARY KEY ("WinkelvoorraaditemID");

ALTER TABLE "Zaal" ADD CONSTRAINT "PK_Zaal"
	PRIMARY KEY ("ZaalID");

ALTER TABLE "Activiteit" ADD CONSTRAINT "FK_Activiteit_Activiteitsoort"
	FOREIGN KEY ("ActiviteitsoortID") REFERENCES "Activiteitsoort" ("ActiviteitsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "FK_Activiteit_Activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "FK_Activiteit_Rondleiding"
	FOREIGN KEY ("RondleidingID") REFERENCES "Rondleiding" ("RondleidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "FK_Activiteit_Programma"
	FOREIGN KEY ("ProgrammaID") REFERENCES "Programma" ("ProgrammaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieverkoop" ADD CONSTRAINT "FK_Balieverkoop_Product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Balieverkoop" ADD CONSTRAINT "FK_Balieverkoop_Prijs"
	FOREIGN KEY ("PrijsID") REFERENCES "Prijs" ("PrijsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BalieverkoopEntreekaart" ADD CONSTRAINT "Fk_balieverkoopEntreekaart_balieverkoop"
	FOREIGN KEY ("BalieverkoopEntreekaartID") REFERENCES "Balieverkoop" ("BalieverkoopID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Belanghebbende" ADD CONSTRAINT "Fk_belanghebbende_rechtspersoon"
	FOREIGN KEY ("BelanghebbendeID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Belangtype" ADD CONSTRAINT "FK_Belangtype_Museumobject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "Museumobject" ("MuseumobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Belangtype" ADD CONSTRAINT "Fk_belangtype_belanghebbende"
	FOREIGN KEY ("BelanghebbendeID") REFERENCES "Belanghebbende" ("BelanghebbendeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doelgroep" ADD CONSTRAINT "FK_Doelgroep_Doelgroep"
	FOREIGN KEY ("DoelgroepID") REFERENCES "Doelgroep" ("DoelgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Entreekaart" ADD CONSTRAINT "Fk_entreekaart_product"
	FOREIGN KEY ("EntreekaartID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bruikleen_tentoonstelling" ADD CONSTRAINT "Fk_kp_bruikleen_tentoonstelling_tentoonstelling"
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bruikleen_tentoonstelling" ADD CONSTRAINT "Fk_kp_bruikleen_tentoonstelling_bruikleen"
	FOREIGN KEY ("BruikleenID") REFERENCES "Bruikleen" ("BruikleenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_collectie_museumobject" ADD CONSTRAINT "Fk_kp_collectie_museumobject_museumobject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "Museumobject" ("MuseumobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_collectie_museumobject" ADD CONSTRAINT "Fk_kp_collectie_museumobject_collectie"
	FOREIGN KEY ("CollectieID") REFERENCES "Collectie" ("CollectieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_incident_museumobject" ADD CONSTRAINT "Fk_kp_incident_museumobject_museumobject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "Museumobject" ("MuseumobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_incident_museumobject" ADD CONSTRAINT "Fk_kp_incident_museumobject_incident"
	FOREIGN KEY ("IncidentID") REFERENCES "Incident" ("IncidentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_lener_bruikleen" ADD CONSTRAINT "Fk_kp_lener_bruikleen_bruikleen"
	FOREIGN KEY ("BruikleenID") REFERENCES "Bruikleen" ("BruikleenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_lener_bruikleen" ADD CONSTRAINT "Fk_kp_lener_bruikleen_lener"
	FOREIGN KEY ("LenerID") REFERENCES "Lener" ("LenerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_mailing_museumrelatie" ADD CONSTRAINT "Fk_kp_mailing_museumrelatie_museumrelatie"
	FOREIGN KEY ("MuseumrelatieID") REFERENCES "Museumrelatie" ("MuseumrelatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_mailing_museumrelatie" ADD CONSTRAINT "Fk_kp_mailing_museumrelatie_mailing"
	FOREIGN KEY ("MailingID") REFERENCES "Mailing" ("MailingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_museumobject_tentoonstellin" ADD CONSTRAINT "Fk_kp_museumobject_tentoonstellin_tentoonstelling"
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_museumobject_tentoonstellin" ADD CONSTRAINT "Fk_kp_museumobject_tentoonstellin_museumobject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "Museumobject" ("MuseumobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_museumrelatie_doelgroep" ADD CONSTRAINT "Fk_kp_museumrelatie_doelgroep_doelgroep"
	FOREIGN KEY ("DoelgroepID") REFERENCES "Doelgroep" ("DoelgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_museumrelatie_doelgroep" ADD CONSTRAINT "Fk_kp_museumrelatie_doelgroep_museumrelatie"
	FOREIGN KEY ("MuseumrelatieID") REFERENCES "Museumrelatie" ("MuseumrelatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_product_omzetgroep" ADD CONSTRAINT "Fk_kp_product_omzetgroep_omzetgroep"
	FOREIGN KEY ("OmzetgroepID") REFERENCES "Omzetgroep" ("OmzetgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_product_omzetgroep" ADD CONSTRAINT "Fk_kp_product_omzetgroep_product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_product_productgroep" ADD CONSTRAINT "Fk_kp_product_productgroep_productgroep"
	FOREIGN KEY ("ProductgroepID") REFERENCES "Productgroep" ("ProductgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_product_productgroep" ADD CONSTRAINT "Fk_kp_product_productgroep_product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_programma_programmasoort" ADD CONSTRAINT "Fk_kp_programma_programmasoort_programmasoort"
	FOREIGN KEY ("ProgrammasoortID") REFERENCES "Programmasoort" ("ProgrammasoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_programma_programmasoort" ADD CONSTRAINT "Fk_kp_programma_programmasoort_programma"
	FOREIGN KEY ("ProgrammaID") REFERENCES "Programma" ("ProgrammaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_samensteller_tentoonstellin" ADD CONSTRAINT "Fk_kp_samensteller_tentoonstellin_tentoonstelling"
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_samensteller_tentoonstellin" ADD CONSTRAINT "Fk_kp_samensteller_tentoonstellin_samensteller"
	FOREIGN KEY ("SamenstellerID") REFERENCES "Samensteller" ("SamenstellerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Lener" ADD CONSTRAINT "Fk_lener_rechtspersoon"
	FOREIGN KEY ("LenerID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Museumobject" ADD CONSTRAINT "FK_Museumobject_Bruikleen"
	FOREIGN KEY ("BruikleenID") REFERENCES "Bruikleen" ("BruikleenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Museumobject" ADD CONSTRAINT "FK_Museumobject_Standplaats"
	FOREIGN KEY ("StandplaatsID") REFERENCES "Standplaats" ("StandplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Museumobject" ADD CONSTRAINT "Fk_museumobject_erfgoedObject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "ErfgoedObject" ("ErfgoedObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Museumrelatie" ADD CONSTRAINT "Fk_museumrelatie_rechtspersoon"
	FOREIGN KEY ("MuseumrelatieID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Prijs" ADD CONSTRAINT "fk_heeftPrijs_product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT fk_betreft_winkelvoorraaditem
	FOREIGN KEY ("WinkelvoorraaditemID") REFERENCES "Winkelvoorraaditem" ("WinkelvoorraaditemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "FK_Product_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Productie_eenheid" ADD CONSTRAINT "FK_Productie_eenheid_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Programma" ADD CONSTRAINT fk_voor_museumrelatie
	FOREIGN KEY ("MuseumrelatieID") REFERENCES "Museumrelatie" ("MuseumrelatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Programma" ADD CONSTRAINT "FK_Programma_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reservering" ADD CONSTRAINT fk_heeft_activiteit
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reservering" ADD CONSTRAINT "FK_Reservering_Productie_eenheid"
	FOREIGN KEY ("Productie_eenheidID") REFERENCES "Productie_eenheid" ("Productie-eenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reservering" ADD CONSTRAINT "FK_Reservering_Zaal"
	FOREIGN KEY ("ZaalID") REFERENCES "Zaal" ("ZaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reservering" ADD CONSTRAINT "FK_Reservering_Voorziening"
	FOREIGN KEY ("VoorzieningID") REFERENCES "Voorziening" ("VoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rol" ADD CONSTRAINT "FK_Rol_Museumobject"
	FOREIGN KEY ("MuseumobjectID") REFERENCES "Museumobject" ("MuseumobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rol" ADD CONSTRAINT "Fk_rol_historischPersoon"
	FOREIGN KEY ("HistorischPersoonID") REFERENCES "HistorischPersoon" ("HistorischPersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rondleiding" ADD CONSTRAINT "FK_Rondleiding_Tentoonstelling"
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Samensteller" ADD CONSTRAINT "Fk_samensteller_medewerker"
	FOREIGN KEY ("SamenstellerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaal" ADD CONSTRAINT fk_tentoonstelling_zaal
	FOREIGN KEY ("TentoonstellingID") REFERENCES "Tentoonstelling" ("TentoonstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aantal" ADD CONSTRAINT "PK_Aantal"
	PRIMARY KEY ("AantalID");

ALTER TABLE "Belijning" ADD CONSTRAINT "PK_Belijning"
	PRIMARY KEY ("BelijningID");

ALTER TABLE "Bezetting" ADD CONSTRAINT "PK_Bezetting"
	PRIMARY KEY ("BezettingID");

ALTER TABLE "Binnenlocatie" ADD CONSTRAINT "PK_Binnenlocatie"
	PRIMARY KEY ("BinnenlocatieID");

ALTER TABLE "Onderhoudskosten" ADD CONSTRAINT "PK_Onderhoudskosten"
	PRIMARY KEY ("OnderhoudskostenID");

ALTER TABLE "Sport" ADD CONSTRAINT "PK_Sport"
	PRIMARY KEY ("SportID");

ALTER TABLE "Sportlocatie" ADD CONSTRAINT "PK_Sportlocatie"
	PRIMARY KEY ("SportlocatieID");

ALTER TABLE "Sportmateriaal" ADD CONSTRAINT "PK_Sportmateriaal"
	PRIMARY KEY ("SportmateriaalID");

ALTER TABLE "Sportpark" ADD CONSTRAINT "PK_Sportpark"
	PRIMARY KEY ("SportparkID");

ALTER TABLE "Sportvereniging" ADD CONSTRAINT "PK_Sportvereniging"
	PRIMARY KEY ("SportverenigingID");

ALTER TABLE "Veld" ADD CONSTRAINT "PK_Veld"
	PRIMARY KEY ("VeldID");

ALTER TABLE "Binnenlocatie" ADD CONSTRAINT "Fk_binnenlocatie_sportlocatie"
	FOREIGN KEY ("BinnenlocatieID") REFERENCES "Sportlocatie" ("SportlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Binnenlocatie" ADD CONSTRAINT "FK_Binnenlocatie_Verblijfsobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Verblijfsobject" ("VerblijfsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Binnenlocatie" ADD CONSTRAINT "FK_Binnenlocatie_Wijk"
	FOREIGN KEY ("WijkID") REFERENCES "Wijk" ("WijkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_binnenlocatie_belijning" ADD CONSTRAINT "Fk_kp_binnenlocatie_belijning_belijning"
	FOREIGN KEY ("BelijningID") REFERENCES "Belijning" ("BelijningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_binnenlocatie_belijning" ADD CONSTRAINT "Fk_kp_binnenlocatie_belijning_binnenlocatie"
	FOREIGN KEY ("BinnenlocatieID") REFERENCES "Binnenlocatie" ("BinnenlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_binnenlocatie_sportmateriaa" ADD CONSTRAINT "Fk_kp_binnenlocatie_sportmateriaa_sportmateriaal"
	FOREIGN KEY ("SportmateriaalID") REFERENCES "Sportmateriaal" ("SportmateriaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_binnenlocatie_sportmateriaa" ADD CONSTRAINT "Fk_kp_binnenlocatie_sportmateriaa_binnenlocatie"
	FOREIGN KEY ("BinnenlocatieID") REFERENCES "Binnenlocatie" ("BinnenlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sportvereniging_sport" ADD CONSTRAINT "Fk_kp_sportvereniging_sport_sport"
	FOREIGN KEY ("SportID") REFERENCES "Sport" ("SportID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sportvereniging_sport" ADD CONSTRAINT "Fk_kp_sportvereniging_sport_sportvereniging"
	FOREIGN KEY ("SportverenigingID") REFERENCES "Sportvereniging" ("SportverenigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sportvereniging_sportlocati" ADD CONSTRAINT "Fk_kp_sportvereniging_sportlocati_sportlocatie"
	FOREIGN KEY ("SportlocatieID") REFERENCES "Sportlocatie" ("SportlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sportvereniging_sportlocati" ADD CONSTRAINT "Fk_kp_sportvereniging_sportlocati_sportvereniging"
	FOREIGN KEY ("SportverenigingID") REFERENCES "Sportvereniging" ("SportverenigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_veld_belijning" ADD CONSTRAINT "Fk_kp_veld_belijning_belijning"
	FOREIGN KEY ("BelijningID") REFERENCES "Belijning" ("BelijningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_veld_belijning" ADD CONSTRAINT "Fk_kp_veld_belijning_veld"
	FOREIGN KEY ("VeldID") REFERENCES "Veld" ("VeldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sportpark" ADD CONSTRAINT "Fk_sportpark_sportlocatie"
	FOREIGN KEY ("SportparkID") REFERENCES "Sportlocatie" ("SportlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sportvereniging" ADD CONSTRAINT "Fk_sportvereniging_nietnatuurlijkpersoon"
	FOREIGN KEY ("SportverenigingID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Veld" ADD CONSTRAINT fk_heeft_sportpark
	FOREIGN KEY ("SportparkID") REFERENCES "Sportpark" ("SportparkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gemeentebegrafenis" ADD CONSTRAINT "PK_Gemeentebegrafenis"
	PRIMARY KEY ("GemeentebegrafenisID");

ALTER TABLE "Brutonettoinkomsten" ADD CONSTRAINT "PK_Brutonettoinkomsten"
	PRIMARY KEY ("BrutonettoinkomstenID");

ALTER TABLE "Cdsrtinkomstenverhouding" ADD CONSTRAINT "PK_Cdsrtinkomstenverhouding"
	PRIMARY KEY ("CdsrtinkomstenverhoudingID");

ALTER TABLE "Cdszwet" ADD CONSTRAINT "PK_Cdszwet"
	PRIMARY KEY ("CdszwetID");

ALTER TABLE "Cduitkeringsperiode" ADD CONSTRAINT "PK_Cduitkeringsperiode"
	PRIMARY KEY ("CduitkeringsperiodeID");

ALTER TABLE "Codesoortvrijlating" ADD CONSTRAINT "PK_Codesoortvrijlating"
	PRIMARY KEY ("CodesoortvrijlatingID");

ALTER TABLE "Inkomstencomponenttype" ADD CONSTRAINT "PK_Inkomstencomponenttype"
	PRIMARY KEY ("InkomstencomponenttypeID");

ALTER TABLE "Inkomstensoortalimentatie" ADD CONSTRAINT "PK_Inkomstensoortalimentatie"
	PRIMARY KEY ("InkomstensoortalimentatieID");

ALTER TABLE "Inkomstensoortbetaaldwerk" ADD CONSTRAINT "PK_Inkomstensoortbetaaldwerk"
	PRIMARY KEY ("InkomstensoortbetaaldwerkID");

ALTER TABLE "Inkomstensoortpensioen" ADD CONSTRAINT "PK_Inkomstensoortpensioen"
	PRIMARY KEY ("InkomstensoortpensioenID");

ALTER TABLE "Inkomstensoortstudiefinancieri" ADD CONSTRAINT "PK_Inkomstensoortstudiefinancieri"
	PRIMARY KEY ("InkomstensoortstudiefinancieringID");

ALTER TABLE "Jsonruledgrouptype" ADD CONSTRAINT "PK_Jsonruledgrouptype"
	PRIMARY KEY ("JsonruledgrouptypeID");

ALTER TABLE "Onderhoudsplichttype" ADD CONSTRAINT "PK_Onderhoudsplichttype"
	PRIMARY KEY ("OnderhoudsplichttypeID");

ALTER TABLE "Soortcontract" ADD CONSTRAINT "PK_Soortcontract"
	PRIMARY KEY ("SoortcontractID");

ALTER TABLE "Alimentatie" ADD CONSTRAINT "PK_Alimentatie"
	PRIMARY KEY ("AlimentatieID");

ALTER TABLE "AnderInkomen" ADD CONSTRAINT "PK_AnderInkomen"
	PRIMARY KEY ("AnderInkomenID");

ALTER TABLE "BeslagOpInkomen" ADD CONSTRAINT "PK_BeslagOpInkomen"
	PRIMARY KEY ("BeslagOpInkomenID");

ALTER TABLE "BetaaldWerk" ADD CONSTRAINT "PK_BetaaldWerk"
	PRIMARY KEY ("BetaaldWerkID");

ALTER TABLE "DertiendeMaand_Eindejaarsui" ADD CONSTRAINT "PK_DertiendeMaand_Eindejaarsui"
	PRIMARY KEY ("DertiendeMaand-EindejaarsuitkeringID");

ALTER TABLE "Draagkracht" ADD CONSTRAINT "PK_Draagkracht"
	PRIMARY KEY ("DraagkrachtID");

ALTER TABLE "Draagkrachtregime" ADD CONSTRAINT "PK_Draagkrachtregime"
	PRIMARY KEY ("DraagkrachtregimeID");

ALTER TABLE "EigenBedrijf" ADD CONSTRAINT "PK_EigenBedrijf"
	PRIMARY KEY ("EigenBedrijfID");

ALTER TABLE "EigenBijdrage" ADD CONSTRAINT "PK_EigenBijdrage"
	PRIMARY KEY ("EigenBijdrageID");

ALTER TABLE "Heffingskorting" ADD CONSTRAINT "PK_Heffingskorting"
	PRIMARY KEY ("HeffingskortingID");

ALTER TABLE "Hobby" ADD CONSTRAINT "PK_Hobby"
	PRIMARY KEY ("HobbyID");

ALTER TABLE "Inkomstencomponent" ADD CONSTRAINT "PK_Inkomstencomponent"
	PRIMARY KEY ("InkomstencomponentID");

ALTER TABLE "Inkomstenverhouding" ADD CONSTRAINT "PK_Inkomstenverhouding"
	PRIMARY KEY ("InkomstenverhoudingID");

ALTER TABLE "Inkomstenvermindering" ADD CONSTRAINT "PK_Inkomstenvermindering"
	PRIMARY KEY ("InkomstenverminderingID");

ALTER TABLE "Kostencomponent" ADD CONSTRAINT "PK_Kostencomponent"
	PRIMARY KEY ("KostencomponentID");

ALTER TABLE "Loonbeslag" ADD CONSTRAINT "PK_Loonbeslag"
	PRIMARY KEY ("LoonbeslagID");

ALTER TABLE "Maaltijdvergoeding" ADD CONSTRAINT "PK_Maaltijdvergoeding"
	PRIMARY KEY ("MaaltijdvergoedingID");

ALTER TABLE "Onderhoudsplicht" ADD CONSTRAINT "PK_Onderhoudsplicht"
	PRIMARY KEY ("OnderhoudsplichtID");

ALTER TABLE "Onderhoudsverhouding" ADD CONSTRAINT "PK_Onderhoudsverhouding"
	PRIMARY KEY ("OnderhoudsverhoudingID");

ALTER TABLE "Onkostenvergoeding" ADD CONSTRAINT "PK_Onkostenvergoeding"
	PRIMARY KEY ("OnkostenvergoedingID");

ALTER TABLE "Pensioen" ADD CONSTRAINT "PK_Pensioen"
	PRIMARY KEY ("PensioenID");

ALTER TABLE "PrimairInkomstencomponent" ADD CONSTRAINT "PK_PrimairInkomstencomponent"
	PRIMARY KEY ("PrimairInkomstencomponentID");

ALTER TABLE "ReiskostenNaarHetWerk" ADD CONSTRAINT "PK_ReiskostenNaarHetWerk"
	PRIMARY KEY ("ReiskostenNaarHetWerkID");

ALTER TABLE "Reiskostenvergoeding" ADD CONSTRAINT "PK_Reiskostenvergoeding"
	PRIMARY KEY ("ReiskostenvergoedingID");

ALTER TABLE "SecundairInkomstencomponent" ADD CONSTRAINT "PK_SecundairInkomstencomponent"
	PRIMARY KEY ("SecundairInkomstencomponentID");

ALTER TABLE "Stage" ADD CONSTRAINT "PK_Stage"
	PRIMARY KEY ("StageID");

ALTER TABLE "Studiefinanciering" ADD CONSTRAINT "PK_Studiefinanciering"
	PRIMARY KEY ("StudiefinancieringID");

ALTER TABLE "TeBetalenAlimentatie" ADD CONSTRAINT "PK_TeBetalenAlimentatie"
	PRIMARY KEY ("TeBetalenAlimentatieID");

ALTER TABLE "Uitkering" ADD CONSTRAINT "PK_Uitkering"
	PRIMARY KEY ("UitkeringID");

ALTER TABLE "Vakantiegeld" ADD CONSTRAINT "PK_Vakantiegeld"
	PRIMARY KEY ("VakantiegeldID");

ALTER TABLE "Vergoeding" ADD CONSTRAINT "PK_Vergoeding"
	PRIMARY KEY ("VergoedingID");

ALTER TABLE "VergoedingInNatura" ADD CONSTRAINT "PK_VergoedingInNatura"
	PRIMARY KEY ("VergoedingInNaturaID");

ALTER TABLE "VerlagingDoorBoete" ADD CONSTRAINT "PK_VerlagingDoorBoete"
	PRIMARY KEY ("VerlagingDoorBoeteID");

ALTER TABLE "VerlagingDoorMaatregel" ADD CONSTRAINT "PK_VerlagingDoorMaatregel"
	PRIMARY KEY ("VerlagingDoorMaatregelID");

ALTER TABLE "VrijlatingInkomsten" ADD CONSTRAINT "PK_VrijlatingInkomsten"
	PRIMARY KEY ("VrijlatingInkomstenID");

ALTER TABLE "Alimentatie" ADD CONSTRAINT "Fk_alimentatie_primairInkomstencomponent"
	FOREIGN KEY ("AlimentatieID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AnderInkomen" ADD CONSTRAINT "Fk_anderInkomen_primairInkomstencomponent"
	FOREIGN KEY ("AnderInkomenID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeslagOpInkomen" ADD CONSTRAINT "Fk_beslagOpInkomen_kostencomponent"
	FOREIGN KEY ("BeslagOpInkomenID") REFERENCES "Kostencomponent" ("KostencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BetaaldWerk" ADD CONSTRAINT "Fk_betaaldWerk_primairInkomstencomponent"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "DertiendeMaand_Eindejaarsui" ADD CONSTRAINT "Fk_dertiendeMaand_Eindejaars_secundairInkomstencomponent"
	FOREIGN KEY ("DertiendeMaand_EindejaarsID") REFERENCES "SecundairInkomstencomponent" ("SecundairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "EigenBedrijf" ADD CONSTRAINT "Fk_eigenBedrijf_primairInkomstencomponent"
	FOREIGN KEY ("EigenBedrijfID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "EigenBijdrage" ADD CONSTRAINT "Fk_eigenBijdrage_kostencomponent"
	FOREIGN KEY ("EigenBijdrageID") REFERENCES "Kostencomponent" ("KostencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffingskorting" ADD CONSTRAINT "Fk_heffingskorting_secundairInkomstencomponent"
	FOREIGN KEY ("HeffingskortingID") REFERENCES "SecundairInkomstencomponent" ("SecundairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hobby" ADD CONSTRAINT "Fk_hobby_primairInkomstencomponent"
	FOREIGN KEY ("HobbyID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkomstenverhouding" ADD CONSTRAINT "FK_Inkomstenverhouding_PrimairInkomstencomponent"
	FOREIGN KEY ("PrimairInkomstencomponentID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkomstenvermindering" ADD CONSTRAINT "Fk_inkomstenvermindering_secundairInkomstencomponent"
	FOREIGN KEY ("InkomstenverminderingID") REFERENCES "SecundairInkomstencomponent" ("SecundairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_dertiendeMaan" ADD CONSTRAINT "Fk_kp_betaaldwerk_dertiendemaan_dertiendeMaand_Eindejaars"
	FOREIGN KEY ("DertiendeMaand_EindejaarsID") REFERENCES "DertiendeMaand_Eindejaarsui" ("DertiendeMaand-EindejaarsuitkeringID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_dertiendeMaan" ADD CONSTRAINT "Fk_kp_betaaldwerk_dertiendemaan_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_heffingskortin" ADD CONSTRAINT "Fk_kp_betaaldwerk_heffingskortin_heffingskorting"
	FOREIGN KEY ("HeffingskortingID") REFERENCES "Heffingskorting" ("HeffingskortingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_heffingskortin" ADD CONSTRAINT "Fk_kp_betaaldwerk_heffingskortin_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_loonbeslag" ADD CONSTRAINT "Fk_kp_betaaldwerk_loonbeslag_loonbeslag"
	FOREIGN KEY ("LoonbeslagID") REFERENCES "Loonbeslag" ("LoonbeslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_loonbeslag" ADD CONSTRAINT "Fk_kp_betaaldwerk_loonbeslag_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_maaltijdvergoe" ADD CONSTRAINT "Fk_kp_betaaldwerk_maaltijdvergoe_maaltijdvergoeding"
	FOREIGN KEY ("MaaltijdvergoedingID") REFERENCES "Maaltijdvergoeding" ("MaaltijdvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_maaltijdvergoe" ADD CONSTRAINT "Fk_kp_betaaldwerk_maaltijdvergoe_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_onkostenvergoe" ADD CONSTRAINT "Fk_kp_betaaldwerk_onkostenvergoe_onkostenvergoeding"
	FOREIGN KEY ("OnkostenvergoedingID") REFERENCES "Onkostenvergoeding" ("OnkostenvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_onkostenvergoe" ADD CONSTRAINT "Fk_kp_betaaldwerk_onkostenvergoe_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_reiskostenverg" ADD CONSTRAINT "Fk_kp_betaaldwerk_reiskostenverg_reiskostenvergoeding"
	FOREIGN KEY ("ReiskostenvergoedingID") REFERENCES "Reiskostenvergoeding" ("ReiskostenvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_reiskostenverg" ADD CONSTRAINT "Fk_kp_betaaldwerk_reiskostenverg_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_vakantiegeld" ADD CONSTRAINT "Fk_kp_betaaldwerk_vakantiegeld_vakantiegeld"
	FOREIGN KEY ("VakantiegeldID") REFERENCES "Vakantiegeld" ("VakantiegeldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_betaaldWerk_vakantiegeld" ADD CONSTRAINT "Fk_kp_betaaldwerk_vakantiegeld_betaaldWerk"
	FOREIGN KEY ("BetaaldWerkID") REFERENCES "BetaaldWerk" ("BetaaldWerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_draagkracht_draagkrachtregi" ADD CONSTRAINT "Fk_kp_draagkracht_draagkrachtregi_draagkrachtregime"
	FOREIGN KEY ("DraagkrachtregimeID") REFERENCES "Draagkrachtregime" ("DraagkrachtregimeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_draagkracht_draagkrachtregi" ADD CONSTRAINT "Fk_kp_draagkracht_draagkrachtregi_draagkracht"
	FOREIGN KEY ("DraagkrachtID") REFERENCES "Draagkracht" ("DraagkrachtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_onderhoudsverhouding_onderh" ADD CONSTRAINT "Fk_kp_onderhoudsverhouding_onderh_onderhoudsplicht"
	FOREIGN KEY ("OnderhoudsplichtID") REFERENCES "Onderhoudsplicht" ("OnderhoudsplichtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_onderhoudsverhouding_onderh" ADD CONSTRAINT "Fk_kp_onderhoudsverhouding_onderh_onderhoudsverhouding"
	FOREIGN KEY ("OnderhoudsverhoudingID") REFERENCES "Onderhoudsverhouding" ("OnderhoudsverhoudingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pensioen_loonbeslag" ADD CONSTRAINT "Fk_kp_pensioen_loonbeslag_loonbeslag"
	FOREIGN KEY ("LoonbeslagID") REFERENCES "Loonbeslag" ("LoonbeslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pensioen_loonbeslag" ADD CONSTRAINT "Fk_kp_pensioen_loonbeslag_pensioen"
	FOREIGN KEY ("PensioenID") REFERENCES "Pensioen" ("PensioenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pensioen_vakantiegeld" ADD CONSTRAINT "Fk_kp_pensioen_vakantiegeld_vakantiegeld"
	FOREIGN KEY ("VakantiegeldID") REFERENCES "Vakantiegeld" ("VakantiegeldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pensioen_vakantiegeld" ADD CONSTRAINT "Fk_kp_pensioen_vakantiegeld_pensioen"
	FOREIGN KEY ("PensioenID") REFERENCES "Pensioen" ("PensioenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_maaltijdvergoeding" ADD CONSTRAINT "Fk_kp_stage_maaltijdvergoeding_maaltijdvergoeding"
	FOREIGN KEY ("MaaltijdvergoedingID") REFERENCES "Maaltijdvergoeding" ("MaaltijdvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_maaltijdvergoeding" ADD CONSTRAINT "Fk_kp_stage_maaltijdvergoeding_stage"
	FOREIGN KEY ("StageID") REFERENCES "Stage" ("StageID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_onkostenvergoeding" ADD CONSTRAINT "Fk_kp_stage_onkostenvergoeding_onkostenvergoeding"
	FOREIGN KEY ("OnkostenvergoedingID") REFERENCES "Onkostenvergoeding" ("OnkostenvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_onkostenvergoeding" ADD CONSTRAINT "Fk_kp_stage_onkostenvergoeding_stage"
	FOREIGN KEY ("StageID") REFERENCES "Stage" ("StageID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_reiskostenvergoeding" ADD CONSTRAINT "Fk_kp_stage_reiskostenvergoeding_reiskostenvergoeding"
	FOREIGN KEY ("ReiskostenvergoedingID") REFERENCES "Reiskostenvergoeding" ("ReiskostenvergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_reiskostenvergoeding" ADD CONSTRAINT "Fk_kp_stage_reiskostenvergoeding_stage"
	FOREIGN KEY ("StageID") REFERENCES "Stage" ("StageID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_vergoedingInNatura" ADD CONSTRAINT "Fk_kp_stage_vergoedinginnatura_vergoedingInNatura"
	FOREIGN KEY ("VergoedingInNaturaID") REFERENCES "VergoedingInNatura" ("VergoedingInNaturaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_stage_vergoedingInNatura" ADD CONSTRAINT "Fk_kp_stage_vergoedinginnatura_stage"
	FOREIGN KEY ("StageID") REFERENCES "Stage" ("StageID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_loonbeslag" ADD CONSTRAINT "Fk_kp_uitkering_loonbeslag_loonbeslag"
	FOREIGN KEY ("LoonbeslagID") REFERENCES "Loonbeslag" ("LoonbeslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_loonbeslag" ADD CONSTRAINT "Fk_kp_uitkering_loonbeslag_uitkering"
	FOREIGN KEY ("UitkeringID") REFERENCES "Uitkering" ("UitkeringID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_vakantiegeld" ADD CONSTRAINT "Fk_kp_uitkering_vakantiegeld_vakantiegeld"
	FOREIGN KEY ("VakantiegeldID") REFERENCES "Vakantiegeld" ("VakantiegeldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_vakantiegeld" ADD CONSTRAINT "Fk_kp_uitkering_vakantiegeld_uitkering"
	FOREIGN KEY ("UitkeringID") REFERENCES "Uitkering" ("UitkeringID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_verlagingDoorBo" ADD CONSTRAINT "Fk_kp_uitkering_verlagingdoorbo_verlagingDoorBoete"
	FOREIGN KEY ("VerlagingDoorBoeteID") REFERENCES "VerlagingDoorBoete" ("VerlagingDoorBoeteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_verlagingDoorBo" ADD CONSTRAINT "Fk_kp_uitkering_verlagingdoorbo_uitkering"
	FOREIGN KEY ("UitkeringID") REFERENCES "Uitkering" ("UitkeringID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_verlagingDoorMa" ADD CONSTRAINT "Fk_kp_uitkering_verlagingdoorma_verlagingDoorMaatregel"
	FOREIGN KEY ("VerlagingDoorMaatregelID") REFERENCES "VerlagingDoorMaatregel" ("VerlagingDoorMaatregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitkering_verlagingDoorMa" ADD CONSTRAINT "Fk_kp_uitkering_verlagingdoorma_uitkering"
	FOREIGN KEY ("UitkeringID") REFERENCES "Uitkering" ("UitkeringID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Loonbeslag" ADD CONSTRAINT "Fk_loonbeslag_inkomstenvermindering"
	FOREIGN KEY ("LoonbeslagID") REFERENCES "Inkomstenvermindering" ("InkomstenverminderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Maaltijdvergoeding" ADD CONSTRAINT "Fk_maaltijdvergoeding_vergoeding"
	FOREIGN KEY ("MaaltijdvergoedingID") REFERENCES "Vergoeding" ("VergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onkostenvergoeding" ADD CONSTRAINT "Fk_onkostenvergoeding_vergoeding"
	FOREIGN KEY ("OnkostenvergoedingID") REFERENCES "Vergoeding" ("VergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pensioen" ADD CONSTRAINT "Fk_pensioen_primairInkomstencomponent"
	FOREIGN KEY ("PensioenID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "PrimairInkomstencomponent" ADD CONSTRAINT "Fk_primairInkomstencomponent_inkomstencomponent"
	FOREIGN KEY ("PrimairInkomstencomponentID") REFERENCES "Inkomstencomponent" ("InkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ReiskostenNaarHetWerk" ADD CONSTRAINT "Fk_reiskostenNaarHetWerk_kostencomponent"
	FOREIGN KEY ("ReiskostenNaarHetWerkID") REFERENCES "Kostencomponent" ("KostencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reiskostenvergoeding" ADD CONSTRAINT "Fk_reiskostenvergoeding_vergoeding"
	FOREIGN KEY ("ReiskostenvergoedingID") REFERENCES "Vergoeding" ("VergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "SecundairInkomstencomponent" ADD CONSTRAINT "Fk_secundairInkomstencomponent_inkomstencomponent"
	FOREIGN KEY ("SecundairInkomstencomponentID") REFERENCES "Inkomstencomponent" ("InkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stage" ADD CONSTRAINT "Fk_stage_primairInkomstencomponent"
	FOREIGN KEY ("StageID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Studiefinanciering" ADD CONSTRAINT "Fk_studiefinanciering_primairInkomstencomponent"
	FOREIGN KEY ("StudiefinancieringID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "TeBetalenAlimentatie" ADD CONSTRAINT "Fk_teBetalenAlimentatie_kostencomponent"
	FOREIGN KEY ("TeBetalenAlimentatieID") REFERENCES "Kostencomponent" ("KostencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitkering" ADD CONSTRAINT "Fk_uitkering_primairInkomstencomponent"
	FOREIGN KEY ("UitkeringID") REFERENCES "PrimairInkomstencomponent" ("PrimairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vakantiegeld" ADD CONSTRAINT "Fk_vakantiegeld_secundairInkomstencomponent"
	FOREIGN KEY ("VakantiegeldID") REFERENCES "SecundairInkomstencomponent" ("SecundairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vergoeding" ADD CONSTRAINT "Fk_vergoeding_secundairInkomstencomponent"
	FOREIGN KEY ("VergoedingID") REFERENCES "SecundairInkomstencomponent" ("SecundairInkomstencomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VergoedingInNatura" ADD CONSTRAINT "Fk_vergoedingInNatura_vergoeding"
	FOREIGN KEY ("VergoedingInNaturaID") REFERENCES "Vergoeding" ("VergoedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VerlagingDoorBoete" ADD CONSTRAINT "Fk_verlagingDoorBoete_inkomstenvermindering"
	FOREIGN KEY ("VerlagingDoorBoeteID") REFERENCES "Inkomstenvermindering" ("InkomstenverminderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VerlagingDoorMaatregel" ADD CONSTRAINT "Fk_verlagingDoorMaatregel_inkomstenvermindering"
	FOREIGN KEY ("VerlagingDoorMaatregelID") REFERENCES "Inkomstenvermindering" ("InkomstenverminderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Adrestype" ADD CONSTRAINT "PK_Adrestype"
	PRIMARY KEY ("AdrestypeID");

ALTER TABLE "Cdsrtvermogenscomponent" ADD CONSTRAINT "PK_Cdsrtvermogenscomponent"
	PRIMARY KEY ("CdsrtvermogenscomponentID");

ALTER TABLE "Cdsrtvoertuig" ADD CONSTRAINT "PK_Cdsrtvoertuig"
	PRIMARY KEY ("CdsrtvoertuigID");

ALTER TABLE "Cdsrtwaardevermogenscomponent" ADD CONSTRAINT "PK_Cdsrtwaardevermogenscomponent"
	PRIMARY KEY ("CdsrtwaardevermogenscomponentID");

ALTER TABLE "Bankrekening" ADD CONSTRAINT "PK_Bankrekening"
	PRIMARY KEY ("BankrekeningID");

ALTER TABLE "Hypotheek" ADD CONSTRAINT "PK_Hypotheek"
	PRIMARY KEY ("HypotheekID");

ALTER TABLE "Motorvoertuig" ADD CONSTRAINT "PK_Motorvoertuig"
	PRIMARY KEY ("MotorvoertuigID");

ALTER TABLE "OnroerendGoed" ADD CONSTRAINT "PK_OnroerendGoed"
	PRIMARY KEY ("OnroerendGoedID");

ALTER TABLE "Vermogenscomponent" ADD CONSTRAINT "PK_Vermogenscomponent"
	PRIMARY KEY ("VermogenscomponentID");

ALTER TABLE "Waardepeiling" ADD CONSTRAINT "PK_Waardepeiling"
	PRIMARY KEY ("WaardepeilingID");

ALTER TABLE "Bankrekening" ADD CONSTRAINT "Fk_bankrekening_vermogenscomponent"
	FOREIGN KEY ("BankrekeningID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hypotheek" ADD CONSTRAINT "Fk_hypotheek_vermogenscomponent"
	FOREIGN KEY ("HypotheekID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_client_bankrekening" ADD CONSTRAINT "Fk_kp_client_bankrekening_bankrekening"
	FOREIGN KEY ("BankrekeningID") REFERENCES "Bankrekening" ("BankrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hypotheek_onroerendGoed" ADD CONSTRAINT "Fk_kp_hypotheek_onroerendgoed_onroerendGoed"
	FOREIGN KEY ("OnroerendGoedID") REFERENCES "OnroerendGoed" ("OnroerendGoedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hypotheek_onroerendGoed" ADD CONSTRAINT "Fk_kp_hypotheek_onroerendgoed_hypotheek"
	FOREIGN KEY ("HypotheekID") REFERENCES "Hypotheek" ("HypotheekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_profiel_vermogenscomponent" ADD CONSTRAINT "Fk_kp_profiel_vermogenscomponent_vermogenscomponent"
	FOREIGN KEY ("VermogenscomponentID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vermogenscomponent_waardepe" ADD CONSTRAINT "Fk_kp_vermogenscomponent_waardepe_waardepeiling"
	FOREIGN KEY ("WaardepeilingID") REFERENCES "Waardepeiling" ("WaardepeilingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vermogenscomponent_waardepe" ADD CONSTRAINT "Fk_kp_vermogenscomponent_waardepe_vermogenscomponent"
	FOREIGN KEY ("VermogenscomponentID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Motorvoertuig" ADD CONSTRAINT "Fk_motorvoertuig_vermogenscomponent"
	FOREIGN KEY ("MotorvoertuigID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "OnroerendGoed" ADD CONSTRAINT "Fk_onroerendGoed_vermogenscomponent"
	FOREIGN KEY ("OnroerendGoedID") REFERENCES "Vermogenscomponent" ("VermogenscomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aom_aanvraagwmojeugd" ADD CONSTRAINT "PK_Aom_aanvraagwmojeugd"
	PRIMARY KEY ("Aom_aanvraagwmojeugdID");

ALTER TABLE "Aommeldingwmojeugd" ADD CONSTRAINT "PK_Aommeldingwmojeugd"
	PRIMARY KEY ("AommeldingwmojeugdID");

ALTER TABLE "Beperking" ADD CONSTRAINT "PK_Beperking"
	PRIMARY KEY ("BeperkingID");

ALTER TABLE "Beperkingscategorie" ADD CONSTRAINT "PK_Beperkingscategorie"
	PRIMARY KEY ("BeperkingscategorieID");

ALTER TABLE "Beperkingscore" ADD CONSTRAINT "PK_Beperkingscore"
	PRIMARY KEY ("BeperkingscoreID");

ALTER TABLE "Beperkingscoresoort" ADD CONSTRAINT "PK_Beperkingscoresoort"
	PRIMARY KEY ("BeperkingscoresoortID");

ALTER TABLE "Beschikking" ADD CONSTRAINT "PK_Beschikking"
	PRIMARY KEY ("BeschikkingID");

ALTER TABLE "Beschikkingsoort" ADD CONSTRAINT "PK_Beschikkingsoort"
	PRIMARY KEY ("BeschikkingsoortID");

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "PK_BeschikteVoorziening"
	PRIMARY KEY ("BeschikteVoorzieningID");

ALTER TABLE "Budgetuitputting" ADD CONSTRAINT "PK_Budgetuitputting"
	PRIMARY KEY ("BudgetuitputtingID");

ALTER TABLE "Declaratie" ADD CONSTRAINT "PK_Declaratie"
	PRIMARY KEY ("DeclaratieID");

ALTER TABLE "Declaratieregel" ADD CONSTRAINT "PK_Declaratieregel"
	PRIMARY KEY ("DeclaratieregelID");

ALTER TABLE "Leefgebied" ADD CONSTRAINT "PK_Leefgebied"
	PRIMARY KEY ("LeefgebiedID");

ALTER TABLE "Levering" ADD CONSTRAINT "PK_Levering"
	PRIMARY KEY ("LeveringID");

ALTER TABLE "Leveringsvorm" ADD CONSTRAINT "PK_Leveringsvorm"
	PRIMARY KEY ("LeveringsvormID");

ALTER TABLE "MeldingEigenBijdrage" ADD CONSTRAINT "PK_MeldingEigenBijdrage"
	PRIMARY KEY ("MeldingEigenBijdrageID");

ALTER TABLE "Pgb-toekenning" ADD CONSTRAINT "PK_Pgb-toekenning"
	PRIMARY KEY ("Pgb-toekenningID");

ALTER TABLE "Score" ADD CONSTRAINT "PK_Score"
	PRIMARY KEY ("ScoreID");

ALTER TABLE "Scoresoort" ADD CONSTRAINT "PK_Scoresoort"
	PRIMARY KEY ("ScoresoortID");

ALTER TABLE "Tarief" ADD CONSTRAINT "PK_Tarief"
	PRIMARY KEY ("TariefID");

ALTER TABLE "Team" ADD CONSTRAINT "PK_Team"
	PRIMARY KEY ("TeamID");

ALTER TABLE "Toewijzing" ADD CONSTRAINT "PK_Toewijzing"
	PRIMARY KEY ("ToewijzingID");

ALTER TABLE "VerplichtingWmoJeugd" ADD CONSTRAINT "PK_VerplichtingWmoJeugd"
	PRIMARY KEY ("VerplichtingWmoJeugdID");

ALTER TABLE "VerzoekOmToewijzing" ADD CONSTRAINT "PK_VerzoekOmToewijzing"
	PRIMARY KEY ("VerzoekOmToewijzingID");

ALTER TABLE "Voorziening" ADD CONSTRAINT "PK_Voorziening"
	PRIMARY KEY ("VoorzieningID");

ALTER TABLE "Voorzieningsoort" ADD CONSTRAINT "PK_Voorzieningsoort"
	PRIMARY KEY ("VoorzieningsoortID");

ALTER TABLE "Zelfredzaamheidmatrix" ADD CONSTRAINT "PK_Zelfredzaamheidmatrix"
	PRIMARY KEY ("ZelfredzaamheidmatrixID");

ALTER TABLE "Aom_aanvraagwmojeugd" ADD CONSTRAINT "FK_Aom_aanvraagwmojeugd_VerplichtingWmoJeugd"
	FOREIGN KEY ("VerplichtingWmoJeugdID") REFERENCES "VerplichtingWmoJeugd" ("VerplichtingWmoJeugdID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aom_aanvraagwmojeugd" ADD CONSTRAINT "Fk_aom_aanvraagwmojeugd_aanvraagofmelding"
	FOREIGN KEY ("Aom_aanvraagwmojeugdID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aommeldingwmojeugd" ADD CONSTRAINT "FK_AOMMeldingWMOJeugd_betreft"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aommeldingwmojeugd" ADD CONSTRAINT "Fk_aommeldingwmojeugd_aanvraagofmelding"
	FOREIGN KEY ("AommeldingwmojeugdID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beperking" ADD CONSTRAINT "FK_Beperking_is een"
	FOREIGN KEY ("BeperkingscategorieID") REFERENCES "Beperkingscategorie" ("BeperkingscategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beperking" ADD CONSTRAINT "FK_Beperking_is gebaseerd op"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beperkingscore" ADD CONSTRAINT "FK_Beperkingscore_Beperking"
	FOREIGN KEY ("BeperkingID") REFERENCES "Beperking" ("BeperkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beperkingscore" ADD CONSTRAINT "FK_Beperkingscore_is een"
	FOREIGN KEY ("BeperkingscoresoortID") REFERENCES "Beperkingscoresoort" ("BeperkingscoresoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beschikking" ADD CONSTRAINT "FK_Beschikking_leidt_tot"
	FOREIGN KEY ("Aom_aanvraagwmojeugdID") REFERENCES "Aom_aanvraagwmojeugd" ("Aom_aanvraagwmojeugdID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "FK_Beschikte Voorziening_heeft voorzieningen"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "FK_Beschikte Voorziening_heeft"
	FOREIGN KEY ("LeveringsvormID") REFERENCES "Leveringsvorm" ("LeveringsvormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "FK_Beschikte Voorziening_Toegewezen Product"
	FOREIGN KEY ("ToewijzingID") REFERENCES "Toewijzing" ("ToewijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "FK_Beschikte Voorziening_is voorziening"
	FOREIGN KEY ("VoorzieningID") REFERENCES "Voorziening" ("VoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BeschikteVoorziening" ADD CONSTRAINT "FK_BeschikteVoorziening_VerplichtingWmoJeugd"
	FOREIGN KEY ("VerplichtingWmoJeugdID") REFERENCES "VerplichtingWmoJeugd" ("VerplichtingWmoJeugdID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Budgetuitputting" ADD CONSTRAINT "FK_Budgetuitputting_betreft"
	FOREIGN KEY ("Pgb-toekenningID") REFERENCES "Pgb-toekenning" ("Pgb-toekenningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Declaratieregel" ADD CONSTRAINT "FK_Declaratieregel_is voor"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Declaratieregel" ADD CONSTRAINT "FK_Declaratieregel_valt binnen"
	FOREIGN KEY ("DeclaratieID") REFERENCES "Declaratie" ("DeclaratieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Declaratieregel" ADD CONSTRAINT "FK_Declaratieregel_is op basis van"
	FOREIGN KEY ("ToewijzingID") REFERENCES "Toewijzing" ("ToewijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Levering" ADD CONSTRAINT "FK_Levering_geleverde prestatie"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Levering" ADD CONSTRAINT "FK_Levering_voorziening"
	FOREIGN KEY ("VoorzieningID") REFERENCES "Voorziening" ("VoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Levering" ADD CONSTRAINT "FK_Levering_geleverde zorg"
	FOREIGN KEY ("ToewijzingID") REFERENCES "Toewijzing" ("ToewijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "MeldingEigenBijdrage" ADD CONSTRAINT "FK_Melding Eigen bijdrage_betreft"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "onderkent leefgebiieden" ADD CONSTRAINT "FK_onderkent leefgebiieden_Leefgebied"
	FOREIGN KEY ("LeefgebiedID") REFERENCES "Leefgebied" ("LeefgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "onderkent leefgebiieden" ADD CONSTRAINT "FK_onderkent leefgebiieden_Zelfredzaamheidmatrix"
	FOREIGN KEY ("ZelfredzaamheidmatrixID") REFERENCES "Zelfredzaamheidmatrix" ("ZelfredzaamheidmatrixID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "onderkent scores" ADD CONSTRAINT "FK_onderkent scores_Scoresoort"
	FOREIGN KEY ("ScoresoortID") REFERENCES "Scoresoort" ("ScoresoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "onderkent scores" ADD CONSTRAINT "FK_onderkent scores_Zelfredzaamheidmatrix"
	FOREIGN KEY ("ZelfredzaamheidmatrixID") REFERENCES "Zelfredzaamheidmatrix" ("ZelfredzaamheidmatrixID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pgb-toekenning" ADD CONSTRAINT "FK_PGB-Toekenning_betreft"
	FOREIGN KEY ("BeschikteVoorzieningID") REFERENCES "BeschikteVoorziening" ("BeschikteVoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Score" ADD CONSTRAINT "FK_Score_score bij leeggebied"
	FOREIGN KEY ("LeefgebiedID") REFERENCES "Leefgebied" ("LeefgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Score" ADD CONSTRAINT "FK_Score_hoogte score"
	FOREIGN KEY ("ScoresoortID") REFERENCES "Scoresoort" ("ScoresoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tarief" ADD CONSTRAINT "FK_Tarief_heeft"
	FOREIGN KEY ("VoorzieningID") REFERENCES "Voorziening" ("VoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tarief" ADD CONSTRAINT fk_bevat_contract
	FOREIGN KEY ("ContractID") REFERENCES "Contract" ("ContractID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Toewijzing" ADD CONSTRAINT "FK_Toewijzing_toewijzing"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VerplichtingWmoJeugd" ADD CONSTRAINT "Fk_verplichtingWmoJeugd_inkooporder"
	FOREIGN KEY ("VerplichtingWmoJeugdID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VerzoekOmToewijzing" ADD CONSTRAINT "FK_Verzoek om Toewijzing_leidt tot"
	FOREIGN KEY ("BeschikkingID") REFERENCES "Beschikking" ("BeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "VerzoekOmToewijzing" ADD CONSTRAINT "FK_Verzoek om Toewijzing_betreft"
	FOREIGN KEY ("VoorzieningID") REFERENCES "Voorziening" ("VoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Voorziening" ADD CONSTRAINT "FK_Voorziening_valt binnen"
	FOREIGN KEY ("VoorzieningsoortID") REFERENCES "Voorzieningsoort" ("VoorzieningsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Asielstatushouder" ADD CONSTRAINT "PK_Asielstatushouder"
	PRIMARY KEY ("AsielstatushouderID");

ALTER TABLE "B1" ADD CONSTRAINT "PK_B1"
	PRIMARY KEY ("B1ID");

ALTER TABLE "BredeIntake" ADD CONSTRAINT "PK_BredeIntake"
	PRIMARY KEY ("BredeIntakeID");

ALTER TABLE "Examen" ADD CONSTRAINT "PK_Examen"
	PRIMARY KEY ("ExamenID");

ALTER TABLE "Examenonderdeel" ADD CONSTRAINT "PK_Examenonderdeel"
	PRIMARY KEY ("ExamenonderdeelID");

ALTER TABLE "GezinsmigrantEnOverigeMigra" ADD CONSTRAINT "PK_GezinsmigrantEnOverigeMigra"
	PRIMARY KEY ("GezinsmigrantEnOverigeMigrant
ID");

ALTER TABLE "Inburgeraar" ADD CONSTRAINT "PK_Inburgeraar"
	PRIMARY KEY ("InburgeraarID");

ALTER TABLE "Inburgeringstraject" ADD CONSTRAINT "PK_Inburgeringstraject"
	PRIMARY KEY ("InburgeringstrajectID");

ALTER TABLE "Knm?" ADD CONSTRAINT "PK_Knm?"
	PRIMARY KEY ("Knm?ID");

ALTER TABLE "Leerroute" ADD CONSTRAINT "PK_Leerroute"
	PRIMARY KEY ("LeerrouteID");

ALTER TABLE "Map" ADD CONSTRAINT "PK_Map"
	PRIMARY KEY ("MapID");

ALTER TABLE "Onderwijs" ADD CONSTRAINT "PK_Onderwijs"
	PRIMARY KEY ("OnderwijsID");

ALTER TABLE "Participatiecomponent" ADD CONSTRAINT "PK_Participatiecomponent"
	PRIMARY KEY ("ParticipatiecomponentID");

ALTER TABLE "Pip" ADD CONSTRAINT "PK_Pip"
	PRIMARY KEY ("PipID");

ALTER TABLE "Pvt" ADD CONSTRAINT "PK_Pvt"
	PRIMARY KEY ("PvtID");

ALTER TABLE "Verblijfplaats" ADD CONSTRAINT "PK_Verblijfplaats"
	PRIMARY KEY ("VerblijfplaatsID");

ALTER TABLE "VerblijfplaatsAzc" ADD CONSTRAINT "PK_VerblijfplaatsAzc"
	PRIMARY KEY ("VerblijfplaatsAzcID");

ALTER TABLE "Vreemdeling" ADD CONSTRAINT "PK_Vreemdeling"
	PRIMARY KEY ("VreemdelingID");

ALTER TABLE "Z" ADD CONSTRAINT "PK_Z"
	PRIMARY KEY ("ZID");

ALTER TABLE "Asielstatushouder" ADD CONSTRAINT "FK_Asielstatushouder_VerblijfplaatsAzc"
	FOREIGN KEY ("VerblijfplaatsAzcID") REFERENCES "VerblijfplaatsAzc" ("VerblijfplaatsAzcID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Asielstatushouder" ADD CONSTRAINT "Fk_asielstatushouder_inburgeraar"
	FOREIGN KEY ("AsielstatushouderID") REFERENCES "Inburgeraar" ("InburgeraarID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Asielstatushouder" ADD CONSTRAINT "FK_Asielstatushouder_Gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "B1" ADD CONSTRAINT "Fk_b1_leerroute"
	FOREIGN KEY ("B1ID") REFERENCES "Leerroute" ("LeerrouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BredeIntake" ADD CONSTRAINT "fk_leidtTot_pip"
	FOREIGN KEY ("PipID") REFERENCES "Pip" ("PipID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Examenonderdeel" ADD CONSTRAINT "FK_Examenonderdeel_Examen"
	FOREIGN KEY ("ExamenID") REFERENCES "Examen" ("ExamenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "GezinsmigrantEnOverigeMigra" ADD CONSTRAINT "Fk_gezinsmigrantEnOverigeMig_inburgeraar"
	FOREIGN KEY ("GezinsmigrantEnOverigeMigID") REFERENCES "Inburgeraar" ("InburgeraarID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeraar" ADD CONSTRAINT "Fk_inburgeraar_vreemdeling"
	FOREIGN KEY ("InburgeraarID") REFERENCES "Vreemdeling" ("VreemdelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeraar" ADD CONSTRAINT fk_heeft_inburgeringstraject
	FOREIGN KEY ("InburgeringstrajectID") REFERENCES "Inburgeringstraject" ("InburgeringstrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeringstraject" ADD CONSTRAINT "fk_onderdeelVan_bredeIntake"
	FOREIGN KEY ("BredeIntakeID") REFERENCES "BredeIntake" ("BredeIntakeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeringstraject" ADD CONSTRAINT "fk_afgerondMet_examen"
	FOREIGN KEY ("ExamenID") REFERENCES "Examen" ("ExamenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeringstraject" ADD CONSTRAINT "fk_onderdeelVan_map"
	FOREIGN KEY ("MapID") REFERENCES "Map" ("MapID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inburgeringstraject" ADD CONSTRAINT "fk_onderdeelVan_pvt"
	FOREIGN KEY ("PvtID") REFERENCES "Pvt" ("PvtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leerroute" ADD CONSTRAINT "fk_onderdeelVan_knm?"
	FOREIGN KEY ("Knm?ID") REFERENCES "Knm?" ("Knm?ID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onderwijs" ADD CONSTRAINT "Fk_onderwijs_leerroute"
	FOREIGN KEY ("OnderwijsID") REFERENCES "Leerroute" ("LeerrouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Participatiecomponent" ADD CONSTRAINT "FK_Participatiecomponent_Z"
	FOREIGN KEY ("ZID") REFERENCES "Z" ("ZID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pip" ADD CONSTRAINT "fk_afgesprokenIn_leerroute"
	FOREIGN KEY ("LeerrouteID") REFERENCES "Leerroute" ("LeerrouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vreemdeling" ADD CONSTRAINT "Fk_vreemdeling_natuurlijkpersoon"
	FOREIGN KEY ("VreemdelingID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Z" ADD CONSTRAINT "Fk_z_leerroute"
	FOREIGN KEY ("ZID") REFERENCES "Leerroute" ("LeerrouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_enumSocialeGroep" ADD CONSTRAINT "PK_Enum_enumSocialeGroep"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_enumSocialeRelatie" ADD CONSTRAINT "PK_Enum_enumSocialeRelatie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_incidenttype" ADD CONSTRAINT "PK_Enum_incidenttype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_leefgebied" ADD CONSTRAINT "PK_Enum_leefgebied"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_verzoeksoort" ADD CONSTRAINT "PK_Enum_verzoeksoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Informering" ADD CONSTRAINT "PK_Informering"
	PRIMARY KEY ("InformeringID");

ALTER TABLE "Leefgebied" ADD CONSTRAINT "PK_Leefgebied"
	PRIMARY KEY ("LeefgebiedID");

ALTER TABLE "ZorgelijkeSituatie" ADD CONSTRAINT "PK_ZorgelijkeSituatie"
	PRIMARY KEY ("ZorgelijkeSituatieID");

ALTER TABLE "Zorgmelding" ADD CONSTRAINT "PK_Zorgmelding"
	PRIMARY KEY ("ZorgmeldingID");

ALTER TABLE "Informering" ADD CONSTRAINT "FK_Informering_Natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zorgmelding_medewerker" ADD CONSTRAINT "Fk_kp_zorgmelding_medewerker_zorgmelding"
	FOREIGN KEY ("ZorgmeldingID") REFERENCES "Zorgmelding" ("ZorgmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zorgmelding_medewerker" ADD CONSTRAINT "Fk_kp_zorgmelding_medewerker_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zorgmelding_natuurlijkperso" ADD CONSTRAINT "Fk_kp_zorgmelding_natuurlijkperso_zorgmelding"
	FOREIGN KEY ("ZorgmeldingID") REFERENCES "Zorgmelding" ("ZorgmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zorgmelding_natuurlijkperso" ADD CONSTRAINT "Fk_kp_zorgmelding_natuurlijkperso_natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leefgebied" ADD CONSTRAINT "fk_toelichting_zorgelijkeSitua"
	FOREIGN KEY ("ZorgelijkeSituatieID") REFERENCES "ZorgelijkeSituatie" ("ZorgelijkeSituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ZorgelijkeSituatie" ADD CONSTRAINT "fk_naarAanleidingVan_zorgmeldi"
	FOREIGN KEY ("ZorgmeldingID") REFERENCES "Zorgmelding" ("ZorgmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zorgmelding" ADD CONSTRAINT "Fk_zorgmelding_aanvraagofmelding"
	FOREIGN KEY ("ZorgmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zorgmelding" ADD CONSTRAINT "FK_Zorgmelding_Natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Component" ADD CONSTRAINT "PK_Component"
	PRIMARY KEY ("ComponentID");

ALTER TABLE "Componentsoort" ADD CONSTRAINT "PK_Componentsoort"
	PRIMARY KEY ("ComponentsoortID");

ALTER TABLE "Doelgroep" ADD CONSTRAINT "PK_Doelgroep"
	PRIMARY KEY ("DoelgroepID");

ALTER TABLE "Enum_verstrekkingsvormsoort" ADD CONSTRAINT "PK_Enum_verstrekkingsvormsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Fraudegegevens" ADD CONSTRAINT "PK_Fraudegegevens"
	PRIMARY KEY ("FraudegegevensID");

ALTER TABLE "Fraudesoort" ADD CONSTRAINT "PK_Fraudesoort"
	PRIMARY KEY ("FraudesoortID");

ALTER TABLE "Huisvestingsoort" ADD CONSTRAINT "PK_Huisvestingsoort"
	PRIMARY KEY ("HuisvestingsoortID");

ALTER TABLE "Informatiedakloosheid" ADD CONSTRAINT "PK_Informatiedakloosheid"
	PRIMARY KEY ("InformatiedakloosheidID");

ALTER TABLE "Inkomensvoorziening" ADD CONSTRAINT "PK_Inkomensvoorziening"
	PRIMARY KEY ("InkomensvoorzieningID");

ALTER TABLE "Inkomensvoorzieningsoort" ADD CONSTRAINT "PK_Inkomensvoorzieningsoort"
	PRIMARY KEY ("InkomensvoorzieningsoortID");

ALTER TABLE "Participatiedossier" ADD CONSTRAINT "PK_Participatiedossier"
	PRIMARY KEY ("ParticipatiedossierID");

ALTER TABLE "Redenbeeindiging" ADD CONSTRAINT "PK_Redenbeeindiging"
	PRIMARY KEY ("RedenbeeindigingID");

ALTER TABLE "Redenblokkering" ADD CONSTRAINT "PK_Redenblokkering"
	PRIMARY KEY ("RedenblokkeringID");

ALTER TABLE "Redeninstroom" ADD CONSTRAINT "PK_Redeninstroom"
	PRIMARY KEY ("RedeninstroomID");

ALTER TABLE "Redenuitstroom" ADD CONSTRAINT "PK_Redenuitstroom"
	PRIMARY KEY ("RedenuitstroomID");

ALTER TABLE "Regeling" ADD CONSTRAINT "PK_Regeling"
	PRIMARY KEY ("RegelingID");

ALTER TABLE "Regelingsoort" ADD CONSTRAINT "PK_Regelingsoort"
	PRIMARY KEY ("RegelingsoortID");

ALTER TABLE "Taalniveau" ADD CONSTRAINT "PK_Taalniveau"
	PRIMARY KEY ("TaalniveauID");

ALTER TABLE "Tegenprestatie" ADD CONSTRAINT "PK_Tegenprestatie"
	PRIMARY KEY ("TegenprestatieID");

ALTER TABLE "Tegenprestatiehoogte" ADD CONSTRAINT "PK_Tegenprestatiehoogte"
	PRIMARY KEY ("TegenprestatiehoogteID");

ALTER TABLE "Traject" ADD CONSTRAINT "PK_Traject"
	PRIMARY KEY ("TrajectID");

ALTER TABLE "Trajectactiviteit" ADD CONSTRAINT "PK_Trajectactiviteit"
	PRIMARY KEY ("TrajectactiviteitID");

ALTER TABLE "Trajectactiviteitsoort" ADD CONSTRAINT "PK_Trajectactiviteitsoort"
	PRIMARY KEY ("TrajectactiviteitsoortID");

ALTER TABLE "Trajectsoort" ADD CONSTRAINT "PK_Trajectsoort"
	PRIMARY KEY ("TrajectsoortID");

ALTER TABLE "Uitkeringsrun" ADD CONSTRAINT "PK_Uitkeringsrun"
	PRIMARY KEY ("UitkeringsrunID");

ALTER TABLE "Component" ADD CONSTRAINT "FK_Component_Uitkeringsrun"
	FOREIGN KEY ("UitkeringsrunID") REFERENCES "Uitkeringsrun" ("UitkeringsrunID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Component" ADD CONSTRAINT "FK_Component_Trajectactiviteit"
	FOREIGN KEY ("TrajectactiviteitID") REFERENCES "Trajectactiviteit" ("TrajectactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Component" ADD CONSTRAINT "FK_Component_Componentsoort"
	FOREIGN KEY ("ComponentsoortID") REFERENCES "Componentsoort" ("ComponentsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Component" ADD CONSTRAINT "fk_isOpgebouwdUit_inkomensvoor"
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Fraudegegevens" ADD CONSTRAINT "FK_Fraudegegevens_Fraudesoort"
	FOREIGN KEY ("FraudesoortID") REFERENCES "Fraudesoort" ("FraudesoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Fraudegegevens" ADD CONSTRAINT "fk_heeftFinancieleSituatie_ing"
	FOREIGN KEY ("IngeschrevenpersoonID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Huisvestingsoort" ADD CONSTRAINT fk_soorthuisvesting_inkomensvo
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkomensvoorziening" ADD CONSTRAINT "fk_isSoortVoorziening_inkomens"
	FOREIGN KEY ("InkomensvoorzieningsoortID") REFERENCES "Inkomensvoorzieningsoort" ("InkomensvoorzieningsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkomensvoorziening" ADD CONSTRAINT "fk_heeftUitkering_ingeschreven"
	FOREIGN KEY ("IngeschrevenpersoonID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_client_inkomensvoorziening" ADD CONSTRAINT "Fk_kp_client_inkomensvoorziening_inkomensvoorziening"
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_client_taalniveau" ADD CONSTRAINT "Fk_kp_client_taalniveau_taalniveau"
	FOREIGN KEY ("TaalniveauID") REFERENCES "Taalniveau" ("TaalniveauID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_trajectsoort_trajectactivit" ADD CONSTRAINT "Fk_kp_trajectsoort_trajectactivit_trajectactiviteitsoort"
	FOREIGN KEY ("TrajectactiviteitsoortID") REFERENCES "Trajectactiviteitsoort" ("TrajectactiviteitsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_trajectsoort_trajectactivit" ADD CONSTRAINT "Fk_kp_trajectsoort_trajectactivit_trajectsoort"
	FOREIGN KEY ("TrajectsoortID") REFERENCES "Trajectsoort" ("TrajectsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Redenblokkering" ADD CONSTRAINT fk_redenblokkering_inkomensvoo
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Redeninstroom" ADD CONSTRAINT fk_redeninstroom_inkomensvoorz
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Redenuitstroom" ADD CONSTRAINT fk_redenuistroom_inkomensvoorz
	FOREIGN KEY ("InkomensvoorzieningID") REFERENCES "Inkomensvoorziening" ("InkomensvoorzieningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Regeling" ADD CONSTRAINT "FK_Regeling_Regelingsoort"
	FOREIGN KEY ("RegelingsoortID") REFERENCES "Regelingsoort" ("RegelingsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Regeling" ADD CONSTRAINT fk_ingeschrevenpersoon_regelin
	FOREIGN KEY ("IngeschrevenpersoonID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tegenprestatie" ADD CONSTRAINT "FK_Tegenprestatie_Tegenprestatiehoogte"
	FOREIGN KEY ("TegenprestatiehoogteID") REFERENCES "Tegenprestatiehoogte" ("TegenprestatiehoogteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Traject" ADD CONSTRAINT "FK_Traject_Redenbeeindiging"
	FOREIGN KEY ("RedenbeeindigingID") REFERENCES "Redenbeeindiging" ("RedenbeeindigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Traject" ADD CONSTRAINT "FK_Traject_Trajectsoort"
	FOREIGN KEY ("TrajectsoortID") REFERENCES "Trajectsoort" ("TrajectsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Trajectactiviteit" ADD CONSTRAINT fk_heeft_traject
	FOREIGN KEY ("TrajectID") REFERENCES "Traject" ("TrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Trajectactiviteitsoort" ADD CONSTRAINT "fk_isActiviteitsoort_trajectac"
	FOREIGN KEY ("TrajectactiviteitID") REFERENCES "Trajectactiviteit" ("TrajectactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Trajectsoort" ADD CONSTRAINT "FK_Trajectsoort_Doelgroep"
	FOREIGN KEY ("DoelgroepID") REFERENCES "Doelgroep" ("DoelgroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanmelding" ADD CONSTRAINT "PK_Aanmelding"
	PRIMARY KEY ("AanmeldingID");

ALTER TABLE "Begeleiding" ADD CONSTRAINT "PK_Begeleiding"
	PRIMARY KEY ("BegeleidingID");

ALTER TABLE "Begeleidingssoort" ADD CONSTRAINT "PK_Begeleidingssoort"
	PRIMARY KEY ("BegeleidingssoortID");

ALTER TABLE "Contactpersoon" ADD CONSTRAINT "PK_Contactpersoon"
	PRIMARY KEY ("ContactpersoonID");

ALTER TABLE "Crisisinterventie" ADD CONSTRAINT "PK_Crisisinterventie"
	PRIMARY KEY ("CrisisinterventieID");

ALTER TABLE "Enumbegeleidingssoort" ADD CONSTRAINT "PK_Enumbegeleidingssoort"
	PRIMARY KEY ("EnumbegeleidingssoortID");

ALTER TABLE "Enumbeschikkingssoort" ADD CONSTRAINT "PK_Enumbeschikkingssoort"
	PRIMARY KEY ("EnumbeschikkingssoortID");

ALTER TABLE "Enumhuishoudenssoort" ADD CONSTRAINT "PK_Enumhuishoudenssoort"
	PRIMARY KEY ("EnumhuishoudenssoortID");

ALTER TABLE "Enumoplossingssoort" ADD CONSTRAINT "PK_Enumoplossingssoort"
	PRIMARY KEY ("EnumoplossingssoortID");

ALTER TABLE "Enumschuldensoort" ADD CONSTRAINT "PK_Enumschuldensoort"
	PRIMARY KEY ("EnumschuldensoortID");

ALTER TABLE "Enumuitstroomreden" ADD CONSTRAINT "PK_Enumuitstroomreden"
	PRIMARY KEY ("EnumuitstroomredenID");

ALTER TABLE "Enumwoningbezit" ADD CONSTRAINT "PK_Enumwoningbezit"
	PRIMARY KEY ("EnumwoningbezitID");

ALTER TABLE "Informatieenadvies" ADD CONSTRAINT "PK_Informatieenadvies"
	PRIMARY KEY ("InformatieenadviesID");

ALTER TABLE "Inkomen" ADD CONSTRAINT "PK_Inkomen"
	PRIMARY KEY ("InkomenID");

ALTER TABLE "Intake" ADD CONSTRAINT "PK_Intake"
	PRIMARY KEY ("IntakeID");

ALTER TABLE "Leefsituatie" ADD CONSTRAINT "PK_Leefsituatie"
	PRIMARY KEY ("LeefsituatieID");

ALTER TABLE "Moratorium" ADD CONSTRAINT "PK_Moratorium"
	PRIMARY KEY ("MoratoriumID");

ALTER TABLE "Nazorg" ADD CONSTRAINT "PK_Nazorg"
	PRIMARY KEY ("NazorgID");

ALTER TABLE "Ondernemer" ADD CONSTRAINT "PK_Ondernemer"
	PRIMARY KEY ("OndernemerID");

ALTER TABLE "Oplossing" ADD CONSTRAINT "PK_Oplossing"
	PRIMARY KEY ("OplossingID");

ALTER TABLE "Oplossingssoort" ADD CONSTRAINT "PK_Oplossingssoort"
	PRIMARY KEY ("OplossingssoortID");

ALTER TABLE "Partner" ADD CONSTRAINT "PK_Partner"
	PRIMARY KEY ("PartnerID");

ALTER TABLE "Planvanaanpak" ADD CONSTRAINT "PK_Planvanaanpak"
	PRIMARY KEY ("PlanvanaanpakID");

ALTER TABLE "Schuld" ADD CONSTRAINT "PK_Schuld"
	PRIMARY KEY ("SchuldID");

ALTER TABLE "Schuldeiser" ADD CONSTRAINT "PK_Schuldeiser"
	PRIMARY KEY ("SchuldeiserID");

ALTER TABLE "Schuldhulporganisatie" ADD CONSTRAINT "PK_Schuldhulporganisatie"
	PRIMARY KEY ("SchuldhulporganisatieID");

ALTER TABLE "Schuldhulptraject" ADD CONSTRAINT "PK_Schuldhulptraject"
	PRIMARY KEY ("SchuldhulptrajectID");

ALTER TABLE "Schuldregeling" ADD CONSTRAINT "PK_Schuldregeling"
	PRIMARY KEY ("SchuldregelingID");

ALTER TABLE "Stabilisatie" ADD CONSTRAINT "PK_Stabilisatie"
	PRIMARY KEY ("StabilisatieID");

ALTER TABLE "Uitstroom" ADD CONSTRAINT "PK_Uitstroom"
	PRIMARY KEY ("UitstroomID");

ALTER TABLE "Voorlopigevoorziening" ADD CONSTRAINT "PK_Voorlopigevoorziening"
	PRIMARY KEY ("VoorlopigevoorzieningID");

ALTER TABLE "Woningbezit" ADD CONSTRAINT "PK_Woningbezit"
	PRIMARY KEY ("WoningbezitID");

ALTER TABLE "Wsnp_traject" ADD CONSTRAINT "PK_Wsnp_traject"
	PRIMARY KEY ("Wsnp-trajectID");

ALTER TABLE "Wsnp_verklaring" ADD CONSTRAINT "PK_Wsnp_verklaring"
	PRIMARY KEY ("Wsnp-verklaringID");

ALTER TABLE "Aanmelding" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begeleiding" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY (begeleiding) REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begeleiding" ADD CONSTRAINT "fk_resulteertIn_schuldregeling"
	FOREIGN KEY ("SchuldregelingID") REFERENCES "Schuldregeling" ("SchuldregelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begeleiding" ADD CONSTRAINT "FK_Begeleiding_Begeleidingssoort"
	FOREIGN KEY ("BegeleidingssoortID") REFERENCES "Begeleidingssoort" ("BegeleidingssoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begeleiding" ADD CONSTRAINT "fk_resulteertIn_stabilisatie"
	FOREIGN KEY ("StabilisatieID") REFERENCES "Stabilisatie" ("StabilisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begeleiding" ADD CONSTRAINT "fk_resulteertIn_intake"
	FOREIGN KEY ("IntakeID") REFERENCES "Intake" ("IntakeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Crisisinterventie" ADD CONSTRAINT "fk_kanHebben_schuldhulptraject"
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Informatieenadvies" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Informatieenadvies" ADD CONSTRAINT "fk_resulteertIn_intake"
	FOREIGN KEY ("IntakeID") REFERENCES "Intake" ("IntakeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkomen" ADD CONSTRAINT fk_heeft_leefsituatie
	FOREIGN KEY (inkomen) REFERENCES "Leefsituatie" ("LeefsituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Intake" ADD CONSTRAINT "fk_resulteertIn_aanmelding"
	FOREIGN KEY ("AanmeldingID") REFERENCES "Aanmelding" ("AanmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Intake" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leefsituatie_woningbezit" ADD CONSTRAINT "Fk_kp_leefsituatie_woningbezit_woningbezit"
	FOREIGN KEY ("WoningbezitID") REFERENCES "Woningbezit" ("WoningbezitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leefsituatie_woningbezit" ADD CONSTRAINT "Fk_kp_leefsituatie_woningbezit_koopwoning"
	FOREIGN KEY (koopwoning) REFERENCES "Leefsituatie" ("LeefsituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_begel" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_begel_begeleidingssoort"
	FOREIGN KEY ("BegeleidingssoortID") REFERENCES "Begeleidingssoort" ("BegeleidingssoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_begel" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_begel_schuldhulporganisatie"
	FOREIGN KEY ("SchuldhulporganisatieID") REFERENCES "Schuldhulporganisatie" ("SchuldhulporganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_conta" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_conta_contactpersoon"
	FOREIGN KEY ("ContactpersoonID") REFERENCES "Contactpersoon" ("ContactpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_conta" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_conta_contactpersonen"
	FOREIGN KEY (contactpersonen) REFERENCES "Schuldhulporganisatie" ("SchuldhulporganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_oplos" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_oplos_oplossingssoort"
	FOREIGN KEY ("OplossingssoortID") REFERENCES "Oplossingssoort" ("OplossingssoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_oplos" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_oplos_schuldhulporganisatie"
	FOREIGN KEY ("SchuldhulporganisatieID") REFERENCES "Schuldhulporganisatie" ("SchuldhulporganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_schul" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_schul_schuldhulptraject"
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulporganisatie_schul" ADD CONSTRAINT "Fk_kp_schuldhulporganisatie_schul_schuldhulporganisatie"
	FOREIGN KEY ("SchuldhulporganisatieID") REFERENCES "Schuldhulporganisatie" ("SchuldhulporganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_schuldhulptraject_client" ADD CONSTRAINT "Fk_kp_schuldhulptraject_client_client"
	FOREIGN KEY (client) REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Moratorium" ADD CONSTRAINT "fk_kanHebben_schuldhulptraject"
	FOREIGN KEY (moratoria) REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nazorg" ADD CONSTRAINT "fk_resulteertIn_begeleiding"
	FOREIGN KEY ("BegeleidingID") REFERENCES "Begeleiding" ("BegeleidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nazorg" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nazorg" ADD CONSTRAINT "fk_resulteertIn_oplossing"
	FOREIGN KEY ("OplossingID") REFERENCES "Oplossing" ("OplossingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ondernemer" ADD CONSTRAINT fk_is_leefsituatie
	FOREIGN KEY ("LeefsituatieID") REFERENCES "Leefsituatie" ("LeefsituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Oplossing" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Oplossing" ADD CONSTRAINT "fk_resulteertIn_schuldregeling"
	FOREIGN KEY ("SchuldregelingID") REFERENCES "Schuldregeling" ("SchuldregelingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Oplossing" ADD CONSTRAINT "FK_Oplossing_Oplossingssoort"
	FOREIGN KEY ("OplossingssoortID") REFERENCES "Oplossingssoort" ("OplossingssoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Partner" ADD CONSTRAINT fk_heeft_leefsituatie
	FOREIGN KEY (partner) REFERENCES "Leefsituatie" ("LeefsituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Partner" ADD CONSTRAINT "Fk_partner_natuurlijkpersoon"
	FOREIGN KEY ("PartnerID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Planvanaanpak" ADD CONSTRAINT fk_heeft_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuld" ADD CONSTRAINT fk_heeft_schuldhulptraject
	FOREIGN KEY (schulden) REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuld" ADD CONSTRAINT "FK_Schuld_Schuldeiser"
	FOREIGN KEY ("SchuldeiserID") REFERENCES "Schuldeiser" ("SchuldeiserID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuldeiser" ADD CONSTRAINT "Fk_schuldeiser_rechtspersoon"
	FOREIGN KEY ("SchuldeiserID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuldhulporganisatie" ADD CONSTRAINT "Fk_schuldhulporganisatie_nietnatuurlijkpersoon"
	FOREIGN KEY ("SchuldhulporganisatieID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuldhulptraject" ADD CONSTRAINT "FK_Schuldhulptraject_Gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuldregeling" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schuldregeling" ADD CONSTRAINT "fk_resulteertIn_stabilisatie"
	FOREIGN KEY ("StabilisatieID") REFERENCES "Stabilisatie" ("StabilisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stabilisatie" ADD CONSTRAINT "fk_resulteertIn_intake"
	FOREIGN KEY ("IntakeID") REFERENCES "Intake" ("IntakeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stabilisatie" ADD CONSTRAINT fk_bevat_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitstroom" ADD CONSTRAINT fk_uitstroom_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Voorlopigevoorziening" ADD CONSTRAINT fk_heeft_schuldhulptraject
	FOREIGN KEY ("SchuldhulptrajectID") REFERENCES "Schuldhulptraject" ("SchuldhulptrajectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Wsnp_traject" ADD CONSTRAINT "FK_Wsnp_traject_Leefsituatie"
	FOREIGN KEY ("LeefsituatieID") REFERENCES "Leefsituatie" ("LeefsituatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Behandeling" ADD CONSTRAINT "PK_Behandeling"
	PRIMARY KEY ("BehandelingID");

ALTER TABLE "Behandelsoort" ADD CONSTRAINT "PK_Behandelsoort"
	PRIMARY KEY ("BehandelsoortID");

ALTER TABLE "Bijzonderheid" ADD CONSTRAINT "PK_Bijzonderheid"
	PRIMARY KEY ("BijzonderheidID");

ALTER TABLE "Bijzonderheidsoort" ADD CONSTRAINT "PK_Bijzonderheidsoort"
	PRIMARY KEY ("BijzonderheidsoortID");

ALTER TABLE "Caseaanmelding" ADD CONSTRAINT "PK_Caseaanmelding"
	PRIMARY KEY ("CaseaanmeldingID");

ALTER TABLE "Doelstelling" ADD CONSTRAINT "PK_Doelstelling"
	PRIMARY KEY ("DoelstellingID");

ALTER TABLE "Doelstellingsoort" ADD CONSTRAINT "PK_Doelstellingsoort"
	PRIMARY KEY ("DoelstellingsoortID");

ALTER TABLE "Sociaalteamdossier" ADD CONSTRAINT "PK_Sociaalteamdossier"
	PRIMARY KEY ("SociaalteamdossierID");

ALTER TABLE "Sociaalteamdossiersoort" ADD CONSTRAINT "PK_Sociaalteamdossiersoort"
	PRIMARY KEY ("SociaalteamdossiersoortID");

ALTER TABLE "Behandeling" ADD CONSTRAINT "FK_Behandeling_Behandelsoort"
	FOREIGN KEY ("BehandelsoortID") REFERENCES "Behandelsoort" ("BehandelsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Behandeling" ADD CONSTRAINT "fk_heeftBehandeling_sociaaltea"
	FOREIGN KEY ("SociaalteamdossierID") REFERENCES "Sociaalteamdossier" ("SociaalteamdossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bijzonderheid" ADD CONSTRAINT "FK_Bijzonderheid_Bijzonderheidsoort"
	FOREIGN KEY ("BijzonderheidsoortID") REFERENCES "Bijzonderheidsoort" ("BijzonderheidsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bijzonderheid" ADD CONSTRAINT "fk_heeftBijzonderheid_sociaalt"
	FOREIGN KEY ("SociaalteamdossierID") REFERENCES "Sociaalteamdossier" ("SociaalteamdossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Caseaanmelding" ADD CONSTRAINT "fk_heeftAanmelding_sociaalteam"
	FOREIGN KEY ("SociaalteamdossierID") REFERENCES "Sociaalteamdossier" ("SociaalteamdossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doelstelling" ADD CONSTRAINT "FK_Doelstelling_Doelstellingsoort"
	FOREIGN KEY ("DoelstellingsoortID") REFERENCES "Doelstellingsoort" ("DoelstellingsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doelstelling" ADD CONSTRAINT "fk_heeftDoelstelling_sociaalte"
	FOREIGN KEY ("SociaalteamdossierID") REFERENCES "Sociaalteamdossier" ("SociaalteamdossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sociaalteamdossier_relatie" ADD CONSTRAINT "Fk_kp_sociaalteamdossier_relatie_sociaalteamdossier"
	FOREIGN KEY ("SociaalteamdossierID") REFERENCES "Sociaalteamdossier" ("SociaalteamdossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sociaalteamdossier" ADD CONSTRAINT "FK_Sociaalteamdossier_Sociaalteamdossiersoort"
	FOREIGN KEY ("SociaalteamdossiersoortID") REFERENCES "Sociaalteamdossiersoort" ("SociaalteamdossiersoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Categorie" ADD CONSTRAINT "PK_Categorie"
	PRIMARY KEY ("CategorieID");

ALTER TABLE "Container" ADD CONSTRAINT "PK_Container"
	PRIMARY KEY ("ContainerID");

ALTER TABLE "Containertype" ADD CONSTRAINT "PK_Containertype"
	PRIMARY KEY ("ContainertypeID");

ALTER TABLE "Enum_routesoort" ADD CONSTRAINT "PK_Enum_routesoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Fractie" ADD CONSTRAINT "PK_Fractie"
	PRIMARY KEY ("FractieID");

ALTER TABLE "Locatie" ADD CONSTRAINT "PK_Locatie"
	PRIMARY KEY ("LocatieID");

ALTER TABLE "Melding" ADD CONSTRAINT "PK_Melding"
	PRIMARY KEY ("MeldingID");

ALTER TABLE "Milieustraat" ADD CONSTRAINT "PK_Milieustraat"
	PRIMARY KEY ("MilieustraatID");

ALTER TABLE "Ophaalmoment" ADD CONSTRAINT "PK_Ophaalmoment"
	PRIMARY KEY ("OphaalmomentID");

ALTER TABLE "Pas" ADD CONSTRAINT "PK_Pas"
	PRIMARY KEY ("PasID");

ALTER TABLE "Prijsafspraak" ADD CONSTRAINT "PK_Prijsafspraak"
	PRIMARY KEY ("PrijsafspraakID");

ALTER TABLE "Prijsregel" ADD CONSTRAINT "PK_Prijsregel"
	PRIMARY KEY ("PrijsregelID");

ALTER TABLE "Rit" ADD CONSTRAINT "PK_Rit"
	PRIMARY KEY ("RitID");

ALTER TABLE "Route" ADD CONSTRAINT "PK_Route"
	PRIMARY KEY ("RouteID");

ALTER TABLE "Storting" ADD CONSTRAINT "PK_Storting"
	PRIMARY KEY ("StortingID");

ALTER TABLE "Vuilniswagen" ADD CONSTRAINT "PK_Vuilniswagen"
	PRIMARY KEY ("VuilniswagenID");

ALTER TABLE "Vulgraadmeting" ADD CONSTRAINT "PK_Vulgraadmeting"
	PRIMARY KEY ("VulgraadmetingID");

ALTER TABLE "Container" ADD CONSTRAINT "FK_Container_Fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Container" ADD CONSTRAINT "FK_Container_Locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Container" ADD CONSTRAINT "FK_Container_Containertype"
	FOREIGN KEY ("ContainertypeID") REFERENCES "Containertype" ("ContainertypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_milieustraat_fractie" ADD CONSTRAINT "Fk_kp_milieustraat_fractie_fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_milieustraat_fractie" ADD CONSTRAINT "Fk_kp_milieustraat_fractie_milieustraat"
	FOREIGN KEY ("MilieustraatID") REFERENCES "Milieustraat" ("MilieustraatID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pas_milieustraat" ADD CONSTRAINT "Fk_kp_pas_milieustraat_milieustraat"
	FOREIGN KEY ("MilieustraatID") REFERENCES "Milieustraat" ("MilieustraatID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_pas_milieustraat" ADD CONSTRAINT "Fk_kp_pas_milieustraat_pas"
	FOREIGN KEY ("PasID") REFERENCES "Pas" ("PasID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_storting_fractie" ADD CONSTRAINT "Fk_kp_storting_fractie_fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_storting_fractie" ADD CONSTRAINT "Fk_kp_storting_fractie_storting"
	FOREIGN KEY ("StortingID") REFERENCES "Storting" ("StortingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vuilniswagen_containertype" ADD CONSTRAINT "Fk_kp_vuilniswagen_containertype_containertype"
	FOREIGN KEY ("ContainertypeID") REFERENCES "Containertype" ("ContainertypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vuilniswagen_containertype" ADD CONSTRAINT "Fk_kp_vuilniswagen_containertype_vuilniswagen"
	FOREIGN KEY ("VuilniswagenID") REFERENCES "Vuilniswagen" ("VuilniswagenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Locatie" ADD CONSTRAINT "fk_gaatLangs_route"
	FOREIGN KEY ("RouteID") REFERENCES "Route" ("RouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Categorie"
	FOREIGN KEY ("CategorieID") REFERENCES "Categorie" ("CategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Containertype"
	FOREIGN KEY ("ContainertypeID") REFERENCES "Containertype" ("ContainertypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "Fk_melding_aanvraagofmelding"
	FOREIGN KEY ("MeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ophaalmoment" ADD CONSTRAINT "FK_Ophaalmoment_Container"
	FOREIGN KEY ("ContainerID") REFERENCES "Container" ("ContainerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ophaalmoment" ADD CONSTRAINT "FK_Ophaalmoment_Locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ophaalmoment" ADD CONSTRAINT fk_heeft_rit
	FOREIGN KEY ("RitID") REFERENCES "Rit" ("RitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Prijsregel" ADD CONSTRAINT "FK_Prijsregel_Fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Prijsregel" ADD CONSTRAINT fk_heeft_prijsafspraak
	FOREIGN KEY ("PrijsafspraakID") REFERENCES "Prijsafspraak" ("PrijsafspraakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rit" ADD CONSTRAINT "FK_Rit_Route"
	FOREIGN KEY ("RouteID") REFERENCES "Route" ("RouteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rit" ADD CONSTRAINT "FK_Rit_Vuilniswagen"
	FOREIGN KEY ("VuilniswagenID") REFERENCES "Vuilniswagen" ("VuilniswagenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Route" ADD CONSTRAINT "FK_Route_Fractie"
	FOREIGN KEY ("FractieID") REFERENCES "Fractie" ("FractieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Storting" ADD CONSTRAINT "FK_Storting_Milieustraat"
	FOREIGN KEY ("MilieustraatID") REFERENCES "Milieustraat" ("MilieustraatID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Storting" ADD CONSTRAINT "fk_uitgevoerdeStorting_pas"
	FOREIGN KEY ("PasID") REFERENCES "Pas" ("PasID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vulgraadmeting" ADD CONSTRAINT fk_heeft_container
	FOREIGN KEY ("ContainerID") REFERENCES "Container" ("ContainerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebouw" ADD CONSTRAINT "PK_Gebouw"
	PRIMARY KEY ("GebouwID");

ALTER TABLE "Huurwoningen" ADD CONSTRAINT "PK_Huurwoningen"
	PRIMARY KEY ("HuurwoningenID");

ALTER TABLE "Koopwoningen" ADD CONSTRAINT "PK_Koopwoningen"
	PRIMARY KEY ("KoopwoningenID");

ALTER TABLE "Plan" ADD CONSTRAINT "PK_Plan"
	PRIMARY KEY ("PlanID");

ALTER TABLE "Projectleider" ADD CONSTRAINT "PK_Projectleider"
	PRIMARY KEY ("ProjectleiderID");

ALTER TABLE "Projectontwikkelaar" ADD CONSTRAINT "PK_Projectontwikkelaar"
	PRIMARY KEY ("ProjectontwikkelaarID");

ALTER TABLE "Studentenwoningen" ADD CONSTRAINT "PK_Studentenwoningen"
	PRIMARY KEY ("StudentenwoningenID");

ALTER TABLE "Gebouw" ADD CONSTRAINT "fk_bestaatUit_plan"
	FOREIGN KEY ("PlanID") REFERENCES "Plan" ("PlanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Huurwoningen" ADD CONSTRAINT "Fk_huurwoningen_gebouw"
	FOREIGN KEY ("HuurwoningenID") REFERENCES "Gebouw" ("GebouwID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Koopwoningen" ADD CONSTRAINT "Fk_koopwoningen_gebouw"
	FOREIGN KEY ("KoopwoningenID") REFERENCES "Gebouw" ("GebouwID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_projectontwikkelaar_plan" ADD CONSTRAINT "Fk_kp_projectontwikkelaar_plan_plan"
	FOREIGN KEY ("PlanID") REFERENCES "Plan" ("PlanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_projectontwikkelaar_plan" ADD CONSTRAINT "Fk_kp_projectontwikkelaar_plan_projectontwikkelaar"
	FOREIGN KEY ("ProjectontwikkelaarID") REFERENCES "Projectontwikkelaar" ("ProjectontwikkelaarID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Plan" ADD CONSTRAINT "fk_isProjectleiderVan_projectl"
	FOREIGN KEY ("ProjectleiderID") REFERENCES "Projectleider" ("ProjectleiderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Plan" ADD CONSTRAINT "fk_binnenProgramma_programma"
	FOREIGN KEY ("ProgrammaID") REFERENCES "Programma" ("ProgrammaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectleider" ADD CONSTRAINT "Fk_projectleider_natuurlijkpersoon"
	FOREIGN KEY ("ProjectleiderID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectontwikkelaar" ADD CONSTRAINT "Fk_projectontwikkelaar_nietnatuurlijkpersoon"
	FOREIGN KEY ("ProjectontwikkelaarID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Studentenwoningen" ADD CONSTRAINT "Fk_studentenwoningen_gebouw"
	FOREIGN KEY ("StudentenwoningenID") REFERENCES "Gebouw" ("GebouwID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Actie" ADD CONSTRAINT "PK_Actie"
	PRIMARY KEY ("ActieID");

ALTER TABLE "Areaal" ADD CONSTRAINT "PK_Areaal"
	PRIMARY KEY ("AreaalID");

ALTER TABLE "Crow_melding" ADD CONSTRAINT "PK_Crow_melding"
	PRIMARY KEY ("Crow-meldingID");

ALTER TABLE "Deelplan_veld" ADD CONSTRAINT "PK_Deelplan_veld"
	PRIMARY KEY ("Deelplan/veldID");

ALTER TABLE "Enum_crow_kwaliteitsniveaus" ADD CONSTRAINT "PK_Enum_crow_kwaliteitsniveaus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_energielabel" ADD CONSTRAINT "PK_Enum_energielabel"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_oppervlakteWoning" ADD CONSTRAINT "PK_Enum_oppervlakteWoning"
	PRIMARY KEY ("ID");

ALTER TABLE "Fase_oplevering" ADD CONSTRAINT "PK_Fase_oplevering"
	PRIMARY KEY ("Fase/opleveringID");

ALTER TABLE "Geo_object" ADD CONSTRAINT "PK_Geo_object"
	PRIMARY KEY ("Geo-objectID");

ALTER TABLE "Grondbeheerder" ADD CONSTRAINT "PK_Grondbeheerder"
	PRIMARY KEY ("GrondbeheerderID");

ALTER TABLE "Inspectie" ADD CONSTRAINT "PK_Inspectie"
	PRIMARY KEY ("InspectieID");

ALTER TABLE "Kadastralemutatie" ADD CONSTRAINT "PK_Kadastralemutatie"
	PRIMARY KEY ("KadastralemutatieID");

ALTER TABLE "KwaliteitscatalogusOpenbareR" ADD CONSTRAINT "PK_KwaliteitscatalogusOpenbareR"
	PRIMARY KEY ("KwaliteitscatalogusOpenbareRuimteID");

ALTER TABLE "Kwaliteitskenmerken" ADD CONSTRAINT "PK_Kwaliteitskenmerken"
	PRIMARY KEY ("KwaliteitskenmerkenID");

ALTER TABLE "Logboek" ADD CONSTRAINT "PK_Logboek"
	PRIMARY KEY ("LogboekID");

ALTER TABLE "Melding" ADD CONSTRAINT "PK_Melding"
	PRIMARY KEY ("MeldingID");

ALTER TABLE "Meldingongeval" ADD CONSTRAINT "PK_Meldingongeval"
	PRIMARY KEY ("MeldingongevalID");

ALTER TABLE "Moor_melding" ADD CONSTRAINT "PK_Moor_melding"
	PRIMARY KEY ("Moor-meldingID");

ALTER TABLE "Omgevingsvergunning" ADD CONSTRAINT "PK_Omgevingsvergunning"
	PRIMARY KEY ("OmgevingsvergunningID");

ALTER TABLE "Onderhoud" ADD CONSTRAINT "PK_Onderhoud"
	PRIMARY KEY ("OnderhoudID");

ALTER TABLE "Opbreking" ADD CONSTRAINT "PK_Opbreking"
	PRIMARY KEY ("OpbrekingID");

ALTER TABLE "Proces_verbaal_moor_melding" ADD CONSTRAINT "PK_Proces_verbaal_moor_melding"
	PRIMARY KEY ("Proces-verbaal-moor-meldingID");

ALTER TABLE "Schouwronde" ADD CONSTRAINT "PK_Schouwronde"
	PRIMARY KEY ("SchouwrondeID");

ALTER TABLE "Storing" ADD CONSTRAINT "PK_Storing"
	PRIMARY KEY ("StoringID");

ALTER TABLE "Taak" ADD CONSTRAINT "PK_Taak"
	PRIMARY KEY ("TaakID");

ALTER TABLE "UitvoerderGraafwerkzaamheden" ADD CONSTRAINT "PK_UitvoerderGraafwerkzaamheden"
	PRIMARY KEY ("UitvoerderGraafwerkzaamhedenID");

ALTER TABLE "Verkeerslicht" ADD CONSTRAINT "PK_Verkeerslicht"
	PRIMARY KEY ("VerkeerslichtID");

ALTER TABLE "Actie" ADD CONSTRAINT "Fk_actie_melding"
	FOREIGN KEY ("ActieID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Crow_melding" ADD CONSTRAINT "FK_Crow_melding_KwaliteitscatalogusOpenbareR"
	FOREIGN KEY ("KwaliteitscatalogusOpenbareID") REFERENCES "KwaliteitscatalogusOpenbareR" ("KwaliteitscatalogusOpenbareRuimteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Crow_melding" ADD CONSTRAINT "Fk_crow_melding_melding"
	FOREIGN KEY ("Crow_meldingID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Grondbeheerder" ADD CONSTRAINT "Fk_grondbeheerder_rechtspersoon"
	FOREIGN KEY ("GrondbeheerderID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inspectie" ADD CONSTRAINT "Fk_inspectie_melding"
	FOREIGN KEY ("InspectieID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_buurt" ADD CONSTRAINT "Fk_kp_areaal_buurt_areaal"
	FOREIGN KEY ("AreaalID") REFERENCES "Areaal" ("AreaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_buurt" ADD CONSTRAINT "Fk_kp_areaal_buurt_buurt"
	FOREIGN KEY ("BuurtID") REFERENCES "Buurt" ("BuurtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_schouwronde" ADD CONSTRAINT "Fk_kp_areaal_schouwronde_schouwronde"
	FOREIGN KEY ("SchouwrondeID") REFERENCES "Schouwronde" ("SchouwrondeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_schouwronde" ADD CONSTRAINT "Fk_kp_areaal_schouwronde_areaal"
	FOREIGN KEY ("AreaalID") REFERENCES "Areaal" ("AreaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_wijk" ADD CONSTRAINT "Fk_kp_areaal_wijk_areaal"
	FOREIGN KEY ("AreaalID") REFERENCES "Areaal" ("AreaalID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_areaal_wijk" ADD CONSTRAINT "Fk_kp_areaal_wijk_wijk"
	FOREIGN KEY ("WijkID") REFERENCES "Wijk" ("WijkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kadastralemutatie_kadastral" ADD CONSTRAINT "Fk_kp_kadastralemutatie_kadastral_kadastralemutatie"
	FOREIGN KEY ("KadastralemutatieID") REFERENCES "Kadastralemutatie" ("KadastralemutatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kadastralemutatie_kadastral" ADD CONSTRAINT "Fk_kp_kadastralemutatie_kadastral_kadastraleonroerendezaak"
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_rechtspersoon_kadastralemut" ADD CONSTRAINT "Fk_kp_rechtspersoon_kadastralemut_kadastralemutatie"
	FOREIGN KEY ("KadastralemutatieID") REFERENCES "Kadastralemutatie" ("KadastralemutatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_rechtspersoon_kadastralemut" ADD CONSTRAINT "Fk_kp_rechtspersoon_kadastralemut_rechtspersoon"
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitvoerderGraafwerkzaamhed" ADD CONSTRAINT "Fk_kp_uitvoerdergraafwerkzaamhed_opbreking"
	FOREIGN KEY ("OpbrekingID") REFERENCES "Opbreking" ("OpbrekingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_uitvoerderGraafwerkzaamhed" ADD CONSTRAINT "Fk_kp_uitvoerdergraafwerkzaamhed_uitvoerderGraafwerkzaamhede"
	FOREIGN KEY ("UitvoerderGraafwerkzaamhedeID") REFERENCES "UitvoerderGraafwerkzaamheden" ("UitvoerderGraafwerkzaamhedenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Logboek" ADD CONSTRAINT fk_heeft_beheerobject
	FOREIGN KEY ("BeheerobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT fk_bevat_logboek
	FOREIGN KEY ("LogboekID") REFERENCES "Logboek" ("LogboekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT fk_heeft_schouwronde
	FOREIGN KEY ("SchouwrondeID") REFERENCES "Schouwronde" ("SchouwrondeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Melding" ADD CONSTRAINT "FK_Melding_Natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Meldingongeval" ADD CONSTRAINT "Fk_meldingongeval_melding"
	FOREIGN KEY ("MeldingongevalID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Moor_melding" ADD CONSTRAINT "FK_Moor_melding_Omgevingsvergunning"
	FOREIGN KEY ("OmgevingsvergunningID") REFERENCES "Omgevingsvergunning" ("OmgevingsvergunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Moor_melding" ADD CONSTRAINT "fk_doet_uitvoerderGraafwerkzaa"
	FOREIGN KEY ("UitvoerderGraafwerkzaamhedeID") REFERENCES "UitvoerderGraafwerkzaamheden" ("UitvoerderGraafwerkzaamhedenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Omgevingsvergunning" ADD CONSTRAINT "FK_Omgevingsvergunning_Plan"
	FOREIGN KEY ("PlanID") REFERENCES "Plan" ("PlanID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Opbreking" ADD CONSTRAINT fk_betreft_moor_melding
	FOREIGN KEY ("Moor_meldingID") REFERENCES "Moor_melding" ("Moor-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Proces_verbaal_moor_melding" ADD CONSTRAINT fk_betreft_moor_melding
	FOREIGN KEY ("Moor_meldingID") REFERENCES "Moor_melding" ("Moor-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Proces_verbaal_moor_melding" ADD CONSTRAINT "FK_Proces_verbaal_moor_melding_Document"
	FOREIGN KEY ("DocumentID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Proces_verbaal_moor_melding" ADD CONSTRAINT fk_verleent_medewerker
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Schouwronde" ADD CONSTRAINT "fk_voertUit_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Storing" ADD CONSTRAINT "Fk_storing_melding"
	FOREIGN KEY ("StoringID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "UitvoerderGraafwerkzaamheden" ADD CONSTRAINT "Fk_uitvoerderGraafwerkzaamhede_grondbeheerder"
	FOREIGN KEY ("UitvoerderGraafwerkzaamhedeID") REFERENCES "Grondbeheerder" ("GrondbeheerderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "UitvoerderGraafwerkzaamheden" ADD CONSTRAINT "Fk_uitvoerderGraafwerkzaamhede_leverancier"
	FOREIGN KEY ("UitvoerderGraafwerkzaamhedeID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_aanofvrijliggend" ADD CONSTRAINT "PK_Enum_aanofvrijliggend"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_afmeting" ADD CONSTRAINT "PK_Enum_afmeting"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_bedienaar" ADD CONSTRAINT "PK_Enum_bedienaar"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_beheergebied" ADD CONSTRAINT "PK_Enum_beheergebied"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_beheerobjectgebruiksfunct" ADD CONSTRAINT "PK_Enum_beheerobjectgebruiksfunct"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_belasting" ADD CONSTRAINT "PK_Enum_belasting"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_belastingklassenieuw" ADD CONSTRAINT "PK_Enum_belastingklassenieuw"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_belastingklasseoud" ADD CONSTRAINT "PK_Enum_belastingklasseoud"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_beleidsstatus" ADD CONSTRAINT "PK_Enum_beleidsstatus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_beoogdeomlooptijd" ADD CONSTRAINT "PK_Enum_beoogdeomlooptijd"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_bereikbaarheid" ADD CONSTRAINT "PK_Enum_bereikbaarheid"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_bereikbaarheidkolk" ADD CONSTRAINT "PK_Enum_bereikbaarheidkolk"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boombeeld" ADD CONSTRAINT "PK_Enum_boombeeld"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boomgroep" ADD CONSTRAINT "PK_Enum_boomgroep"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boomhoogteklasseactueel" ADD CONSTRAINT "PK_Enum_boomhoogteklasseactueel"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boomtypebeschermingsstatu" ADD CONSTRAINT "PK_Enum_boomtypebeschermingsstatu"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boomveiligheidsklasse" ADD CONSTRAINT "PK_Enum_boomveiligheidsklasse"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_boomvoorziening" ADD CONSTRAINT "PK_Enum_boomvoorziening"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_breedteklassehaag" ADD CONSTRAINT "PK_Enum_breedteklassehaag"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_certificeringsinstantie" ADD CONSTRAINT "PK_Enum_certificeringsinstantie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_constructielaagsoort" ADD CONSTRAINT "PK_Enum_constructielaagsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_constructietype" ADD CONSTRAINT "PK_Enum_constructietype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_controlefrequentie" ADD CONSTRAINT "PK_Enum_controlefrequentie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_cultuurhistorischwaardevo" ADD CONSTRAINT "PK_Enum_cultuurhistorischwaardevo"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_doelsoort" ADD CONSTRAINT "PK_Enum_doelsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_fabrikant" ADD CONSTRAINT "PK_Enum_fabrikant"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_formaat" ADD CONSTRAINT "PK_Enum_formaat"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_funderingleiding" ADD CONSTRAINT "PK_Enum_funderingleiding"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_gebiedstype" ADD CONSTRAINT "PK_Enum_gebiedstype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_gewenstsluitingspercentag" ADD CONSTRAINT "PK_Enum_gewenstsluitingspercentag"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_groeifase" ADD CONSTRAINT "PK_Enum_groeifase"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_groenobjectbereikbaarheid" ADD CONSTRAINT "PK_Enum_groenobjectbereikbaarheid"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_grondsoort" ADD CONSTRAINT "PK_Enum_grondsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_grondsoortplus" ADD CONSTRAINT "PK_Enum_grondsoortplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_hoogteklassehaag" ADD CONSTRAINT "PK_Enum_hoogteklassehaag"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_imklthema" ADD CONSTRAINT "PK_Enum_imklthema"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_installateur" ADD CONSTRAINT "PK_Enum_installateur"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_kleur" ADD CONSTRAINT "PK_Enum_kleur"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_kroondiameterklasseactuee" ADD CONSTRAINT "PK_Enum_kroondiameterklasseactuee"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_kwaliteitsniveaugewenst" ADD CONSTRAINT "PK_Enum_kwaliteitsniveaugewenst"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_kweker" ADD CONSTRAINT "PK_Enum_kweker"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_lengtekunstgras" ADD CONSTRAINT "PK_Enum_lengtekunstgras"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_leverancier" ADD CONSTRAINT "PK_Enum_leverancier"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_liningtype" ADD CONSTRAINT "PK_Enum_liningtype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_markeringsbreedte" ADD CONSTRAINT "PK_Enum_markeringsbreedte"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_markeringsoort" ADD CONSTRAINT "PK_Enum_markeringsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_markeringspatroon" ADD CONSTRAINT "PK_Enum_markeringspatroon"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_materiaal" ADD CONSTRAINT "PK_Enum_materiaal"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_ondergroei" ADD CONSTRAINT "PK_Enum_ondergroei"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_onderhoudsplichtige" ADD CONSTRAINT "PK_Enum_onderhoudsplichtige"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_onderhoudsregime" ADD CONSTRAINT "PK_Enum_onderhoudsregime"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_ondersteuningsvorm" ADD CONSTRAINT "PK_Enum_ondersteuningsvorm"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_oriã«ntatie" ADD CONSTRAINT "PK_Enum_oriã«ntatie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_overbruggingsobjectmodali" ADD CONSTRAINT "PK_Enum_overbruggingsobjectmodali"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_plaatsorientatie" ADD CONSTRAINT "PK_Enum_plaatsorientatie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_rioolputconstructieonderd" ADD CONSTRAINT "PK_Enum_rioolputconstructieonderd"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_snoeifase" ADD CONSTRAINT "PK_Enum_snoeifase"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_soortnaam" ADD CONSTRAINT "PK_Enum_soortnaam"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_soortplantenbak" ADD CONSTRAINT "PK_Enum_soortplantenbak"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_soortvoeg" ADD CONSTRAINT "PK_Enum_soortvoeg"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_speelterreinleeftijddoelg" ADD CONSTRAINT "PK_Enum_speelterreinleeftijddoelg"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_speeltoesteltoestelonderd" ADD CONSTRAINT "PK_Enum_speeltoesteltoestelonderd"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_sportterreintypesport" ADD CONSTRAINT "PK_Enum_sportterreintypesport"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_stamdiameterklasse" ADD CONSTRAINT "PK_Enum_stamdiameterklasse"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_status" ADD CONSTRAINT "PK_Enum_status"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_takvrijestam" ADD CONSTRAINT "PK_Enum_takvrijestam"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_taludsteilte" ADD CONSTRAINT "PK_Enum_taludsteilte"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_toestelgroep" ADD CONSTRAINT "PK_Enum_toestelgroep"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_type" ADD CONSTRAINT "PK_Enum_type"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeafdekking" ADD CONSTRAINT "PK_Enum_typeafdekking"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeasbesthoudend" ADD CONSTRAINT "PK_Enum_typeasbesthoudend"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebediening" ADD CONSTRAINT "PK_Enum_typebediening"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebeheerder" ADD CONSTRAINT "PK_Enum_typebeheerder"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebeheerderplus" ADD CONSTRAINT "PK_Enum_typebeheerderplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebeschermingsstatus" ADD CONSTRAINT "PK_Enum_typebeschermingsstatus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebewerking" ADD CONSTRAINT "PK_Enum_typebewerking"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebouwdeel" ADD CONSTRAINT "PK_Enum_typebouwdeel"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typebovenkantkademuur" ADD CONSTRAINT "PK_Enum_typebovenkantkademuur"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typecommunicatie" ADD CONSTRAINT "PK_Enum_typecommunicatie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeconstructie" ADD CONSTRAINT "PK_Enum_typeconstructie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typedeurbediening" ADD CONSTRAINT "PK_Enum_typedeurbediening"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeeigenaar" ADD CONSTRAINT "PK_Enum_typeeigenaar"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeeigenaarplus" ADD CONSTRAINT "PK_Enum_typeeigenaarplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeelement" ADD CONSTRAINT "PK_Enum_typeelement"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typefundering" ADD CONSTRAINT "PK_Enum_typefundering"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeligging" ADD CONSTRAINT "PK_Enum_typeligging"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typemantel" ADD CONSTRAINT "PK_Enum_typemantel"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typemonument" ADD CONSTRAINT "PK_Enum_typemonument"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typenivelleerschijf" ADD CONSTRAINT "PK_Enum_typenivelleerschijf"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeomgevingsrisicoklasse" ADD CONSTRAINT "PK_Enum_typeomgevingsrisicoklasse"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeonderdeelmetpomp" ADD CONSTRAINT "PK_Enum_typeonderdeelmetpomp"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeplus" ADD CONSTRAINT "PK_Enum_typeplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeslot" ADD CONSTRAINT "PK_Enum_typeslot"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typestandplaats" ADD CONSTRAINT "PK_Enum_typestandplaats"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typestandplaatsplus" ADD CONSTRAINT "PK_Enum_typestandplaatsplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeteerhoudend" ADD CONSTRAINT "PK_Enum_typeteerhoudend"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typevaarwater" ADD CONSTRAINT "PK_Enum_typevaarwater"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typevermeerderingsvorm" ADD CONSTRAINT "PK_Enum_typevermeerderingsvorm"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typevoeg" ADD CONSTRAINT "PK_Enum_typevoeg"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typevoegvulling" ADD CONSTRAINT "PK_Enum_typevoegvulling"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typewaaier" ADD CONSTRAINT "PK_Enum_typewaaier"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typewaterplant" ADD CONSTRAINT "PK_Enum_typewaterplant"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vegen" ADD CONSTRAINT "PK_Enum_vegen"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_verbindingstype" ADD CONSTRAINT "PK_Enum_verbindingstype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_verhardingsobjectwegfunct" ADD CONSTRAINT "PK_Enum_verhardingsobjectwegfunct"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vorm" ADD CONSTRAINT "PK_Enum_vorm"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vrijedoorrijhoogte" ADD CONSTRAINT "PK_Enum_vrijedoorrijhoogte"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vrijetakval" ADD CONSTRAINT "PK_Enum_vrijetakval"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vulmateriaalkunstgras" ADD CONSTRAINT "PK_Enum_vulmateriaalkunstgras"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_waterdoorlatendheid" ADD CONSTRAINT "PK_Enum_waterdoorlatendheid"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_wegastyperoute" ADD CONSTRAINT "PK_Enum_wegastyperoute"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_wegcategoriedv" ADD CONSTRAINT "PK_Enum_wegcategoriedv"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_wegtypebestaand" ADD CONSTRAINT "PK_Enum_wegtypebestaand"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_zettingsgevoeligheid" ADD CONSTRAINT "PK_Enum_zettingsgevoeligheid"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_zettingsgevoeligheidplus" ADD CONSTRAINT "PK_Enum_zettingsgevoeligheidplus"
	PRIMARY KEY ("ID");

ALTER TABLE "Aansluitput" ADD CONSTRAINT "PK_Aansluitput"
	PRIMARY KEY ("AansluitputID");

ALTER TABLE "Afvalbak" ADD CONSTRAINT "PK_Afvalbak"
	PRIMARY KEY ("AfvalbakID");

ALTER TABLE "Bak" ADD CONSTRAINT "PK_Bak"
	PRIMARY KEY ("BakID");

ALTER TABLE "Bank" ADD CONSTRAINT "PK_Bank"
	PRIMARY KEY ("BankID");

ALTER TABLE "Beheerobject" ADD CONSTRAINT "PK_Beheerobject"
	PRIMARY KEY ("BeheerobjectID");

ALTER TABLE "Bemalingsgebied" ADD CONSTRAINT "PK_Bemalingsgebied"
	PRIMARY KEY ("BemalingsgebiedID");

ALTER TABLE "Bergingsbassin" ADD CONSTRAINT "PK_Bergingsbassin"
	PRIMARY KEY ("BergingsbassinID");

ALTER TABLE "Boom" ADD CONSTRAINT "PK_Boom"
	PRIMARY KEY ("BoomID");

ALTER TABLE "Bord" ADD CONSTRAINT "PK_Bord"
	PRIMARY KEY ("BordID");

ALTER TABLE "Bouwwerk" ADD CONSTRAINT "PK_Bouwwerk"
	PRIMARY KEY ("BouwwerkID");

ALTER TABLE "Brug" ADD CONSTRAINT "PK_Brug"
	PRIMARY KEY ("BrugID");

ALTER TABLE "Drainageput" ADD CONSTRAINT "PK_Drainageput"
	PRIMARY KEY ("DrainageputID");

ALTER TABLE "Ecoduct" ADD CONSTRAINT "PK_Ecoduct"
	PRIMARY KEY ("EcoductID");

ALTER TABLE "Fietsparkeervoorziening" ADD CONSTRAINT "PK_Fietsparkeervoorziening"
	PRIMARY KEY ("FietsparkeervoorzieningID");

ALTER TABLE "Filterput" ADD CONSTRAINT "PK_Filterput"
	PRIMARY KEY ("FilterputID");

ALTER TABLE "Flyover" ADD CONSTRAINT "PK_Flyover"
	PRIMARY KEY ("FlyoverID");

ALTER TABLE "Functioneelgebied" ADD CONSTRAINT "PK_Functioneelgebied"
	PRIMARY KEY ("FunctioneelgebiedID");

ALTER TABLE "Geluidsscherm" ADD CONSTRAINT "PK_Geluidsscherm"
	PRIMARY KEY ("GeluidsschermID");

ALTER TABLE "Gemaal" ADD CONSTRAINT "PK_Gemaal"
	PRIMARY KEY ("GemaalID");

ALTER TABLE "Groenobject" ADD CONSTRAINT "PK_Groenobject"
	PRIMARY KEY ("GroenobjectID");

ALTER TABLE "Infiltratieput" ADD CONSTRAINT "PK_Infiltratieput"
	PRIMARY KEY ("InfiltratieputID");

ALTER TABLE "Installatie" ADD CONSTRAINT "PK_Installatie"
	PRIMARY KEY ("InstallatieID");

ALTER TABLE "Kademuur" ADD CONSTRAINT "PK_Kademuur"
	PRIMARY KEY ("KademuurID");

ALTER TABLE "Kast" ADD CONSTRAINT "PK_Kast"
	PRIMARY KEY ("KastID");

ALTER TABLE "Keermuur" ADD CONSTRAINT "PK_Keermuur"
	PRIMARY KEY ("KeermuurID");

ALTER TABLE "Klimplant" ADD CONSTRAINT "PK_Klimplant"
	PRIMARY KEY ("KlimplantID");

ALTER TABLE "Kolk" ADD CONSTRAINT "PK_Kolk"
	PRIMARY KEY ("KolkID");

ALTER TABLE "Kunstwerk" ADD CONSTRAINT "PK_Kunstwerk"
	PRIMARY KEY ("KunstwerkID");

ALTER TABLE "Leiding" ADD CONSTRAINT "PK_Leiding"
	PRIMARY KEY ("LeidingID");

ALTER TABLE "Leidingelement" ADD CONSTRAINT "PK_Leidingelement"
	PRIMARY KEY ("LeidingelementID");

ALTER TABLE "Mast" ADD CONSTRAINT "PK_Mast"
	PRIMARY KEY ("MastID");

ALTER TABLE "Meubilair" ADD CONSTRAINT "PK_Meubilair"
	PRIMARY KEY ("MeubilairID");

ALTER TABLE "Overbruggingsobject" ADD CONSTRAINT "PK_Overbruggingsobject"
	PRIMARY KEY ("OverbruggingsobjectID");

ALTER TABLE "Overstortconstructie" ADD CONSTRAINT "PK_Overstortconstructie"
	PRIMARY KEY ("OverstortconstructieID");

ALTER TABLE "Paal" ADD CONSTRAINT "PK_Paal"
	PRIMARY KEY ("PaalID");

ALTER TABLE "Pomp" ADD CONSTRAINT "PK_Pomp"
	PRIMARY KEY ("PompID");

ALTER TABLE "Put" ADD CONSTRAINT "PK_Put"
	PRIMARY KEY ("PutID");

ALTER TABLE "Putdeksel" ADD CONSTRAINT "PK_Putdeksel"
	PRIMARY KEY ("PutdekselID");

ALTER TABLE "Rioleringsgebied" ADD CONSTRAINT "PK_Rioleringsgebied"
	PRIMARY KEY ("RioleringsgebiedID");

ALTER TABLE "Rioolput" ADD CONSTRAINT "PK_Rioolput"
	PRIMARY KEY ("RioolputID");

ALTER TABLE "Scheiding" ADD CONSTRAINT "PK_Scheiding"
	PRIMARY KEY ("ScheidingID");

ALTER TABLE "Sensor" ADD CONSTRAINT "PK_Sensor"
	PRIMARY KEY ("SensorID");

ALTER TABLE "Solitaireplant" ADD CONSTRAINT "PK_Solitaireplant"
	PRIMARY KEY ("SolitaireplantID");

ALTER TABLE "Speelterrein" ADD CONSTRAINT "PK_Speelterrein"
	PRIMARY KEY ("SpeelterreinID");

ALTER TABLE "Speeltoestel" ADD CONSTRAINT "PK_Speeltoestel"
	PRIMARY KEY ("SpeeltoestelID");

ALTER TABLE "Sportterrein" ADD CONSTRAINT "PK_Sportterrein"
	PRIMARY KEY ("SportterreinID");

ALTER TABLE "Stuwgebied" ADD CONSTRAINT "PK_Stuwgebied"
	PRIMARY KEY ("StuwgebiedID");

ALTER TABLE "Terreindeel" ADD CONSTRAINT "PK_Terreindeel"
	PRIMARY KEY ("TerreindeelID");

ALTER TABLE "Tunnelobject" ADD CONSTRAINT "PK_Tunnelobject"
	PRIMARY KEY ("TunnelobjectID");

ALTER TABLE "Uitlaatconstructie" ADD CONSTRAINT "PK_Uitlaatconstructie"
	PRIMARY KEY ("UitlaatconstructieID");

ALTER TABLE "Vegetatieobject" ADD CONSTRAINT "PK_Vegetatieobject"
	PRIMARY KEY ("VegetatieobjectID");

ALTER TABLE "Verhardingsobject" ADD CONSTRAINT "PK_Verhardingsobject"
	PRIMARY KEY ("VerhardingsobjectID");

ALTER TABLE "Verkeersdrempel" ADD CONSTRAINT "PK_Verkeersdrempel"
	PRIMARY KEY ("VerkeersdrempelID");

ALTER TABLE "Verlichtingsobject" ADD CONSTRAINT "PK_Verlichtingsobject"
	PRIMARY KEY ("VerlichtingsobjectID");

ALTER TABLE "Viaduct" ADD CONSTRAINT "PK_Viaduct"
	PRIMARY KEY ("ViaductID");

ALTER TABLE "Waterinrichtingsobject" ADD CONSTRAINT "PK_Waterinrichtingsobject"
	PRIMARY KEY ("WaterinrichtingsobjectID");

ALTER TABLE "Waterobject" ADD CONSTRAINT "PK_Waterobject"
	PRIMARY KEY ("WaterobjectID");

ALTER TABLE "Weginrichtingsobject" ADD CONSTRAINT "PK_Weginrichtingsobject"
	PRIMARY KEY ("WeginrichtingsobjectID");

ALTER TABLE "Aansluitput" ADD CONSTRAINT "Fk_aansluitput_put"
	FOREIGN KEY ("AansluitputID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Afvalbak" ADD CONSTRAINT "Fk_afvalbak_bak"
	FOREIGN KEY ("AfvalbakID") REFERENCES "Bak" ("BakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bak" ADD CONSTRAINT "Fk_bak_beheerobject"
	FOREIGN KEY ("BakID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bank" ADD CONSTRAINT "Fk_bank_meubilair"
	FOREIGN KEY ("BankID") REFERENCES "Meubilair" ("MeubilairID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beheerobject" ADD CONSTRAINT "fk_verwijstNaar_geo_object"
	FOREIGN KEY ("Geo_objectID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bemalingsgebied" ADD CONSTRAINT "Fk_bemalingsgebied_functioneelgebied"
	FOREIGN KEY ("BemalingsgebiedID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bergingsbassin" ADD CONSTRAINT "Fk_bergingsbassin_bouwwerk"
	FOREIGN KEY ("BergingsbassinID") REFERENCES "Bouwwerk" ("BouwwerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Boom" ADD CONSTRAINT "Fk_boom_vegetatieobject"
	FOREIGN KEY ("BoomID") REFERENCES "Vegetatieobject" ("VegetatieobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bord" ADD CONSTRAINT "Fk_bord_beheerobject"
	FOREIGN KEY ("BordID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bouwwerk" ADD CONSTRAINT "Fk_bouwwerk_beheerobject"
	FOREIGN KEY ("BouwwerkID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Brug" ADD CONSTRAINT "Fk_brug_overbruggingsobject"
	FOREIGN KEY ("BrugID") REFERENCES "Overbruggingsobject" ("OverbruggingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Drainageput" ADD CONSTRAINT "Fk_drainageput_put"
	FOREIGN KEY ("DrainageputID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ecoduct" ADD CONSTRAINT "Fk_ecoduct_overbruggingsobject"
	FOREIGN KEY ("EcoductID") REFERENCES "Overbruggingsobject" ("OverbruggingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Fietsparkeervoorziening" ADD CONSTRAINT "Fk_fietsparkeervoorziening_meubilair"
	FOREIGN KEY ("FietsparkeervoorzieningID") REFERENCES "Meubilair" ("MeubilairID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Filterput" ADD CONSTRAINT "Fk_filterput_put"
	FOREIGN KEY ("FilterputID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Flyover" ADD CONSTRAINT "Fk_flyover_overbruggingsobject"
	FOREIGN KEY ("FlyoverID") REFERENCES "Overbruggingsobject" ("OverbruggingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functioneelgebied" ADD CONSTRAINT "Fk_functioneelgebied_beheerobject"
	FOREIGN KEY ("FunctioneelgebiedID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Geluidsscherm" ADD CONSTRAINT "Fk_geluidsscherm_scheiding"
	FOREIGN KEY ("GeluidsschermID") REFERENCES "Scheiding" ("ScheidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gemaal" ADD CONSTRAINT "Fk_gemaal_kunstwerk"
	FOREIGN KEY ("GemaalID") REFERENCES "Kunstwerk" ("KunstwerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Groenobject" ADD CONSTRAINT "Fk_groenobject_beheerobject"
	FOREIGN KEY ("GroenobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Infiltratieput" ADD CONSTRAINT "Fk_infiltratieput_put"
	FOREIGN KEY ("InfiltratieputID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Installatie" ADD CONSTRAINT "Fk_installatie_beheerobject"
	FOREIGN KEY ("InstallatieID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kademuur" ADD CONSTRAINT "Fk_kademuur_scheiding"
	FOREIGN KEY ("KademuurID") REFERENCES "Scheiding" ("ScheidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kast" ADD CONSTRAINT "Fk_kast_beheerobject"
	FOREIGN KEY ("KastID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Keermuur" ADD CONSTRAINT "Fk_keermuur_scheiding"
	FOREIGN KEY ("KeermuurID") REFERENCES "Scheiding" ("ScheidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klimplant" ADD CONSTRAINT "Fk_klimplant_vegetatieobject"
	FOREIGN KEY ("KlimplantID") REFERENCES "Vegetatieobject" ("VegetatieobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kolk" ADD CONSTRAINT "Fk_kolk_put"
	FOREIGN KEY ("KolkID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_melding_beheerobject" ADD CONSTRAINT "Fk_kp_melding_beheerobject_beheerobject"
	FOREIGN KEY ("BeheerobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_melding_beheerobject" ADD CONSTRAINT "Fk_kp_melding_beheerobject_melding"
	FOREIGN KEY ("MeldingID") REFERENCES "Melding" ("MeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kunstwerk" ADD CONSTRAINT "Fk_kunstwerk_beheerobject"
	FOREIGN KEY ("KunstwerkID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leiding" ADD CONSTRAINT "Fk_leiding_beheerobject"
	FOREIGN KEY ("LeidingID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leidingelement" ADD CONSTRAINT "Fk_leidingelement_beheerobject"
	FOREIGN KEY ("LeidingelementID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mast" ADD CONSTRAINT "Fk_mast_beheerobject"
	FOREIGN KEY ("MastID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Meubilair" ADD CONSTRAINT "Fk_meubilair_beheerobject"
	FOREIGN KEY ("MeubilairID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overbruggingsobject" ADD CONSTRAINT "Fk_overbruggingsobject_beheerobject"
	FOREIGN KEY ("OverbruggingsobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overstortconstructie" ADD CONSTRAINT "Fk_overstortconstructie_kunstwerk"
	FOREIGN KEY ("OverstortconstructieID") REFERENCES "Kunstwerk" ("KunstwerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Paal" ADD CONSTRAINT "Fk_paal_beheerobject"
	FOREIGN KEY ("PaalID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pomp" ADD CONSTRAINT "Fk_pomp_installatie"
	FOREIGN KEY ("PompID") REFERENCES "Installatie" ("InstallatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Put" ADD CONSTRAINT "Fk_put_beheerobject"
	FOREIGN KEY ("PutID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Putdeksel" ADD CONSTRAINT "Fk_putdeksel_weginrichtingsobject"
	FOREIGN KEY ("PutdekselID") REFERENCES "Weginrichtingsobject" ("WeginrichtingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rioleringsgebied" ADD CONSTRAINT "Fk_rioleringsgebied_functioneelgebied"
	FOREIGN KEY ("RioleringsgebiedID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rioolput" ADD CONSTRAINT "Fk_rioolput_put"
	FOREIGN KEY ("RioolputID") REFERENCES "Put" ("PutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Scheiding" ADD CONSTRAINT "Fk_scheiding_beheerobject"
	FOREIGN KEY ("ScheidingID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sensor" ADD CONSTRAINT "Fk_sensor_beheerobject"
	FOREIGN KEY ("SensorID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Solitaireplant" ADD CONSTRAINT "Fk_solitaireplant_vegetatieobject"
	FOREIGN KEY ("SolitaireplantID") REFERENCES "Vegetatieobject" ("VegetatieobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Speelterrein" ADD CONSTRAINT "Fk_speelterrein_functioneelgebied"
	FOREIGN KEY ("SpeelterreinID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Speeltoestel" ADD CONSTRAINT "Fk_speeltoestel_meubilair"
	FOREIGN KEY ("SpeeltoestelID") REFERENCES "Meubilair" ("MeubilairID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sportterrein" ADD CONSTRAINT "Fk_sportterrein_functioneelgebied"
	FOREIGN KEY ("SportterreinID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stuwgebied" ADD CONSTRAINT "Fk_stuwgebied_functioneelgebied"
	FOREIGN KEY ("StuwgebiedID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Terreindeel" ADD CONSTRAINT "Fk_terreindeel_beheerobject"
	FOREIGN KEY ("TerreindeelID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tunnelobject" ADD CONSTRAINT "Fk_tunnelobject_beheerobject"
	FOREIGN KEY ("TunnelobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitlaatconstructie" ADD CONSTRAINT "Fk_uitlaatconstructie_kunstwerk"
	FOREIGN KEY ("UitlaatconstructieID") REFERENCES "Kunstwerk" ("KunstwerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vegetatieobject" ADD CONSTRAINT "Fk_vegetatieobject_beheerobject"
	FOREIGN KEY ("VegetatieobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verhardingsobject" ADD CONSTRAINT "Fk_verhardingsobject_beheerobject"
	FOREIGN KEY ("VerhardingsobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verkeersdrempel" ADD CONSTRAINT "Fk_verkeersdrempel_weginrichtingsobject"
	FOREIGN KEY ("VerkeersdrempelID") REFERENCES "Weginrichtingsobject" ("WeginrichtingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verlichtingsobject" ADD CONSTRAINT "Fk_verlichtingsobject_beheerobject"
	FOREIGN KEY ("VerlichtingsobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Viaduct" ADD CONSTRAINT "Fk_viaduct_overbruggingsobject"
	FOREIGN KEY ("ViaductID") REFERENCES "Overbruggingsobject" ("OverbruggingsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waterinrichtingsobject" ADD CONSTRAINT "Fk_waterinrichtingsobject_beheerobject"
	FOREIGN KEY ("WaterinrichtingsobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waterobject" ADD CONSTRAINT "Fk_waterobject_beheerobject"
	FOREIGN KEY ("WaterobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Weginrichtingsobject" ADD CONSTRAINT "Fk_weginrichtingsobject_beheerobject"
	FOREIGN KEY ("WeginrichtingsobjectID") REFERENCES "Beheerobject" ("BeheerobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "BevoegdGezag" ADD CONSTRAINT "PK_BevoegdGezag"
	PRIMARY KEY ("BevoegdGezagID");

ALTER TABLE "Enum_doelVerzoek" ADD CONSTRAINT "PK_Enum_doelVerzoek"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeVerzoek" ADD CONSTRAINT "PK_Enum_typeVerzoek"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vraagClassificatie" ADD CONSTRAINT "PK_Enum_vraagClassificatie"
	PRIMARY KEY ("ID");

ALTER TABLE "Gemachtigde" ADD CONSTRAINT "PK_Gemachtigde"
	PRIMARY KEY ("GemachtigdeID");

ALTER TABLE "Initiatiefnemer" ADD CONSTRAINT "PK_Initiatiefnemer"
	PRIMARY KEY ("InitiatiefnemerID");

ALTER TABLE "Project" ADD CONSTRAINT "PK_Project"
	PRIMARY KEY ("ProjectID");

ALTER TABLE "Projectactiviteit" ADD CONSTRAINT "PK_Projectactiviteit"
	PRIMARY KEY ("ProjectactiviteitID");

ALTER TABLE "Projectlocatie" ADD CONSTRAINT "PK_Projectlocatie"
	PRIMARY KEY ("ProjectlocatieID");

ALTER TABLE "Specificatie" ADD CONSTRAINT "PK_Specificatie"
	PRIMARY KEY ("SpecificatieID");

ALTER TABLE "UitvoerendeInstantie" ADD CONSTRAINT "PK_UitvoerendeInstantie"
	PRIMARY KEY ("UitvoerendeInstantieID");

ALTER TABLE "Verzoek" ADD CONSTRAINT "PK_Verzoek"
	PRIMARY KEY ("VerzoekID");

ALTER TABLE "BevoegdGezag" ADD CONSTRAINT "Fk_bevoegdGezag_rechtspersoon"
	FOREIGN KEY ("BevoegdGezagID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gemachtigde" ADD CONSTRAINT "Fk_gemachtigde_rechtspersoon"
	FOREIGN KEY ("GemachtigdeID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Initiatiefnemer" ADD CONSTRAINT "Fk_initiatiefnemer_rechtspersoon"
	FOREIGN KEY ("InitiatiefnemerID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_activiteit" ADD CONSTRAINT "Fk_kp_verzoek_activiteit_verzoek"
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_activiteit" ADD CONSTRAINT "Fk_kp_verzoek_activiteit_activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_locatie" ADD CONSTRAINT "Fk_kp_verzoek_locatie_verzoek"
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_locatie" ADD CONSTRAINT "Fk_kp_verzoek_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_project" ADD CONSTRAINT "Fk_kp_verzoek_project_project"
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_project" ADD CONSTRAINT "Fk_kp_verzoek_project_verzoek"
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_projectactiviteit" ADD CONSTRAINT "Fk_kp_verzoek_projectactiviteit_projectactiviteit"
	FOREIGN KEY ("ProjectactiviteitID") REFERENCES "Projectactiviteit" ("ProjectactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verzoek_projectactiviteit" ADD CONSTRAINT "Fk_kp_verzoek_projectactiviteit_verzoek"
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectactiviteit" ADD CONSTRAINT fk_heeft_project
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectactiviteit" ADD CONSTRAINT "FK_Projectactiviteit_Projectlocatie"
	FOREIGN KEY ("ProjectlocatieID") REFERENCES "Projectlocatie" ("ProjectlocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectlocatie" ADD CONSTRAINT fk_heeft_project
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Projectlocatie" ADD CONSTRAINT "FK_Projectlocatie_Locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Specificatie" ADD CONSTRAINT "FK_Specificatie_Projectactiviteit"
	FOREIGN KEY ("ProjectactiviteitID") REFERENCES "Projectactiviteit" ("ProjectactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Specificatie" ADD CONSTRAINT fk_bevat_verzoek
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzoek" ADD CONSTRAINT "FK_Verzoek_BevoegdGezag"
	FOREIGN KEY ("BevoegdGezagID") REFERENCES "BevoegdGezag" ("BevoegdGezagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzoek" ADD CONSTRAINT "fk_dientIn_gemachtigde"
	FOREIGN KEY ("GemachtigdeID") REFERENCES "Gemachtigde" ("GemachtigdeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzoek" ADD CONSTRAINT "fk_heeftAlsVerantwoordelijke_i"
	FOREIGN KEY ("InitiatiefnemerID") REFERENCES "Initiatiefnemer" ("InitiatiefnemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzoek" ADD CONSTRAINT "FK_Verzoek_UitvoerendeInstantie"
	FOREIGN KEY ("UitvoerendeInstantieID") REFERENCES "UitvoerendeInstantie" ("UitvoerendeInstantieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzoek" ADD CONSTRAINT fk_eerderverzoek_verzoek
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Omgevingsdocument" ADD CONSTRAINT "PK_Omgevingsdocument"
	PRIMARY KEY ("OmgevingsdocumentID");

ALTER TABLE "Regeltekst" ADD CONSTRAINT "PK_Regeltekst"
	PRIMARY KEY ("RegeltekstID");

ALTER TABLE "Kp_regeltekst_idealisatie" ADD CONSTRAINT "Fk_kp_regeltekst_idealisatie_regeltekst"
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regeltekst_idealisatie" ADD CONSTRAINT "Fk_kp_regeltekst_idealisatie_idealisatie"
	FOREIGN KEY ("IdealisatieID") REFERENCES "Idealisatie" ("IdealisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regeltekst_locatie" ADD CONSTRAINT "Fk_kp_regeltekst_locatie_regeltekst"
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regeltekst_locatie" ADD CONSTRAINT "Fk_kp_regeltekst_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regeltekst_thema" ADD CONSTRAINT "Fk_kp_regeltekst_thema_regeltekst"
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regeltekst_thema" ADD CONSTRAINT "Fk_kp_regeltekst_thema_thema"
	FOREIGN KEY ("ThemaID") REFERENCES "Thema" ("ThemaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Regeltekst" ADD CONSTRAINT fk_bevat_omgevingsdocument
	FOREIGN KEY ("OmgevingsdocumentID") REFERENCES "Omgevingsdocument" ("OmgevingsdocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Regeltekst" ADD CONSTRAINT "fk_isGerelateerd_regeltekst"
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Regeltekst" ADD CONSTRAINT fk_werkingsgebied_regeltekst
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "PK_Activiteit"
	PRIMARY KEY ("ActiviteitID");

ALTER TABLE "Beperkingsgebied" ADD CONSTRAINT "PK_Beperkingsgebied"
	PRIMARY KEY ("BeperkingsgebiedID");

ALTER TABLE "Functie" ADD CONSTRAINT "PK_Functie"
	PRIMARY KEY ("FunctieID");

ALTER TABLE "Gebiedsaanwijzing" ADD CONSTRAINT "PK_Gebiedsaanwijzing"
	PRIMARY KEY ("GebiedsaanwijzingID");

ALTER TABLE "Idealisatie" ADD CONSTRAINT "PK_Idealisatie"
	PRIMARY KEY ("IdealisatieID");

ALTER TABLE "Instructieregel" ADD CONSTRAINT "PK_Instructieregel"
	PRIMARY KEY ("InstructieregelID");

ALTER TABLE "JuridischeRegel" ADD CONSTRAINT "PK_JuridischeRegel"
	PRIMARY KEY ("JuridischeRegelID");

ALTER TABLE "Norm" ADD CONSTRAINT "PK_Norm"
	PRIMARY KEY ("NormID");

ALTER TABLE "Normwaarde" ADD CONSTRAINT "PK_Normwaarde"
	PRIMARY KEY ("NormwaardeID");

ALTER TABLE "Omgevingsnorm" ADD CONSTRAINT "PK_Omgevingsnorm"
	PRIMARY KEY ("OmgevingsnormID");

ALTER TABLE "Omgevingswaarde" ADD CONSTRAINT "PK_Omgevingswaarde"
	PRIMARY KEY ("OmgevingswaardeID");

ALTER TABLE "Omgevingswaarderegel" ADD CONSTRAINT "PK_Omgevingswaarderegel"
	PRIMARY KEY ("OmgevingswaarderegelID");

ALTER TABLE "RegelVoorIedereen" ADD CONSTRAINT "PK_RegelVoorIedereen"
	PRIMARY KEY ("RegelVoorIedereenID");

ALTER TABLE "Thema" ADD CONSTRAINT "PK_Thema"
	PRIMARY KEY ("ThemaID");

ALTER TABLE "Activiteit" ADD CONSTRAINT "fk_bovenliggendeActiviteit_act"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activiteit" ADD CONSTRAINT "fk_gerelateerdeActiviteit_acti"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beperkingsgebied" ADD CONSTRAINT "Fk_beperkingsgebied_gebiedsaanwijzing"
	FOREIGN KEY ("BeperkingsgebiedID") REFERENCES "Gebiedsaanwijzing" ("GebiedsaanwijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functie" ADD CONSTRAINT "Fk_functie_gebiedsaanwijzing"
	FOREIGN KEY ("FunctieID") REFERENCES "Gebiedsaanwijzing" ("GebiedsaanwijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Instructieregel" ADD CONSTRAINT "Fk_instructieregel_juridischeRegel"
	FOREIGN KEY ("InstructieregelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "JuridischeRegel" ADD CONSTRAINT "FK_JuridischeRegel_Regeltekst"
	FOREIGN KEY ("RegeltekstID") REFERENCES "Regeltekst" ("RegeltekstID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_activiteit_locatie" ADD CONSTRAINT "Fk_kp_activiteit_locatie_activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_activiteit_locatie" ADD CONSTRAINT "Fk_kp_activiteit_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_gebiedsaanwijzing_locatie" ADD CONSTRAINT "Fk_kp_gebiedsaanwijzing_locatie_gebiedsaanwijzing"
	FOREIGN KEY ("GebiedsaanwijzingID") REFERENCES "Gebiedsaanwijzing" ("GebiedsaanwijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_gebiedsaanwijzing_locatie" ADD CONSTRAINT "Fk_kp_gebiedsaanwijzing_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_instructieregel_gebiedsaanw" ADD CONSTRAINT "Fk_kp_instructieregel_gebiedsaanw_gebiedsaanwijzing"
	FOREIGN KEY ("GebiedsaanwijzingID") REFERENCES "Gebiedsaanwijzing" ("GebiedsaanwijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_instructieregel_gebiedsaanw" ADD CONSTRAINT "Fk_kp_instructieregel_gebiedsaanw_instructieregel"
	FOREIGN KEY ("InstructieregelID") REFERENCES "Instructieregel" ("InstructieregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_activiteit" ADD CONSTRAINT "Fk_kp_juridischeregel_activiteit_activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_activiteit" ADD CONSTRAINT "Fk_kp_juridischeregel_activiteit_juridischeRegel"
	FOREIGN KEY ("JuridischeRegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_idealisati" ADD CONSTRAINT "Fk_kp_juridischeregel_idealisati_idealisatie"
	FOREIGN KEY ("IdealisatieID") REFERENCES "Idealisatie" ("IdealisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_idealisati" ADD CONSTRAINT "Fk_kp_juridischeregel_idealisati_juridischeRegel"
	FOREIGN KEY ("JuridischeRegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_locatie" ADD CONSTRAINT "Fk_kp_juridischeregel_locatie_juridischeRegel"
	FOREIGN KEY ("JuridischeRegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_locatie" ADD CONSTRAINT "Fk_kp_juridischeregel_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_thema" ADD CONSTRAINT "Fk_kp_juridischeregel_thema_thema"
	FOREIGN KEY ("ThemaID") REFERENCES "Thema" ("ThemaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_juridischeRegel_thema" ADD CONSTRAINT "Fk_kp_juridischeregel_thema_juridischeRegel"
	FOREIGN KEY ("JuridischeRegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_normwaarde_locatie" ADD CONSTRAINT "Fk_kp_normwaarde_locatie_normwaarde"
	FOREIGN KEY ("NormwaardeID") REFERENCES "Normwaarde" ("NormwaardeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_normwaarde_locatie" ADD CONSTRAINT "Fk_kp_normwaarde_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_omgevingswaarderegel_omgevi" ADD CONSTRAINT "Fk_kp_omgevingswaarderegel_omgevi_omgevingsnorm"
	FOREIGN KEY ("OmgevingsnormID") REFERENCES "Omgevingsnorm" ("OmgevingsnormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_omgevingswaarderegel_omgevi" ADD CONSTRAINT "Fk_kp_omgevingswaarderegel_omgevi_omgevingswaarderegel"
	FOREIGN KEY ("OmgevingswaarderegelID") REFERENCES "Omgevingswaarderegel" ("OmgevingswaarderegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_omgevingswaarderegel_omgevi" ADD CONSTRAINT "Fk_kp_omgevingswaarderegel_omgevi_omgevingswaarde"
	FOREIGN KEY ("OmgevingswaardeID") REFERENCES "Omgevingswaarde" ("OmgevingswaardeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_omgevingswaarderegel_omgevi" ADD CONSTRAINT "Fk_kp_omgevingswaarderegel_omgevi_omgevingswaarderegel"
	FOREIGN KEY ("OmgevingswaarderegelID") REFERENCES "Omgevingswaarderegel" ("OmgevingswaarderegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_activit" ADD CONSTRAINT "Fk_kp_regelvooriedereen_activit_activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_activit" ADD CONSTRAINT "Fk_kp_regelvooriedereen_activit_regelVoorIedereen"
	FOREIGN KEY ("RegelVoorIedereenID") REFERENCES "RegelVoorIedereen" ("RegelVoorIedereenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_gebieds" ADD CONSTRAINT "Fk_kp_regelvooriedereen_gebieds_gebiedsaanwijzing"
	FOREIGN KEY ("GebiedsaanwijzingID") REFERENCES "Gebiedsaanwijzing" ("GebiedsaanwijzingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_gebieds" ADD CONSTRAINT "Fk_kp_regelvooriedereen_gebieds_regelVoorIedereen"
	FOREIGN KEY ("RegelVoorIedereenID") REFERENCES "RegelVoorIedereen" ("RegelVoorIedereenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_omgevin" ADD CONSTRAINT "Fk_kp_regelvooriedereen_omgevin_omgevingsnorm"
	FOREIGN KEY ("OmgevingsnormID") REFERENCES "Omgevingsnorm" ("OmgevingsnormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_regelVoorIedereen_omgevin" ADD CONSTRAINT "Fk_kp_regelvooriedereen_omgevin_regelVoorIedereen"
	FOREIGN KEY ("RegelVoorIedereenID") REFERENCES "RegelVoorIedereen" ("RegelVoorIedereenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_toepasbareRegel_juridische" ADD CONSTRAINT "Fk_kp_toepasbareregel_juridische_juridischeRegel"
	FOREIGN KEY ("JuridischeRegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_toepasbareRegel_juridische" ADD CONSTRAINT "Fk_kp_toepasbareregel_juridische_toepasbareRegel"
	FOREIGN KEY ("ToepasbareRegelID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Normwaarde" ADD CONSTRAINT fk_bevat_norm
	FOREIGN KEY ("NormID") REFERENCES "Norm" ("NormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Omgevingsnorm" ADD CONSTRAINT "Fk_omgevingsnorm_norm"
	FOREIGN KEY ("OmgevingsnormID") REFERENCES "Norm" ("NormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Omgevingswaarde" ADD CONSTRAINT "Fk_omgevingswaarde_norm"
	FOREIGN KEY ("OmgevingswaardeID") REFERENCES "Norm" ("NormID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Omgevingswaarderegel" ADD CONSTRAINT "Fk_omgevingswaarderegel_juridischeRegel"
	FOREIGN KEY ("OmgevingswaarderegelID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "RegelVoorIedereen" ADD CONSTRAINT "Fk_regelVoorIedereen_juridischeRegel"
	FOREIGN KEY ("RegelVoorIedereenID") REFERENCES "JuridischeRegel" ("JuridischeRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Thema" ADD CONSTRAINT fk_subthema_thema
	FOREIGN KEY ("ThemaID") REFERENCES "Thema" ("ThemaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Conclusie" ADD CONSTRAINT "PK_Conclusie"
	PRIMARY KEY ("ConclusieID");

ALTER TABLE "Indieningsvereisten" ADD CONSTRAINT "PK_Indieningsvereisten"
	PRIMARY KEY ("IndieningsvereistenID");

ALTER TABLE "Maatregelen" ADD CONSTRAINT "PK_Maatregelen"
	PRIMARY KEY ("MaatregelenID");

ALTER TABLE "ToepasbareRegel" ADD CONSTRAINT "PK_ToepasbareRegel"
	PRIMARY KEY ("ToepasbareRegelID");

ALTER TABLE "Toepasbareregelbestand" ADD CONSTRAINT "PK_Toepasbareregelbestand"
	PRIMARY KEY ("ToepasbareregelbestandID");

ALTER TABLE "Uitvoeringsregel" ADD CONSTRAINT "PK_Uitvoeringsregel"
	PRIMARY KEY ("UitvoeringsregelID");

ALTER TABLE "Conclusie" ADD CONSTRAINT "Fk_conclusie_toepasbareRegel"
	FOREIGN KEY ("ConclusieID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Indieningsvereisten" ADD CONSTRAINT "Fk_indieningsvereisten_toepasbareRegel"
	FOREIGN KEY ("IndieningsvereistenID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_toepasbareRegel_locatie" ADD CONSTRAINT "Fk_kp_toepasbareregel_locatie_toepasbareRegel"
	FOREIGN KEY ("ToepasbareRegelID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_toepasbareRegel_locatie" ADD CONSTRAINT "Fk_kp_toepasbareregel_locatie_locatie"
	FOREIGN KEY ("LocatieID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Maatregelen" ADD CONSTRAINT "Fk_maatregelen_toepasbareRegel"
	FOREIGN KEY ("MaatregelenID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ToepasbareRegel" ADD CONSTRAINT "FK_ToepasbareRegel_Toepasbareregelbestand"
	FOREIGN KEY ("ToepasbareregelbestandID") REFERENCES "Toepasbareregelbestand" ("ToepasbareregelbestandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "ToepasbareRegel" ADD CONSTRAINT "FK_ToepasbareRegel_Activiteit"
	FOREIGN KEY ("ActiviteitID") REFERENCES "Activiteit" ("ActiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitvoeringsregel" ADD CONSTRAINT "fk_heeft_toepasbareRegel"
	FOREIGN KEY ("ToepasbareRegelID") REFERENCES "ToepasbareRegel" ("ToepasbareRegelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitvoeringsregel" ADD CONSTRAINT fk_bevat_toepasbareregelbestan
	FOREIGN KEY ("ToepasbareregelbestandID") REFERENCES "Toepasbareregelbestand" ("ToepasbareregelbestandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Activa" ADD CONSTRAINT "PK_Activa"
	PRIMARY KEY ("ActivaID");

ALTER TABLE "Activasoort" ADD CONSTRAINT "PK_Activasoort"
	PRIMARY KEY ("ActivasoortID");

ALTER TABLE "Bankafschrift" ADD CONSTRAINT "PK_Bankafschrift"
	PRIMARY KEY ("BankafschriftID");

ALTER TABLE "Bankafschriftregel" ADD CONSTRAINT "PK_Bankafschriftregel"
	PRIMARY KEY ("BankafschriftregelID");

ALTER TABLE "Bankrekening" ADD CONSTRAINT "PK_Bankrekening"
	PRIMARY KEY ("BankrekeningID");

ALTER TABLE "Batch" ADD CONSTRAINT "PK_Batch"
	PRIMARY KEY ("BatchID");

ALTER TABLE "Batchregel" ADD CONSTRAINT "PK_Batchregel"
	PRIMARY KEY ("BatchregelID");

ALTER TABLE "Begroting" ADD CONSTRAINT "PK_Begroting"
	PRIMARY KEY ("BegrotingID");

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "PK_Begrotingregel"
	PRIMARY KEY ("BegrotingregelID");

ALTER TABLE "Debiteur" ADD CONSTRAINT "PK_Debiteur"
	PRIMARY KEY ("DebiteurID");

ALTER TABLE "Doelstelling" ADD CONSTRAINT "PK_Doelstelling"
	PRIMARY KEY ("DoelstellingID");

ALTER TABLE "Factuur" ADD CONSTRAINT "PK_Factuur"
	PRIMARY KEY ("FactuurID");

ALTER TABLE "Factuurregel" ADD CONSTRAINT "PK_Factuurregel"
	PRIMARY KEY ("FactuurregelID");

ALTER TABLE "Hoofdrekening" ADD CONSTRAINT "PK_Hoofdrekening"
	PRIMARY KEY ("HoofdrekeningID");

ALTER TABLE "Hoofdstuk" ADD CONSTRAINT "PK_Hoofdstuk"
	PRIMARY KEY ("HoofdstukID");

ALTER TABLE "Inkooporder" ADD CONSTRAINT "PK_Inkooporder"
	PRIMARY KEY ("InkooporderID");

ALTER TABLE "Kostenplaats" ADD CONSTRAINT "PK_Kostenplaats"
	PRIMARY KEY ("KostenplaatsID");

ALTER TABLE "Mutatie" ADD CONSTRAINT "PK_Mutatie"
	PRIMARY KEY ("MutatieID");

ALTER TABLE "Opdrachtgever" ADD CONSTRAINT "PK_Opdrachtgever"
	PRIMARY KEY ("OpdrachtgeverID");

ALTER TABLE "Opdrachtnemer" ADD CONSTRAINT "PK_Opdrachtnemer"
	PRIMARY KEY ("OpdrachtnemerID");

ALTER TABLE "Product" ADD CONSTRAINT "PK_Product"
	PRIMARY KEY ("ProductID");

ALTER TABLE "Subrekening" ADD CONSTRAINT "PK_Subrekening"
	PRIMARY KEY ("SubrekeningID");

ALTER TABLE "Taakveld" ADD CONSTRAINT "PK_Taakveld"
	PRIMARY KEY ("TaakveldID");

ALTER TABLE "Werkorder" ADD CONSTRAINT "PK_Werkorder"
	PRIMARY KEY ("WerkorderID");

ALTER TABLE "Activa" ADD CONSTRAINT "FK_Activa_Activasoort"
	FOREIGN KEY ("ActivasoortID") REFERENCES "Activasoort" ("ActivasoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bankafschrift" ADD CONSTRAINT fk_heeft_bankrekening
	FOREIGN KEY ("BankrekeningID") REFERENCES "Bankrekening" ("BankrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bankafschriftregel" ADD CONSTRAINT fk_heeft_bankafschrift
	FOREIGN KEY ("BankafschriftID") REFERENCES "Bankafschrift" ("BankafschriftID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Batch" ADD CONSTRAINT "fk_heeftHerkomst_applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Batch" ADD CONSTRAINT "FK_Batch_Externebron"
	FOREIGN KEY ("ExternebronID") REFERENCES "Externebron" ("ExternebronID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Batchregel" ADD CONSTRAINT fk_heeft_batch
	FOREIGN KEY ("BatchID") REFERENCES "Batch" ("BatchID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begroting" ADD CONSTRAINT "FK_Begroting_Periode"
	FOREIGN KEY ("PeriodeID") REFERENCES "Periode" ("PeriodeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT fk_heeft_begroting
	FOREIGN KEY ("BegrotingID") REFERENCES "Begroting" ("BegrotingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "FK_Begrotingregel_Hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "FK_Begrotingregel_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "FK_Begrotingregel_Product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "FK_Begrotingregel_Doelstelling"
	FOREIGN KEY ("DoelstellingID") REFERENCES "Doelstelling" ("DoelstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begrotingregel" ADD CONSTRAINT "FK_Begrotingregel_Hoofdstuk"
	FOREIGN KEY ("HoofdstukID") REFERENCES "Hoofdstuk" ("HoofdstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Debiteur" ADD CONSTRAINT "Fk_debiteur_rechtspersoon"
	FOREIGN KEY ("DebiteurID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doelstelling" ADD CONSTRAINT "FK_Doelstelling_Opdrachtgever"
	FOREIGN KEY ("OpdrachtgeverID") REFERENCES "Opdrachtgever" ("OpdrachtgeverID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Doelstelling" ADD CONSTRAINT fk_heeft_hoofdstuk
	FOREIGN KEY ("HoofdstukID") REFERENCES "Hoofdstuk" ("HoofdstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Factuur" ADD CONSTRAINT fk_heeft_debiteur
	FOREIGN KEY ("DebiteurID") REFERENCES "Debiteur" ("DebiteurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Factuur" ADD CONSTRAINT "FK_Factuur_Inkooporder"
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Factuur" ADD CONSTRAINT "FK_Factuur_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Factuur" ADD CONSTRAINT "FK_Factuur_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Factuurregel" ADD CONSTRAINT fk_heeft_factuur
	FOREIGN KEY ("FactuurID") REFERENCES "Factuur" ("FactuurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hoofdrekening" ADD CONSTRAINT "fk_valtBinnen_hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkooporder" ADD CONSTRAINT fk_oorspronkelijk_inkooporder
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkooporder" ADD CONSTRAINT fk_gerelateerd_inkooporder
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkooporder" ADD CONSTRAINT "FK_Inkooporder_Inkooppakket"
	FOREIGN KEY ("InkooppakketID") REFERENCES "Inkooppakket" ("InkooppakketID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inkooporder" ADD CONSTRAINT "FK_Inkooporder_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kostenplaats" ADD CONSTRAINT "FK_Kostenplaats_Opdrachtnemer"
	FOREIGN KEY ("OpdrachtnemerID") REFERENCES "Opdrachtnemer" ("OpdrachtnemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kostenplaats" ADD CONSTRAINT fk_heeft_organisatorischeeenhe
	FOREIGN KEY ("OrganisatorischeeenheidID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdrekening_activa" ADD CONSTRAINT "Fk_kp_hoofdrekening_activa_activa"
	FOREIGN KEY ("ActivaID") REFERENCES "Activa" ("ActivaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdrekening_activa" ADD CONSTRAINT "Fk_kp_hoofdrekening_activa_hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdrekening_kostenplaats" ADD CONSTRAINT "Fk_kp_hoofdrekening_kostenplaats_kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdrekening_kostenplaats" ADD CONSTRAINT "Fk_kp_hoofdrekening_kostenplaats_hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdstuk_periode" ADD CONSTRAINT "Fk_kp_hoofdstuk_periode_hoofdstuk"
	FOREIGN KEY ("HoofdstukID") REFERENCES "Hoofdstuk" ("HoofdstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_hoofdstuk_periode" ADD CONSTRAINT "Fk_kp_hoofdstuk_periode_periode"
	FOREIGN KEY ("PeriodeID") REFERENCES "Periode" ("PeriodeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inkooporder_hoofdrekening" ADD CONSTRAINT "Fk_kp_inkooporder_hoofdrekening_hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inkooporder_hoofdrekening" ADD CONSTRAINT "Fk_kp_inkooporder_hoofdrekening_inkooporder"
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kostenplaats_inkooporder" ADD CONSTRAINT "Fk_kp_kostenplaats_inkooporder_inkooporder"
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kostenplaats_inkooporder" ADD CONSTRAINT "Fk_kp_kostenplaats_inkooporder_kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kostenplaats_taakveld" ADD CONSTRAINT "Fk_kp_kostenplaats_taakveld_taakveld"
	FOREIGN KEY ("TaakveldID") REFERENCES "Taakveld" ("TaakveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kostenplaats_taakveld" ADD CONSTRAINT "Fk_kp_kostenplaats_taakveld_kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_project_kostenplaats" ADD CONSTRAINT "Fk_kp_project_kostenplaats_kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_project_kostenplaats" ADD CONSTRAINT "Fk_kp_project_kostenplaats_project"
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mutatie" ADD CONSTRAINT "fk_leidtTot_bankafschriftregel"
	FOREIGN KEY ("BankafschriftregelID") REFERENCES "Bankafschriftregel" ("BankafschriftregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mutatie" ADD CONSTRAINT "fk_leidtTot_batchregel"
	FOREIGN KEY ("BatchregelID") REFERENCES "Batchregel" ("BatchregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mutatie" ADD CONSTRAINT "fk_leidtTot_factuurregel"
	FOREIGN KEY ("FactuurregelID") REFERENCES "Factuurregel" ("FactuurregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mutatie" ADD CONSTRAINT "FK_Mutatie_Hoofdrekening"
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Mutatie" ADD CONSTRAINT "FK_Mutatie_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Opdrachtgever" ADD CONSTRAINT "FK_Opdrachtgever_Functie"
	FOREIGN KEY ("FunctieID") REFERENCES "Functie" ("FunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Opdrachtnemer" ADD CONSTRAINT "FK_Opdrachtnemer_Functie"
	FOREIGN KEY ("FunctieID") REFERENCES "Functie" ("FunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT fk_heeft_doelstelling
	FOREIGN KEY ("DoelstellingID") REFERENCES "Doelstelling" ("DoelstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "FK_Product_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "fk_isOpdrachtgever_opdrachtgev"
	FOREIGN KEY ("OpdrachtgeverID") REFERENCES "Opdrachtgever" ("OpdrachtgeverID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "fk_isOpdrachtnemer_opdrachtnem"
	FOREIGN KEY ("OpdrachtnemerID") REFERENCES "Opdrachtnemer" ("OpdrachtnemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subrekening" ADD CONSTRAINT fk_heeft_hoofdrekening
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subrekening" ADD CONSTRAINT fk_heeft_kostenplaats
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Werkorder" ADD CONSTRAINT fk_heeft_hoofdrekening
	FOREIGN KEY ("HoofdrekeningID") REFERENCES "Hoofdrekening" ("HoofdrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Werkorder" ADD CONSTRAINT fk_heeft_kostenplaats
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beoordeling" ADD CONSTRAINT "PK_Beoordeling"
	PRIMARY KEY ("BeoordelingID");

ALTER TABLE "Declaratie" ADD CONSTRAINT "PK_Declaratie"
	PRIMARY KEY ("DeclaratieID");

ALTER TABLE "Declaratiesoort" ADD CONSTRAINT "PK_Declaratiesoort"
	PRIMARY KEY ("DeclaratiesoortID");

ALTER TABLE "Dienstverband" ADD CONSTRAINT "PK_Dienstverband"
	PRIMARY KEY ("DienstverbandID");

ALTER TABLE "DisciplinaireMaatregel" ADD CONSTRAINT "PK_DisciplinaireMaatregel"
	PRIMARY KEY ("DisciplinaireMaatregelID");

ALTER TABLE "Formatieplaats" ADD CONSTRAINT "PK_Formatieplaats"
	PRIMARY KEY ("FormatieplaatsID");

ALTER TABLE "Functie" ADD CONSTRAINT "PK_Functie"
	PRIMARY KEY ("FunctieID");

ALTER TABLE "Functiehuis" ADD CONSTRAINT "PK_Functiehuis"
	PRIMARY KEY ("FunctiehuisID");

ALTER TABLE "Genotenopleiding" ADD CONSTRAINT "PK_Genotenopleiding"
	PRIMARY KEY ("GenotenopleidingID");

ALTER TABLE "Geweldsincident" ADD CONSTRAINT "PK_Geweldsincident"
	PRIMARY KEY ("GeweldsincidentID");

ALTER TABLE "IndividueelKeuzebudget" ADD CONSTRAINT "PK_IndividueelKeuzebudget"
	PRIMARY KEY ("IndividueelKeuzebudgetID");

ALTER TABLE "Inzet" ADD CONSTRAINT "PK_Inzet"
	PRIMARY KEY ("InzetID");

ALTER TABLE "Keuzebudgetbesteding" ADD CONSTRAINT "PK_Keuzebudgetbesteding"
	PRIMARY KEY ("KeuzebudgetbestedingID");

ALTER TABLE "Keuzebudgetbestedingsoort" ADD CONSTRAINT "PK_Keuzebudgetbestedingsoort"
	PRIMARY KEY ("KeuzebudgetbestedingsoortID");

ALTER TABLE "Normprofiel" ADD CONSTRAINT "PK_Normprofiel"
	PRIMARY KEY ("NormprofielID");

ALTER TABLE "Onderwijsinstituut" ADD CONSTRAINT "PK_Onderwijsinstituut"
	PRIMARY KEY ("OnderwijsinstituutID");

ALTER TABLE "Opleiding" ADD CONSTRAINT "PK_Opleiding"
	PRIMARY KEY ("OpleidingID");

ALTER TABLE "Organisatorischeeenheidhr" ADD CONSTRAINT "PK_Organisatorischeeenheidhr"
	PRIMARY KEY ("OrganisatorischeeenheidhrID");

ALTER TABLE "Relatie" ADD CONSTRAINT "PK_Relatie"
	PRIMARY KEY ("RelatieID");

ALTER TABLE "Rol" ADD CONSTRAINT "PK_Rol"
	PRIMARY KEY ("RolID");

ALTER TABLE "Sollicitant" ADD CONSTRAINT "PK_Sollicitant"
	PRIMARY KEY ("SollicitantID");

ALTER TABLE "Sollicitatie" ADD CONSTRAINT "PK_Sollicitatie"
	PRIMARY KEY ("SollicitatieID");

ALTER TABLE "Sollicitatiegesprek" ADD CONSTRAINT "PK_Sollicitatiegesprek"
	PRIMARY KEY ("SollicitatiegesprekID");

ALTER TABLE "Soortdisciplinairemaatregel" ADD CONSTRAINT "PK_Soortdisciplinairemaatregel"
	PRIMARY KEY ("SoortdisciplinairemaatregelID");

ALTER TABLE "Uren" ADD CONSTRAINT "PK_Uren"
	PRIMARY KEY ("UrenID");

ALTER TABLE "Vacature" ADD CONSTRAINT "PK_Vacature"
	PRIMARY KEY ("VacatureID");

ALTER TABLE "Verlof" ADD CONSTRAINT "PK_Verlof"
	PRIMARY KEY ("VerlofID");

ALTER TABLE "Verlofsoort" ADD CONSTRAINT "PK_Verlofsoort"
	PRIMARY KEY ("VerlofsoortID");

ALTER TABLE "Verzuim" ADD CONSTRAINT "PK_Verzuim"
	PRIMARY KEY ("VerzuimID");

ALTER TABLE "Verzuimsoort" ADD CONSTRAINT "PK_Verzuimsoort"
	PRIMARY KEY ("VerzuimsoortID");

ALTER TABLE "Werknemer" ADD CONSTRAINT "PK_Werknemer"
	PRIMARY KEY ("WerknemerID");

ALTER TABLE "Beoordeling" ADD CONSTRAINT "fk_beoordelingVan_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Beoordeling" ADD CONSTRAINT "fk_beoordeeltDoor_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Declaratie" ADD CONSTRAINT "FK_Declaratie_Declaratiesoort"
	FOREIGN KEY ("DeclaratiesoortID") REFERENCES "Declaratiesoort" ("DeclaratiesoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Declaratie" ADD CONSTRAINT "fk_dientIn_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienstverband" ADD CONSTRAINT "FK_Dienstverband_Functie"
	FOREIGN KEY ("FunctieID") REFERENCES "Functie" ("FunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienstverband" ADD CONSTRAINT "fk_toegewezenAan_formatieplaat"
	FOREIGN KEY ("FormatieplaatsID") REFERENCES "Formatieplaats" ("FormatieplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienstverband" ADD CONSTRAINT "fk_aantalVolgensInzet_inzet"
	FOREIGN KEY ("InzetID") REFERENCES "Inzet" ("InzetID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienstverband" ADD CONSTRAINT "fk_aantalVolgensInzet_uren"
	FOREIGN KEY ("UrenID") REFERENCES "Uren" ("UrenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienstverband" ADD CONSTRAINT "fk_medewerkerHeeftDienstverban"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "DisciplinaireMaatregel" ADD CONSTRAINT "FK_DisciplinaireMaatregel_Soortdisciplinairemaatregel"
	FOREIGN KEY ("SoortdisciplinairemaatregelID") REFERENCES "Soortdisciplinairemaatregel" ("SoortdisciplinairemaatregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "DisciplinaireMaatregel" ADD CONSTRAINT "fk_heeftMaatregel_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functie" ADD CONSTRAINT "fk_functieVanFormatieplaats_fo"
	FOREIGN KEY ("FormatieplaatsID") REFERENCES "Formatieplaats" ("FormatieplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functie" ADD CONSTRAINT "fk_inzetVoorFunctie_inzet"
	FOREIGN KEY ("InzetID") REFERENCES "Inzet" ("InzetID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functiehuis" ADD CONSTRAINT "fk_onderdeelVan_normprofiel"
	FOREIGN KEY ("NormprofielID") REFERENCES "Normprofiel" ("NormprofielID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Genotenopleiding" ADD CONSTRAINT "FK_Genotenopleiding_Opleiding"
	FOREIGN KEY ("OpleidingID") REFERENCES "Opleiding" ("OpleidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Genotenopleiding" ADD CONSTRAINT "fk_heeftGenoten_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "IndividueelKeuzebudget" ADD CONSTRAINT "FK_IndividueelKeuzebudget_Werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inzet" ADD CONSTRAINT "FK_Inzet_Organisatorischeeenheidhr"
	FOREIGN KEY ("OrganisatorischeeenheidhrID") REFERENCES "Organisatorischeeenheidhr" ("OrganisatorischeeenheidhrID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Keuzebudgetbesteding" ADD CONSTRAINT "fk_besteding_individueelKeuzeb"
	FOREIGN KEY ("IndividueelKeuzebudgetID") REFERENCES "IndividueelKeuzebudget" ("IndividueelKeuzebudgetID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Keuzebudgetbesteding" ADD CONSTRAINT "FK_Keuzebudgetbesteding_Keuzebudgetbestedingsoort"
	FOREIGN KEY ("KeuzebudgetbestedingsoortID") REFERENCES "Keuzebudgetbestedingsoort" ("KeuzebudgetbestedingsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dienstverband_organisatoris" ADD CONSTRAINT "Fk_kp_dienstverband_organisatoris_organisatorischeeenheidhr"
	FOREIGN KEY ("OrganisatorischeeenheidhrID") REFERENCES "Organisatorischeeenheidhr" ("OrganisatorischeeenheidhrID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dienstverband_organisatoris" ADD CONSTRAINT "Fk_kp_dienstverband_organisatoris_dienstverband"
	FOREIGN KEY ("DienstverbandID") REFERENCES "Dienstverband" ("DienstverbandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dienstverband_vestigingvanz" ADD CONSTRAINT "Fk_kp_dienstverband_vestigingvanz_dienstverband"
	FOREIGN KEY ("DienstverbandID") REFERENCES "Dienstverband" ("DienstverbandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dienstverband_vestigingvanz" ADD CONSTRAINT "Fk_kp_dienstverband_vestigingvanz_vestigingvanzaakbehandelende"
	FOREIGN KEY ("VestigingvanzaakbehandelendeID") REFERENCES "Vestigingvanzaakbehandelendeor" ("VestigingvanzaakbehandelendeorganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_opleiding_onderwijsinstituu" ADD CONSTRAINT "Fk_kp_opleiding_onderwijsinstituu_onderwijsinstituut"
	FOREIGN KEY ("OnderwijsinstituutID") REFERENCES "Onderwijsinstituut" ("OnderwijsinstituutID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_opleiding_onderwijsinstituu" ADD CONSTRAINT "Fk_kp_opleiding_onderwijsinstituu_opleiding"
	FOREIGN KEY ("OpleidingID") REFERENCES "Opleiding" ("OpleidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sollicitatiegesprek_sollici" ADD CONSTRAINT "Fk_kp_sollicitatiegesprek_sollici_sollicitant"
	FOREIGN KEY ("SollicitantID") REFERENCES "Sollicitant" ("SollicitantID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sollicitatiegesprek_sollici" ADD CONSTRAINT "Fk_kp_sollicitatiegesprek_sollici_sollicitatiegesprek"
	FOREIGN KEY ("SollicitatiegesprekID") REFERENCES "Sollicitatiegesprek" ("SollicitatiegesprekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sollicitatiegesprek_werknem" ADD CONSTRAINT "Fk_kp_sollicitatiegesprek_werknem_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_sollicitatiegesprek_werknem" ADD CONSTRAINT "Fk_kp_sollicitatiegesprek_werknem_sollicitatiegesprek"
	FOREIGN KEY ("SollicitatiegesprekID") REFERENCES "Sollicitatiegesprek" ("SollicitatiegesprekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_werknemer_rol" ADD CONSTRAINT "Fk_kp_werknemer_rol_rol"
	FOREIGN KEY ("RolID") REFERENCES "Rol" ("RolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_werknemer_rol" ADD CONSTRAINT "Fk_kp_werknemer_rol_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Normprofiel" ADD CONSTRAINT "fk_gebaseerdOp_functie"
	FOREIGN KEY ("FunctieID") REFERENCES "Functie" ("FunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onderwijsinstituut" ADD CONSTRAINT "Fk_onderwijsinstituut_nietnatuurlijkpersoon"
	FOREIGN KEY ("OnderwijsinstituutID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheidhr" ADD CONSTRAINT "fk_onderdeelVan_formatieplaats"
	FOREIGN KEY ("FormatieplaatsID") REFERENCES "Formatieplaats" ("FormatieplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheidhr" ADD CONSTRAINT "fk_hoortBij_rol"
	FOREIGN KEY ("RolID") REFERENCES "Rol" ("RolID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheidhr" ADD CONSTRAINT "Fk_organisatorischeeenheidhr_organisatorischeeenheid"
	FOREIGN KEY ("OrganisatorischeeenheidhrID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Relatie" ADD CONSTRAINT "FK_Relatie_Werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Relatie" ADD CONSTRAINT "fk_isPartnerVan_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Relatie" ADD CONSTRAINT "Fk_relatie_natuurlijkpersoon"
	FOREIGN KEY ("RelatieID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sollicitant" ADD CONSTRAINT "Fk_sollicitant_natuurlijkpersoon"
	FOREIGN KEY ("SollicitantID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sollicitatie" ADD CONSTRAINT "fk_solliciteertOpFunctie_solli"
	FOREIGN KEY ("SollicitantID") REFERENCES "Sollicitant" ("SollicitantID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sollicitatie" ADD CONSTRAINT "FK_Sollicitatie_Vacature"
	FOREIGN KEY ("VacatureID") REFERENCES "Vacature" ("VacatureID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sollicitatie" ADD CONSTRAINT fk_solliciteert_werknemer
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sollicitatiegesprek" ADD CONSTRAINT "FK_Sollicitatiegesprek_Sollicitatie"
	FOREIGN KEY ("SollicitatieID") REFERENCES "Sollicitatie" ("SollicitatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vacature" ADD CONSTRAINT "FK_Vacature_Functie"
	FOREIGN KEY ("FunctieID") REFERENCES "Functie" ("FunctieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verlof" ADD CONSTRAINT "FK_Verlof_Verlofsoort"
	FOREIGN KEY ("VerlofsoortID") REFERENCES "Verlofsoort" ("VerlofsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verlof" ADD CONSTRAINT "fk_heeftVerlof_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzuim" ADD CONSTRAINT "FK_Verzuim_Verzuimsoort"
	FOREIGN KEY ("VerzuimsoortID") REFERENCES "Verzuimsoort" ("VerzuimsoortID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verzuim" ADD CONSTRAINT "fk_heeftVerzuim_werknemer"
	FOREIGN KEY ("WerknemerID") REFERENCES "Werknemer" ("WerknemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Werknemer" ADD CONSTRAINT "FK_Werknemer_Geweldsincident"
	FOREIGN KEY ("GeweldsincidentID") REFERENCES "Geweldsincident" ("GeweldsincidentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Werknemer" ADD CONSTRAINT "Fk_werknemer_medewerker"
	FOREIGN KEY ("WerknemerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanvraag" ADD CONSTRAINT "PK_Aanvraag"
	PRIMARY KEY ("AanvraagID");

ALTER TABLE "Applicatie" ADD CONSTRAINT "PK_Applicatie"
	PRIMARY KEY ("ApplicatieID");

ALTER TABLE "Attribuutsoort" ADD CONSTRAINT "PK_Attribuutsoort"
	PRIMARY KEY ("AttribuutsoortID");

ALTER TABLE "Classificatie" ADD CONSTRAINT "PK_Classificatie"
	PRIMARY KEY ("ClassificatieID");

ALTER TABLE "Cmdb_item" ADD CONSTRAINT "PK_Cmdb_item"
	PRIMARY KEY ("Cmdb-itemID");

ALTER TABLE "Database" ADD CONSTRAINT "PK_Database"
	PRIMARY KEY ("DatabaseID");

ALTER TABLE "Datatype" ADD CONSTRAINT "PK_Datatype"
	PRIMARY KEY ("DatatypeID");

ALTER TABLE "Dienst" ADD CONSTRAINT "PK_Dienst"
	PRIMARY KEY ("DienstID");

ALTER TABLE "Domein_taakveld" ADD CONSTRAINT "PK_Domein_taakveld"
	PRIMARY KEY ("Domein/taakveldID");

ALTER TABLE "Enum_applicatiecategorie" ADD CONSTRAINT "PK_Enum_applicatiecategorie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_beheerstatus" ADD CONSTRAINT "PK_Enum_beheerstatus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_gebruikerrol" ADD CONSTRAINT "PK_Enum_gebruikerrol"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_packagingstatus" ADD CONSTRAINT "PK_Enum_packagingstatus"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_servertypes" ADD CONSTRAINT "PK_Enum_servertypes"
	PRIMARY KEY ("ID");

ALTER TABLE "ExterneBron" ADD CONSTRAINT "PK_ExterneBron"
	PRIMARY KEY ("ExterneBronID");

ALTER TABLE "Gebruikerrol" ADD CONSTRAINT "PK_Gebruikerrol"
	PRIMARY KEY ("GebruikerrolID");

ALTER TABLE "Gegeven" ADD CONSTRAINT "PK_Gegeven"
	PRIMARY KEY ("GegevenID");

ALTER TABLE "Generalisatie" ADD CONSTRAINT "PK_Generalisatie"
	PRIMARY KEY ("GeneralisatieID");

ALTER TABLE "Hardware" ADD CONSTRAINT "PK_Hardware"
	PRIMARY KEY ("HardwareID");

ALTER TABLE "Inventaris" ADD CONSTRAINT "PK_Inventaris"
	PRIMARY KEY ("InventarisID");

ALTER TABLE "Koppeling" ADD CONSTRAINT "PK_Koppeling"
	PRIMARY KEY ("KoppelingID");

ALTER TABLE "Licentie" ADD CONSTRAINT "PK_Licentie"
	PRIMARY KEY ("LicentieID");

ALTER TABLE "LinkbaarCmdb_item" ADD CONSTRAINT "PK_LinkbaarCmdb_item"
	PRIMARY KEY ("LinkbaarCmdb-itemID");

ALTER TABLE "Log" ADD CONSTRAINT "PK_Log"
	PRIMARY KEY ("LogID");

ALTER TABLE "Melding" ADD CONSTRAINT "PK_Melding"
	PRIMARY KEY ("MeldingID");

ALTER TABLE "Nertwerkcomponent" ADD CONSTRAINT "PK_Nertwerkcomponent"
	PRIMARY KEY ("NertwerkcomponentID");

ALTER TABLE "Notitie" ADD CONSTRAINT "PK_Notitie"
	PRIMARY KEY ("NotitieID");

ALTER TABLE "Objecttype" ADD CONSTRAINT "PK_Objecttype"
	PRIMARY KEY ("ObjecttypeID");

ALTER TABLE "Onderwerp" ADD CONSTRAINT "PK_Onderwerp"
	PRIMARY KEY ("OnderwerpID");

ALTER TABLE "Package" ADD CONSTRAINT "PK_Package"
	PRIMARY KEY ("PackageID");

ALTER TABLE "Prijzenboek" ADD CONSTRAINT "PK_Prijzenboek"
	PRIMARY KEY ("PrijzenboekID");

ALTER TABLE "Product" ADD CONSTRAINT "PK_Product"
	PRIMARY KEY ("ProductID");

ALTER TABLE "Relatiesoort" ADD CONSTRAINT "PK_Relatiesoort"
	PRIMARY KEY ("RelatiesoortID");

ALTER TABLE "Server" ADD CONSTRAINT "PK_Server"
	PRIMARY KEY ("ServerID");

ALTER TABLE "Software" ADD CONSTRAINT "PK_Software"
	PRIMARY KEY ("SoftwareID");

ALTER TABLE "Storing" ADD CONSTRAINT "PK_Storing"
	PRIMARY KEY ("StoringID");

ALTER TABLE "Telefoniegegevens" ADD CONSTRAINT "PK_Telefoniegegevens"
	PRIMARY KEY ("TelefoniegegevensID");

ALTER TABLE "Toegangsmiddel" ADD CONSTRAINT "PK_Toegangsmiddel"
	PRIMARY KEY ("ToegangsmiddelID");

ALTER TABLE "Versie" ADD CONSTRAINT "PK_Versie"
	PRIMARY KEY ("VersieID");

ALTER TABLE "Vervoersmiddel" ADD CONSTRAINT "PK_Vervoersmiddel"
	PRIMARY KEY ("VervoersmiddelID");

ALTER TABLE "Wijzigingsverzoek" ADD CONSTRAINT "PK_Wijzigingsverzoek"
	PRIMARY KEY ("WijzigingsverzoekID");

ALTER TABLE "Applicatie" ADD CONSTRAINT "Fk_applicatie_linkbaarCmdb_item"
	FOREIGN KEY ("ApplicatieID") REFERENCES "LinkbaarCmdb_item" ("LinkbaarCmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Applicatie" ADD CONSTRAINT "FK_Applicatie_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Attribuutsoort" ADD CONSTRAINT "FK_Attribuutsoort_Datatype"
	FOREIGN KEY ("DatatypeID") REFERENCES "Datatype" ("DatatypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Attribuutsoort" ADD CONSTRAINT fk_bezit_objecttype
	FOREIGN KEY ("ObjecttypeID") REFERENCES "Objecttype" ("ObjecttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Database" ADD CONSTRAINT "FK_Database_Server"
	FOREIGN KEY ("ServerID") REFERENCES "Server" ("ServerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Database" ADD CONSTRAINT "Fk_database_linkbaarCmdb_item"
	FOREIGN KEY ("DatabaseID") REFERENCES "LinkbaarCmdb_item" ("LinkbaarCmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienst" ADD CONSTRAINT "FK_Dienst_Domein_taakveld"
	FOREIGN KEY ("Domein_taakveldID") REFERENCES "Domein_taakveld" ("Domein/taakveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienst" ADD CONSTRAINT "FK_Dienst_Product"
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienst" ADD CONSTRAINT "FK_Dienst_Onderwerp"
	FOREIGN KEY ("OnderwerpID") REFERENCES "Onderwerp" ("OnderwerpID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Dienst" ADD CONSTRAINT "FK_Dienst_Zaaktype"
	FOREIGN KEY ("ZaaktypeID") REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebruikerrol" ADD CONSTRAINT "FK_Gebruikerrol_Applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebruikerrol" ADD CONSTRAINT "Fk_gebruikerrol_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gegeven" ADD CONSTRAINT fk_bevat_applicatie
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gegeven" ADD CONSTRAINT "fk_levert_externeBron"
	FOREIGN KEY ("ExterneBronID") REFERENCES "ExterneBron" ("ExterneBronID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gegeven" ADD CONSTRAINT "FK_Gegeven_Objecttype"
	FOREIGN KEY ("ObjecttypeID") REFERENCES "Objecttype" ("ObjecttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Generalisatie" ADD CONSTRAINT fk_objecttype_generalisatie
	FOREIGN KEY (subtype) REFERENCES "Objecttype" ("ObjecttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Hardware" ADD CONSTRAINT "Fk_hardware_cmdb_item"
	FOREIGN KEY ("HardwareID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inventaris" ADD CONSTRAINT "Fk_inventaris_cmdb_item"
	FOREIGN KEY ("InventarisID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Koppeling" ADD CONSTRAINT "FK_Koppeling_LinkbaarCmdb_item"
	FOREIGN KEY ("LinkbaarCmdb_itemID") REFERENCES "LinkbaarCmdb_item" ("LinkbaarCmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Koppeling" ADD CONSTRAINT "fk_linkVan_linkbaarCmdb_item"
	FOREIGN KEY ("LinkbaarCmdb_itemID") REFERENCES "LinkbaarCmdb_item" ("LinkbaarCmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_applicatie_document" ADD CONSTRAINT "Fk_kp_applicatie_document_applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_applicatie_document" ADD CONSTRAINT "Fk_kp_applicatie_document_document"
	FOREIGN KEY ("DocumentID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_gegeven_classificatie" ADD CONSTRAINT "Fk_kp_gegeven_classificatie_classificatie"
	FOREIGN KEY ("ClassificatieID") REFERENCES "Classificatie" ("ClassificatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_gegeven_classificatie" ADD CONSTRAINT "Fk_kp_gegeven_classificatie_gegeven"
	FOREIGN KEY ("GegevenID") REFERENCES "Gegeven" ("GegevenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Licentie" ADD CONSTRAINT "Fk_licentie_cmdb_item"
	FOREIGN KEY ("LicentieID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "LinkbaarCmdb_item" ADD CONSTRAINT "Fk_linkbaarCmdb_item_cmdb_item"
	FOREIGN KEY ("LinkbaarCmdb_itemID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Log" ADD CONSTRAINT "fk_heeftChangelog_cmdb_item"
	FOREIGN KEY ("Cmdb_itemID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nertwerkcomponent" ADD CONSTRAINT "Fk_nertwerkcomponent_cmdb_item"
	FOREIGN KEY ("NertwerkcomponentID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Notitie" ADD CONSTRAINT "fk_heeftNotities_applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Notitie" ADD CONSTRAINT "FK_Notitie_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onderwerp" ADD CONSTRAINT "fk_valtBinnen_domein_taakveld"
	FOREIGN KEY ("Domein_taakveldID") REFERENCES "Domein_taakveld" ("Domein/taakveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Package" ADD CONSTRAINT "fk_heeftPackages_applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "fk_valtBinnen_domein_taakveld"
	FOREIGN KEY ("Domein_taakveldID") REFERENCES "Domein_taakveld" ("Domein/taakveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Product" ADD CONSTRAINT "fk_heeftPrijs_prijzenboek"
	FOREIGN KEY ("PrijzenboekID") REFERENCES "Prijzenboek" ("PrijzenboekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Relatiesoort" ADD CONSTRAINT fk_bezit_objecttype
	FOREIGN KEY ("ObjecttypeID") REFERENCES "Objecttype" ("ObjecttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Relatiesoort" ADD CONSTRAINT "FK_Relatiesoort_Objecttype"
	FOREIGN KEY ("ObjecttypeID") REFERENCES "Objecttype" ("ObjecttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Server" ADD CONSTRAINT "Fk_server_linkbaarCmdb_item"
	FOREIGN KEY ("ServerID") REFERENCES "LinkbaarCmdb_item" ("LinkbaarCmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Server" ADD CONSTRAINT "FK_Server_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Software" ADD CONSTRAINT "Fk_software_cmdb_item"
	FOREIGN KEY ("SoftwareID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Toegangsmiddel" ADD CONSTRAINT "Fk_toegangsmiddel_cmdb_item"
	FOREIGN KEY ("ToegangsmiddelID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Versie" ADD CONSTRAINT "fk_heeftVersies_applicatie"
	FOREIGN KEY ("ApplicatieID") REFERENCES "Applicatie" ("ApplicatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vervoersmiddel" ADD CONSTRAINT "Fk_vervoersmiddel_cmdb_item"
	FOREIGN KEY ("VervoersmiddelID") REFERENCES "Cmdb_item" ("Cmdb-itemID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanbesteding" ADD CONSTRAINT "PK_Aanbesteding"
	PRIMARY KEY ("AanbestedingID");

ALTER TABLE "AanbestedingInhuur" ADD CONSTRAINT "PK_AanbestedingInhuur"
	PRIMARY KEY ("AanbestedingInhuurID");

ALTER TABLE "Aankondiging" ADD CONSTRAINT "PK_Aankondiging"
	PRIMARY KEY ("AankondigingID");

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "PK_AanvraagInkooporder"
	PRIMARY KEY ("AanvraagInkooporderID");

ALTER TABLE "Categorie" ADD CONSTRAINT "PK_Categorie"
	PRIMARY KEY ("CategorieID");

ALTER TABLE "Contract" ADD CONSTRAINT "PK_Contract"
	PRIMARY KEY ("ContractID");

ALTER TABLE "Cpv_code" ADD CONSTRAINT "PK_Cpv_code"
	PRIMARY KEY ("Cpv-codeID");

ALTER TABLE "Enum_aanbestedingsoort" ADD CONSTRAINT "PK_Enum_aanbestedingsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_inkooprol" ADD CONSTRAINT "PK_Enum_inkooprol"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_opdrachtcategorie" ADD CONSTRAINT "PK_Enum_opdrachtcategorie"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_opdrachtsoort" ADD CONSTRAINT "PK_Enum_opdrachtsoort"
	PRIMARY KEY ("ID");

ALTER TABLE "Formulierinhuur" ADD CONSTRAINT "PK_Formulierinhuur"
	PRIMARY KEY ("FormulierinhuurID");

ALTER TABLE "Formulierverlenginginhuur" ADD CONSTRAINT "PK_Formulierverlenginginhuur"
	PRIMARY KEY ("FormulierverlenginginhuurID");

ALTER TABLE "Gunning" ADD CONSTRAINT "PK_Gunning"
	PRIMARY KEY ("GunningID");

ALTER TABLE "Inkooppakket" ADD CONSTRAINT "PK_Inkooppakket"
	PRIMARY KEY ("InkooppakketID");

ALTER TABLE "Inschrijving" ADD CONSTRAINT "PK_Inschrijving"
	PRIMARY KEY ("InschrijvingID");

ALTER TABLE "Kandidaat" ADD CONSTRAINT "PK_Kandidaat"
	PRIMARY KEY ("KandidaatID");

ALTER TABLE "Kwalificatie" ADD CONSTRAINT "PK_Kwalificatie"
	PRIMARY KEY ("KwalificatieID");

ALTER TABLE "Leverancier" ADD CONSTRAINT "PK_Leverancier"
	PRIMARY KEY ("LeverancierID");

ALTER TABLE "Offerte" ADD CONSTRAINT "PK_Offerte"
	PRIMARY KEY ("OfferteID");

ALTER TABLE "Offerteaanvraag" ADD CONSTRAINT "PK_Offerteaanvraag"
	PRIMARY KEY ("OfferteaanvraagID");

ALTER TABLE "Selectietabelaanbesteding" ADD CONSTRAINT "PK_Selectietabelaanbesteding"
	PRIMARY KEY ("SelectietabelaanbestedingID");

ALTER TABLE "Startformulieraanbesteden" ADD CONSTRAINT "PK_Startformulieraanbesteden"
	PRIMARY KEY ("StartformulieraanbestedenID");

ALTER TABLE "Uitnodiging" ADD CONSTRAINT "PK_Uitnodiging"
	PRIMARY KEY ("UitnodigingID");

ALTER TABLE "Aanbesteding" ADD CONSTRAINT "fk_valtOnder_cpv_code"
	FOREIGN KEY ("Cpv_codeID") REFERENCES "Cpv_code" ("Cpv-codeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanbesteding" ADD CONSTRAINT "fk_mondtUit_startformulieraanb"
	FOREIGN KEY ("StartformulieraanbestedenID") REFERENCES "Startformulieraanbesteden" ("StartformulieraanbestedenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aanbesteding" ADD CONSTRAINT "FK_Aanbesteding_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanbestedingInhuur" ADD CONSTRAINT "FK_AanbestedingInhuur_Cpv_code"
	FOREIGN KEY ("Cpv_codeID") REFERENCES "Cpv_code" ("Cpv-codeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanbestedingInhuur" ADD CONSTRAINT "FK_AanbestedingInhuur_Categorie"
	FOREIGN KEY ("CategorieID") REFERENCES "Categorie" ("CategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanbestedingInhuur" ADD CONSTRAINT "fk_mondtUitIn_formulierinhuur"
	FOREIGN KEY ("FormulierinhuurID") REFERENCES "Formulierinhuur" ("FormulierinhuurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanbestedingInhuur" ADD CONSTRAINT "FK_AanbestedingInhuur_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aankondiging" ADD CONSTRAINT "FK_Aankondiging_Aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Aankondiging" ADD CONSTRAINT "fk_mondtUit_startformulieraanb"
	FOREIGN KEY ("StartformulieraanbestedenID") REFERENCES "Startformulieraanbesteden" ("StartformulieraanbestedenID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "FK_AanvraagInkooporder_Contract"
	FOREIGN KEY ("ContractID") REFERENCES "Contract" ("ContractID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "FK_AanvraagInkooporder_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "FK_AanvraagInkooporder_Inkooporder"
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "fk_vraagtAan_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "FK_AanvraagInkooporder_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanvraagInkooporder" ADD CONSTRAINT "FK_AanvraagInkooporder_Organisatorischeeenheid"
	FOREIGN KEY ("OrganisatorischeeenheidID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Contract" ADD CONSTRAINT "FK_Contract_Contract"
	FOREIGN KEY ("ContractID") REFERENCES "Contract" ("ContractID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Contract" ADD CONSTRAINT fk_contractant_leverancier
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Contract" ADD CONSTRAINT fk_betreft_inkooporder
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formulierinhuur" ADD CONSTRAINT "FK_Formulierinhuur_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formulierinhuur" ADD CONSTRAINT "FK_Formulierinhuur_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formulierverlenginginhuur" ADD CONSTRAINT "FK_Formulierverlenginginhuur_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formulierverlenginginhuur" ADD CONSTRAINT "FK_Formulierverlenginginhuur_Inkooporder"
	FOREIGN KEY ("InkooporderID") REFERENCES "Inkooporder" ("InkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Formulierverlenginginhuur" ADD CONSTRAINT "FK_Formulierverlenginginhuur_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gunning" ADD CONSTRAINT "fk_mondtUit_aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gunning" ADD CONSTRAINT "fk_mondtUit_aanbestedingInhuur"
	FOREIGN KEY ("AanbestedingInhuurID") REFERENCES "AanbestedingInhuur" ("AanbestedingInhuurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gunning" ADD CONSTRAINT "FK_Gunning_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inschrijving" ADD CONSTRAINT "FK_Inschrijving_Aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inschrijving" ADD CONSTRAINT fk_betreft_gunning
	FOREIGN KEY ("GunningID") REFERENCES "Gunning" ("GunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inschrijving" ADD CONSTRAINT fk_heeft_leverancier
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kandidaat" ADD CONSTRAINT "FK_Kandidaat_AanbestedingInhuur"
	FOREIGN KEY ("AanbestedingInhuurID") REFERENCES "AanbestedingInhuur" ("AanbestedingInhuurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kandidaat" ADD CONSTRAINT fk_betreft_gunning
	FOREIGN KEY ("GunningID") REFERENCES "Gunning" ("GunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kandidaat" ADD CONSTRAINT "fk_biedtAan_leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kandidaat" ADD CONSTRAINT "FK_Kandidaat_Natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inkooppakket_cpv_code" ADD CONSTRAINT "Fk_kp_inkooppakket_cpv_code_cpv_code"
	FOREIGN KEY ("Cpv_codeID") REFERENCES "Cpv_code" ("Cpv-codeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_inkooppakket_cpv_code" ADD CONSTRAINT "Fk_kp_inkooppakket_cpv_code_inkooppakket"
	FOREIGN KEY ("InkooppakketID") REFERENCES "Inkooppakket" ("InkooppakketID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leverancier_aanbestedingVa" ADD CONSTRAINT "Fk_kp_leverancier_aanbestedingva_leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leverancier_categorie" ADD CONSTRAINT "Fk_kp_leverancier_categorie_categorie"
	FOREIGN KEY ("CategorieID") REFERENCES "Categorie" ("CategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_leverancier_categorie" ADD CONSTRAINT "Fk_kp_leverancier_categorie_leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kwalificatie" ADD CONSTRAINT "FK_Kwalificatie_Aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kwalificatie" ADD CONSTRAINT fk_heeft_leverancier
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Leverancier" ADD CONSTRAINT "Fk_leverancier_rechtspersoon"
	FOREIGN KEY ("LeverancierID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Offerte" ADD CONSTRAINT "FK_Offerte_Aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Offerte" ADD CONSTRAINT fk_betreft_gunning
	FOREIGN KEY ("GunningID") REFERENCES "Gunning" ("GunningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Offerte" ADD CONSTRAINT "FK_Offerte_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Offerteaanvraag" ADD CONSTRAINT "FK_Offerteaanvraag_Aanbesteding"
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Offerteaanvraag" ADD CONSTRAINT "FK_Offerteaanvraag_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Startformulieraanbesteden" ADD CONSTRAINT "fk_dientIn_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Startformulieraanbesteden" ADD CONSTRAINT "FK_Startformulieraanbesteden_Zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitnodiging" ADD CONSTRAINT "FK_Uitnodiging_AanbestedingInhuur"
	FOREIGN KEY ("AanbestedingInhuurID") REFERENCES "AanbestedingInhuur" ("AanbestedingInhuurID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Uitnodiging" ADD CONSTRAINT "FK_Uitnodiging_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Programma" ADD CONSTRAINT "PK_Programma"
	PRIMARY KEY ("ProgrammaID");

ALTER TABLE "Project" ADD CONSTRAINT "PK_Project"
	PRIMARY KEY ("ProjectID");

ALTER TABLE "Betaalmoment" ADD CONSTRAINT "PK_Betaalmoment"
	PRIMARY KEY ("BetaalmomentID");

ALTER TABLE "Enum_subsidieniveau" ADD CONSTRAINT "PK_Enum_subsidieniveau"
	PRIMARY KEY ("ID");

ALTER TABLE "Rapportagemoment" ADD CONSTRAINT "PK_Rapportagemoment"
	PRIMARY KEY ("RapportagemomentID");

ALTER TABLE "Sector" ADD CONSTRAINT "PK_Sector"
	PRIMARY KEY ("SectorID");

ALTER TABLE "Subsidie" ADD CONSTRAINT "PK_Subsidie"
	PRIMARY KEY ("SubsidieID");

ALTER TABLE "Subsidieaanvraag" ADD CONSTRAINT "PK_Subsidieaanvraag"
	PRIMARY KEY ("SubsidieaanvraagID");

ALTER TABLE "Subsidiebeschikking" ADD CONSTRAINT "PK_Subsidiebeschikking"
	PRIMARY KEY ("SubsidiebeschikkingID");

ALTER TABLE "Subsidiecomponent" ADD CONSTRAINT "PK_Subsidiecomponent"
	PRIMARY KEY ("SubsidiecomponentID");

ALTER TABLE "Subsidieprogramma" ADD CONSTRAINT "PK_Subsidieprogramma"
	PRIMARY KEY ("SubsidieprogrammaID");

ALTER TABLE "Taak" ADD CONSTRAINT "PK_Taak"
	PRIMARY KEY ("TaakID");

ALTER TABLE "Betaalmoment" ADD CONSTRAINT fk_heeft_subsidiecomponent
	FOREIGN KEY ("SubsidiecomponentID") REFERENCES "Subsidiecomponent" ("SubsidiecomponentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rapportagemoment" ADD CONSTRAINT fk_heeft_subsidie
	FOREIGN KEY ("SubsidieID") REFERENCES "Subsidie" ("SubsidieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rapportagemoment" ADD CONSTRAINT fk_projectleider_rechtspersoon
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "FK_Subsidie_Sector"
	FOREIGN KEY ("SectorID") REFERENCES "Sector" ("SectorID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT fk_betreft_subsidieaanvraag
	FOREIGN KEY ("SubsidieaanvraagID") REFERENCES "Subsidieaanvraag" ("SubsidieaanvraagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT fk_betreft_subsidiebeschikking
	FOREIGN KEY ("SubsidiebeschikkingID") REFERENCES "Subsidiebeschikking" ("SubsidiebeschikkingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "fk_gaatOver_subsidieprogramma"
	FOREIGN KEY ("SubsidieprogrammaID") REFERENCES "Subsidieprogramma" ("SubsidieprogrammaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "FK_Subsidie_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "FK_Subsidie_Document"
	FOREIGN KEY ("DocumentID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT fk_aanvrager_medewerker
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "FK_Subsidie_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT fk_aanvrager_rechtspersoon
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidie" ADD CONSTRAINT "FK_Subsidie_Rechtspersoon"
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidiebeschikking" ADD CONSTRAINT "fk_mondtUit_subsidieaanvraag"
	FOREIGN KEY ("SubsidieaanvraagID") REFERENCES "Subsidieaanvraag" ("SubsidieaanvraagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidiecomponent" ADD CONSTRAINT "FK_Subsidiecomponent_Kostenplaats"
	FOREIGN KEY ("KostenplaatsID") REFERENCES "Kostenplaats" ("KostenplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Subsidieprogramma" ADD CONSTRAINT "FK_Subsidieprogramma_Organisatorischeeenheid"
	FOREIGN KEY ("OrganisatorischeeenheidID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Taak" ADD CONSTRAINT fk_heeft_subsidie
	FOREIGN KEY ("SubsidieID") REFERENCES "Subsidie" ("SubsidieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Taak" ADD CONSTRAINT "FK_Taak_Rechtspersoon"
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Foto" ADD CONSTRAINT "PK_Foto"
	PRIMARY KEY ("FotoID");

ALTER TABLE "Gebied" ADD CONSTRAINT "PK_Gebied"
	PRIMARY KEY ("GebiedID");

ALTER TABLE "Gebiedengroep" ADD CONSTRAINT "PK_Gebiedengroep"
	PRIMARY KEY ("GebiedengroepID");

ALTER TABLE "Lijn" ADD CONSTRAINT "PK_Lijn"
	PRIMARY KEY ("LijnID");

ALTER TABLE "Lijnengroep" ADD CONSTRAINT "PK_Lijnengroep"
	PRIMARY KEY ("LijnengroepID");

ALTER TABLE "Locatie" ADD CONSTRAINT "PK_Locatie"
	PRIMARY KEY ("LocatieID");

ALTER TABLE "Punt" ADD CONSTRAINT "PK_Punt"
	PRIMARY KEY ("PuntID");

ALTER TABLE "Puntengroep" ADD CONSTRAINT "PK_Puntengroep"
	PRIMARY KEY ("PuntengroepID");

ALTER TABLE "Video_opname" ADD CONSTRAINT "PK_Video_opname"
	PRIMARY KEY ("Video-opnameID");

ALTER TABLE "Foto" ADD CONSTRAINT "fk_monumentFotos_beschermdeSta"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Foto" ADD CONSTRAINT fk_heeft_vth_melding
	FOREIGN KEY ("Vth_meldingID") REFERENCES "Vth_melding" ("Vth-meldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebied" ADD CONSTRAINT "Fk_gebied_locatie"
	FOREIGN KEY ("GebiedID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebied" ADD CONSTRAINT fk_omvat_gebiedengroep
	FOREIGN KEY ("GebiedengroepID") REFERENCES "Gebiedengroep" ("GebiedengroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebiedengroep" ADD CONSTRAINT "Fk_gebiedengroep_locatie"
	FOREIGN KEY ("GebiedengroepID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Lijn" ADD CONSTRAINT "Fk_lijn_locatie"
	FOREIGN KEY ("LijnID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Lijn" ADD CONSTRAINT fk_omvat_lijnengroep
	FOREIGN KEY ("LijnengroepID") REFERENCES "Lijnengroep" ("LijnengroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Lijnengroep" ADD CONSTRAINT "Fk_lijnengroep_locatie"
	FOREIGN KEY ("LijnengroepID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Punt" ADD CONSTRAINT "Fk_punt_locatie"
	FOREIGN KEY ("PuntID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Punt" ADD CONSTRAINT fk_omvat_puntengroep
	FOREIGN KEY ("PuntengroepID") REFERENCES "Puntengroep" ("PuntengroepID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Puntengroep" ADD CONSTRAINT "Fk_puntengroep_locatie"
	FOREIGN KEY ("PuntengroepID") REFERENCES "Locatie" ("LocatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Video_opname" ADD CONSTRAINT fk_betreft_vergadering
	FOREIGN KEY ("VergaderingID") REFERENCES "Vergadering" ("VergaderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Adresseerbaarobject" ADD CONSTRAINT "PK_Adresseerbaarobject"
	PRIMARY KEY ("AdresseerbaarobjectID");

ALTER TABLE "Buurt" ADD CONSTRAINT "PK_Buurt"
	PRIMARY KEY ("BuurtID");

ALTER TABLE "Enum_boolean" ADD CONSTRAINT "PK_Enum_boolean"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_gebruiksdoel" ADD CONSTRAINT "PK_Enum_gebruiksdoel"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_ontsluitingswijzeverdiepi" ADD CONSTRAINT "PK_Enum_ontsluitingswijzeverdiepi"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_soortwoonobject" ADD CONSTRAINT "PK_Enum_soortwoonobject"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusligplaats" ADD CONSTRAINT "PK_Enum_statusligplaats"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusnummeraanduiding" ADD CONSTRAINT "PK_Enum_statusnummeraanduiding"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusopenbareruimte" ADD CONSTRAINT "PK_Enum_statusopenbareruimte"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statuspand" ADD CONSTRAINT "PK_Enum_statuspand"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusstandplaats" ADD CONSTRAINT "PK_Enum_statusstandplaats"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusverblijfsobject" ADD CONSTRAINT "PK_Enum_statusverblijfsobject"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statusvoortgangbouw" ADD CONSTRAINT "PK_Enum_statusvoortgangbouw"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_statuswoonplaats" ADD CONSTRAINT "PK_Enum_statuswoonplaats"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeadresseerbaarobject" ADD CONSTRAINT "PK_Enum_typeadresseerbaarobject"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_typeringopenbareruimte" ADD CONSTRAINT "PK_Enum_typeringopenbareruimte"
	PRIMARY KEY ("ID");

ALTER TABLE "Gemeente" ADD CONSTRAINT "PK_Gemeente"
	PRIMARY KEY ("GemeenteID");

ALTER TABLE "Ligplaats" ADD CONSTRAINT "PK_Ligplaats"
	PRIMARY KEY ("LigplaatsID");

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "PK_Nummeraanduiding"
	PRIMARY KEY ("NummeraanduidingID");

ALTER TABLE "Openbareruimte" ADD CONSTRAINT "PK_Openbareruimte"
	PRIMARY KEY ("OpenbareruimteID");

ALTER TABLE "Pand" ADD CONSTRAINT "PK_Pand"
	PRIMARY KEY ("PandID");

ALTER TABLE "Standplaats" ADD CONSTRAINT "PK_Standplaats"
	PRIMARY KEY ("StandplaatsID");

ALTER TABLE "Verblijfsobject" ADD CONSTRAINT "PK_Verblijfsobject"
	PRIMARY KEY ("VerblijfsobjectID");

ALTER TABLE "Wijk" ADD CONSTRAINT "PK_Wijk"
	PRIMARY KEY ("WijkID");

ALTER TABLE "Woonplaats" ADD CONSTRAINT "PK_Woonplaats"
	PRIMARY KEY ("WoonplaatsID");

ALTER TABLE "Buurt" ADD CONSTRAINT "FK_Buurt_Wijk"
	FOREIGN KEY ("WijkID") REFERENCES "Wijk" ("WijkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Buurt" ADD CONSTRAINT "fk_ligtIn_openbareruimte"
	FOREIGN KEY ("OpenbareruimteID") REFERENCES "Openbareruimte" ("OpenbareruimteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_gebruiksdoel" ADD CONSTRAINT "FK_Enum_gebruiksdoel_Verblijfsobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Verblijfsobject" ("VerblijfsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gemeente" ADD CONSTRAINT "fk_isOvergegaanIn_gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verblijfsobject_pand" ADD CONSTRAINT "Fk_kp_verblijfsobject_pand_pand"
	FOREIGN KEY ("PandID") REFERENCES "Pand" ("PandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verblijfsobject_pand" ADD CONSTRAINT "Fk_kp_verblijfsobject_pand_verblijfsobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Verblijfsobject" ("VerblijfsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_woonplaats_gemeente" ADD CONSTRAINT "Fk_kp_woonplaats_gemeente_gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_woonplaats_gemeente" ADD CONSTRAINT "Fk_kp_woonplaats_gemeente_woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ligplaats" ADD CONSTRAINT "Fk_ligplaats_adresseerbaarobject"
	FOREIGN KEY ("LigplaatsID") REFERENCES "Adresseerbaarobject" ("AdresseerbaarobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "FK_Nummeraanduiding_Openbareruimte"
	FOREIGN KEY ("OpenbareruimteID") REFERENCES "Openbareruimte" ("OpenbareruimteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "FK_Nummeraanduiding_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "fk_heeftAlsHoofdadres_adressee"
	FOREIGN KEY ("AdresseerbaarobjectID") REFERENCES "Adresseerbaarobject" ("AdresseerbaarobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "fk_heeftAlsNevenadres_adressee"
	FOREIGN KEY ("AdresseerbaarobjectID") REFERENCES "Adresseerbaarobject" ("AdresseerbaarobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Openbareruimte" ADD CONSTRAINT "FK_Openbareruimte_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Standplaats" ADD CONSTRAINT "Fk_standplaats_adresseerbaarobject"
	FOREIGN KEY ("StandplaatsID") REFERENCES "Adresseerbaarobject" ("AdresseerbaarobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfsobject" ADD CONSTRAINT "Fk_verblijfsobject_adresseerbaarobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Adresseerbaarobject" ("AdresseerbaarobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Wijk" ADD CONSTRAINT "FK_Wijk_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Periode" ADD CONSTRAINT "PK_Periode"
	PRIMARY KEY ("PeriodeID");

ALTER TABLE "Adresaanduiding" ADD CONSTRAINT "PK_Adresaanduiding"
	PRIMARY KEY ("AdresaanduidingID");

ALTER TABLE "Correspondentieadresbuitenland" ADD CONSTRAINT "PK_Correspondentieadresbuitenland"
	PRIMARY KEY ("CorrespondentieadresbuitenlandID");

ALTER TABLE "Geboorteingeschrevennatuurlijk" ADD CONSTRAINT "PK_Geboorteingeschrevennatuurlijk"
	PRIMARY KEY ("GeboorteingeschrevennatuurlijkpersoonID");

ALTER TABLE "Geboorteingeschrevenpersoon" ADD CONSTRAINT "PK_Geboorteingeschrevenpersoon"
	PRIMARY KEY ("GeboorteingeschrevenpersoonID");

ALTER TABLE "Handelsnamenmaatschappelijkeac" ADD CONSTRAINT "PK_Handelsnamenmaatschappelijkeac"
	PRIMARY KEY ("HandelsnamenmaatschappelijkeactiviteitID");

ALTER TABLE "Handelsnamenvestiging" ADD CONSTRAINT "PK_Handelsnamenvestiging"
	PRIMARY KEY ("HandelsnamenvestigingID");

ALTER TABLE "Koopsomkadastraleonroerendezaa" ADD CONSTRAINT "PK_Koopsomkadastraleonroerendezaa"
	PRIMARY KEY ("KoopsomkadastraleonroerendezaakID");

ALTER TABLE "Locatiekadastraleonroerendezaa" ADD CONSTRAINT "PK_Locatiekadastraleonroerendezaa"
	PRIMARY KEY ("LocatiekadastraleonroerendezaakID");

ALTER TABLE "Migratieingeschrevennatuurlijk" ADD CONSTRAINT "PK_Migratieingeschrevennatuurlijk"
	PRIMARY KEY ("MigratieingeschrevennatuurlijkpersoonID");

ALTER TABLE "Naamaanschrijvingnatuurlijkper" ADD CONSTRAINT "PK_Naamaanschrijvingnatuurlijkper"
	PRIMARY KEY ("NaamaanschrijvingnatuurlijkpersoonID");

ALTER TABLE "Naamgebruiknatuurlijkpersoon" ADD CONSTRAINT "PK_Naamgebruiknatuurlijkpersoon"
	PRIMARY KEY ("NaamgebruiknatuurlijkpersoonID");

ALTER TABLE "Naamnatuurlijkpersoon" ADD CONSTRAINT "PK_Naamnatuurlijkpersoon"
	PRIMARY KEY ("NaamnatuurlijkpersoonID");

ALTER TABLE "Nationaliteitingeschrevennatuu" ADD CONSTRAINT "PK_Nationaliteitingeschrevennatuu"
	PRIMARY KEY ("NationaliteitingeschrevennatuurlijkpersoonID");

ALTER TABLE "Nederlandsenationaliteitingesc" ADD CONSTRAINT "PK_Nederlandsenationaliteitingesc"
	PRIMARY KEY ("NederlandsenationaliteitingeschrevenpersoonID");

ALTER TABLE "Ontbindinghuwelijk_geregistree" ADD CONSTRAINT "PK_Ontbindinghuwelijk_geregistree"
	PRIMARY KEY ("Ontbindinghuwelijk/geregistreerdpartnerschapID");

ALTER TABLE "Overlijdeningeschrevennatuurli" ADD CONSTRAINT "PK_Overlijdeningeschrevennatuurli"
	PRIMARY KEY ("OverlijdeningeschrevennatuurlijkpersoonID");

ALTER TABLE "Overlijdeningeschrevenpersoon" ADD CONSTRAINT "PK_Overlijdeningeschrevenpersoon"
	PRIMARY KEY ("OverlijdeningeschrevenpersoonID");

ALTER TABLE "Postadres" ADD CONSTRAINT "PK_Postadres"
	PRIMARY KEY ("PostadresID");

ALTER TABLE "Rekeningnummer" ADD CONSTRAINT "PK_Rekeningnummer"
	PRIMARY KEY ("RekeningnummerID");

ALTER TABLE "Samengesteldenaamnatuurlijkper" ADD CONSTRAINT "PK_Samengesteldenaamnatuurlijkper"
	PRIMARY KEY ("SamengesteldenaamnatuurlijkpersoonID");

ALTER TABLE "Sbiactiviteitvestiging" ADD CONSTRAINT "PK_Sbiactiviteitvestiging"
	PRIMARY KEY ("SbiactiviteitvestigingID");

ALTER TABLE "Sluitingofaangaanhuwelijkofger" ADD CONSTRAINT "PK_Sluitingofaangaanhuwelijkofger"
	PRIMARY KEY ("SluitingofaangaanhuwelijkofgeregistreerdpartnerschapID");

ALTER TABLE "Soortfunctioneelgebied" ADD CONSTRAINT "PK_Soortfunctioneelgebied"
	PRIMARY KEY ("SoortfunctioneelgebiedID");

ALTER TABLE "Soortkunstwerk" ADD CONSTRAINT "PK_Soortkunstwerk"
	PRIMARY KEY ("SoortkunstwerkID");

ALTER TABLE "Soortoverigbouwwerk" ADD CONSTRAINT "PK_Soortoverigbouwwerk"
	PRIMARY KEY ("SoortoverigbouwwerkID");

ALTER TABLE "Soortscheiding" ADD CONSTRAINT "PK_Soortscheiding"
	PRIMARY KEY ("SoortscheidingID");

ALTER TABLE "Soortspoor" ADD CONSTRAINT "PK_Soortspoor"
	PRIMARY KEY ("SoortspoorID");

ALTER TABLE "Splitsingstekeningreferentie" ADD CONSTRAINT "PK_Splitsingstekeningreferentie"
	PRIMARY KEY ("SplitsingstekeningreferentieID");

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "PK_Verblijfadresingeschrevennatuu"
	PRIMARY KEY ("VerblijfadresingeschrevennatuurlijkpersoonID");

ALTER TABLE "Verblijfadresingeschrevenperso" ADD CONSTRAINT "PK_Verblijfadresingeschrevenperso"
	PRIMARY KEY ("VerblijfadresingeschrevenpersoonID");

ALTER TABLE "Verblijfbuitenland" ADD CONSTRAINT "PK_Verblijfbuitenland"
	PRIMARY KEY ("VerblijfbuitenlandID");

ALTER TABLE "Verblijfbuitenlandsubject" ADD CONSTRAINT "PK_Verblijfbuitenlandsubject"
	PRIMARY KEY ("VerblijfbuitenlandsubjectID");

ALTER TABLE "Verblijfsrechtingeschrevennatu" ADD CONSTRAINT "PK_Verblijfsrechtingeschrevennatu"
	PRIMARY KEY ("VerblijfsrechtingeschrevennatuurlijkpersoonID");

ALTER TABLE "Verstrekkingsbeperkingpartieel" ADD CONSTRAINT "PK_Verstrekkingsbeperkingpartieel"
	PRIMARY KEY ("VerstrekkingsbeperkingpartieelingeschrevennatuurlijkpersoonID");

ALTER TABLE "Geboorteingeschrevennatuurlijk" ADD CONSTRAINT "FK_Geboorteingeschrevennatuurlijk_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Koopsomkadastraleonroerendezaa" ADD CONSTRAINT fk_kadastraleonroerendezaak_ko
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Locatiekadastraleonroerendezaa" ADD CONSTRAINT fk_kadastraleonroerendezaak_lo
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ontbindinghuwelijk_geregistree" ADD CONSTRAINT "FK_Ontbindinghuwelijk_geregistree_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overlijdeningeschrevennatuurli" ADD CONSTRAINT "FK_Overlijdeningeschrevennatuurli_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Postadres" ADD CONSTRAINT "FK_Postadres_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sbiactiviteitvestiging" ADD CONSTRAINT fk_vestiging_sbiactiviteitvest
	FOREIGN KEY ("VestigingID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Sluitingofaangaanhuwelijkofger" ADD CONSTRAINT "FK_Sluitingofaangaanhuwelijkofger_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Soortfunctioneelgebied" ADD CONSTRAINT fk_functioneelgebied_soortfunc
	FOREIGN KEY ("FunctioneelgebiedID") REFERENCES "Functioneelgebied" ("FunctioneelgebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Soortkunstwerk" ADD CONSTRAINT fk_kunstwerkdeel_soortkunstwer
	FOREIGN KEY ("KunstwerkdeelID") REFERENCES "Kunstwerkdeel" ("KunstwerkdeelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Soortoverigbouwwerk" ADD CONSTRAINT fk_overigbouwwerk_soortoverigb
	FOREIGN KEY ("OverigbouwwerkID") REFERENCES "Overigbouwwerk" ("OverigbouwwerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Soortscheiding" ADD CONSTRAINT fk_scheiding_soortscheiding
	FOREIGN KEY ("ScheidingID") REFERENCES "Scheiding" ("ScheidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Soortspoor" ADD CONSTRAINT fk_spoor_soortspoor
	FOREIGN KEY ("SpoorID") REFERENCES "Spoor" ("SpoorID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Splitsingstekeningreferentie" ADD CONSTRAINT fk_appartementsrechtsplitsing_
	FOREIGN KEY ("AppartementsrechtsplitsingID") REFERENCES "Appartementsrechtsplitsing" ("AppartementsrechtsplitsingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "FK_Verblijfadresingeschrevennatuu_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "FK_Verblijfadresingeschrevennatuu_Verblijfsobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Verblijfsobject" ("VerblijfsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "FK_Verblijfadresingeschrevennatuu_Standplaats"
	FOREIGN KEY ("StandplaatsID") REFERENCES "Standplaats" ("StandplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "FK_Verblijfadresingeschrevennatuu_Adresseerbaarobjectaanduiding"
	FOREIGN KEY ("AdresseerbaarobjectaanduidinID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfadresingeschrevennatuu" ADD CONSTRAINT "FK_Verblijfadresingeschrevennatuu_Ligplaats"
	FOREIGN KEY ("LigplaatsID") REFERENCES "Ligplaats" ("LigplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Locatieaanduidingadreswozobjec" ADD CONSTRAINT "PK_Locatieaanduidingadreswozobjec"
	PRIMARY KEY ("LocatieaanduidingadreswozobjectID");

ALTER TABLE "Aantekening" ADD CONSTRAINT "PK_Aantekening"
	PRIMARY KEY ("AantekeningID");

ALTER TABLE "Adresbuitenland" ADD CONSTRAINT "PK_Adresbuitenland"
	PRIMARY KEY ("AdresbuitenlandID");

ALTER TABLE "Adresseerbaarobjectaanduiding" ADD CONSTRAINT "PK_Adresseerbaarobjectaanduiding"
	PRIMARY KEY ("AdresseerbaarobjectaanduidingID");

ALTER TABLE "Appartementsrecht" ADD CONSTRAINT "PK_Appartementsrecht"
	PRIMARY KEY ("AppartementsrechtID");

ALTER TABLE "Appartementsrechtsplitsing" ADD CONSTRAINT "PK_Appartementsrechtsplitsing"
	PRIMARY KEY ("AppartementsrechtsplitsingID");

ALTER TABLE "Begroeidterreindeel" ADD CONSTRAINT "PK_Begroeidterreindeel"
	PRIMARY KEY ("BegroeidterreindeelID");

ALTER TABLE "Benoemdobject" ADD CONSTRAINT "PK_Benoemdobject"
	PRIMARY KEY ("BenoemdobjectID");

ALTER TABLE "Benoemdterrein" ADD CONSTRAINT "PK_Benoemdterrein"
	PRIMARY KEY ("BenoemdterreinID");

ALTER TABLE "Briefadres" ADD CONSTRAINT "PK_Briefadres"
	PRIMARY KEY ("BriefadresID");

ALTER TABLE "Buurt" ADD CONSTRAINT "PK_Buurt"
	PRIMARY KEY ("BuurtID");

ALTER TABLE "Functioneelgebied" ADD CONSTRAINT "PK_Functioneelgebied"
	PRIMARY KEY ("FunctioneelgebiedID");

ALTER TABLE "Gebied" ADD CONSTRAINT "PK_Gebied"
	PRIMARY KEY ("GebiedID");

ALTER TABLE "Gebouwdobject" ADD CONSTRAINT "PK_Gebouwdobject"
	PRIMARY KEY ("GebouwdobjectID");

ALTER TABLE "Gebouwinstallatie" ADD CONSTRAINT "PK_Gebouwinstallatie"
	PRIMARY KEY ("GebouwinstallatieID");

ALTER TABLE "Gemeente" ADD CONSTRAINT "PK_Gemeente"
	PRIMARY KEY ("GemeenteID");

ALTER TABLE "Huishouden" ADD CONSTRAINT "PK_Huishouden"
	PRIMARY KEY ("HuishoudenID");

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT "PK_Ingeschrevenpersoon"
	PRIMARY KEY ("IngeschrevenpersoonID");

ALTER TABLE "Ingezetene" ADD CONSTRAINT "PK_Ingezetene"
	PRIMARY KEY ("IngezeteneID");

ALTER TABLE "Inrichtingselement" ADD CONSTRAINT "PK_Inrichtingselement"
	PRIMARY KEY ("InrichtingselementID");

ALTER TABLE "Kadastraalperceel" ADD CONSTRAINT "PK_Kadastraalperceel"
	PRIMARY KEY ("KadastraalperceelID");

ALTER TABLE "Kadastraleonroerendezaak" ADD CONSTRAINT "PK_Kadastraleonroerendezaak"
	PRIMARY KEY ("KadastraleonroerendezaakID");

ALTER TABLE "Kadastraleonroerendezaakaantek" ADD CONSTRAINT "PK_Kadastraleonroerendezaakaantek"
	PRIMARY KEY ("KadastraleonroerendezaakaantekeningID");

ALTER TABLE "Kunstwerkdeel" ADD CONSTRAINT "PK_Kunstwerkdeel"
	PRIMARY KEY ("KunstwerkdeelID");

ALTER TABLE "Ligplaats" ADD CONSTRAINT "PK_Ligplaats"
	PRIMARY KEY ("LigplaatsID");

ALTER TABLE "Maatschappelijkeactiviteit" ADD CONSTRAINT "PK_Maatschappelijkeactiviteit"
	PRIMARY KEY ("MaatschappelijkeactiviteitID");

ALTER TABLE "Nationaliteit" ADD CONSTRAINT "PK_Nationaliteit"
	PRIMARY KEY ("NationaliteitID");

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT "PK_Natuurlijkpersoon"
	PRIMARY KEY ("NatuurlijkpersoonID");

ALTER TABLE "Nietnatuurlijkpersoon" ADD CONSTRAINT "PK_Nietnatuurlijkpersoon"
	PRIMARY KEY ("NietnatuurlijkpersoonID");

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "PK_Nummeraanduiding"
	PRIMARY KEY ("NummeraanduidingID");

ALTER TABLE "Onbegroeidterreindeel" ADD CONSTRAINT "PK_Onbegroeidterreindeel"
	PRIMARY KEY ("OnbegroeidterreindeelID");

ALTER TABLE "OnbestemdAdres" ADD CONSTRAINT "PK_OnbestemdAdres"
	PRIMARY KEY ("OnbestemdAdresID");

ALTER TABLE "Ondersteunendwaterdeel" ADD CONSTRAINT "PK_Ondersteunendwaterdeel"
	PRIMARY KEY ("OndersteunendwaterdeelID");

ALTER TABLE "Ondersteunendwegdeel" ADD CONSTRAINT "PK_Ondersteunendwegdeel"
	PRIMARY KEY ("OndersteunendwegdeelID");

ALTER TABLE "Openbareruimte" ADD CONSTRAINT "PK_Openbareruimte"
	PRIMARY KEY ("OpenbareruimteID");

ALTER TABLE "Overbruggingsdeel" ADD CONSTRAINT "PK_Overbruggingsdeel"
	PRIMARY KEY ("OverbruggingsdeelID");

ALTER TABLE "Overigbenoemdterrein" ADD CONSTRAINT "PK_Overigbenoemdterrein"
	PRIMARY KEY ("OverigbenoemdterreinID");

ALTER TABLE "Overigbouwwerk" ADD CONSTRAINT "PK_Overigbouwwerk"
	PRIMARY KEY ("OverigbouwwerkID");

ALTER TABLE "Overigeadresseerbaarobjectaand" ADD CONSTRAINT "PK_Overigeadresseerbaarobjectaand"
	PRIMARY KEY ("OverigeadresseerbaarobjectaanduidingID");

ALTER TABLE "Overigescheiding" ADD CONSTRAINT "PK_Overigescheiding"
	PRIMARY KEY ("OverigescheidingID");

ALTER TABLE "Overiggebouwdobject" ADD CONSTRAINT "PK_Overiggebouwdobject"
	PRIMARY KEY ("OveriggebouwdobjectID");

ALTER TABLE "Pand" ADD CONSTRAINT "PK_Pand"
	PRIMARY KEY ("PandID");

ALTER TABLE "Rechtspersoon" ADD CONSTRAINT "PK_Rechtspersoon"
	PRIMARY KEY ("RechtspersoonID");

ALTER TABLE "Reisdocument" ADD CONSTRAINT "PK_Reisdocument"
	PRIMARY KEY ("ReisdocumentID");

ALTER TABLE "Scheiding" ADD CONSTRAINT "PK_Scheiding"
	PRIMARY KEY ("ScheidingID");

ALTER TABLE "Spoor" ADD CONSTRAINT "PK_Spoor"
	PRIMARY KEY ("SpoorID");

ALTER TABLE "Standplaats" ADD CONSTRAINT "PK_Standplaats"
	PRIMARY KEY ("StandplaatsID");

ALTER TABLE "Tenaamstelling" ADD CONSTRAINT "PK_Tenaamstelling"
	PRIMARY KEY ("TenaamstellingID");

ALTER TABLE "Tunneldeel" ADD CONSTRAINT "PK_Tunneldeel"
	PRIMARY KEY ("TunneldeelID");

ALTER TABLE "Vegetatieobject" ADD CONSTRAINT "PK_Vegetatieobject"
	PRIMARY KEY ("VegetatieobjectID");

ALTER TABLE "Verblijfsobject" ADD CONSTRAINT "PK_Verblijfsobject"
	PRIMARY KEY ("VerblijfsobjectID");

ALTER TABLE "Verblijfstitel" ADD CONSTRAINT "PK_Verblijfstitel"
	PRIMARY KEY ("VerblijfstitelID");

ALTER TABLE "Vestiging" ADD CONSTRAINT "PK_Vestiging"
	PRIMARY KEY ("VestigingID");

ALTER TABLE "Waterdeel" ADD CONSTRAINT "PK_Waterdeel"
	PRIMARY KEY ("WaterdeelID");

ALTER TABLE "Wegdeel" ADD CONSTRAINT "PK_Wegdeel"
	PRIMARY KEY ("WegdeelID");

ALTER TABLE "Wijk" ADD CONSTRAINT "PK_Wijk"
	PRIMARY KEY ("WijkID");

ALTER TABLE "Woonplaats" ADD CONSTRAINT "PK_Woonplaats"
	PRIMARY KEY ("WoonplaatsID");

ALTER TABLE "Woz_deelobject" ADD CONSTRAINT "PK_Woz_deelobject"
	PRIMARY KEY ("Woz-deelobjectID");

ALTER TABLE "Woz_object" ADD CONSTRAINT "PK_Woz_object"
	PRIMARY KEY ("Woz-objectID");

ALTER TABLE "Woz_waarde" ADD CONSTRAINT "PK_Woz_waarde"
	PRIMARY KEY ("Woz-waardeID");

ALTER TABLE "Zakelijkrecht" ADD CONSTRAINT "PK_Zakelijkrecht"
	PRIMARY KEY ("ZakelijkrechtID");

ALTER TABLE "Zekerheidsrecht" ADD CONSTRAINT "PK_Zekerheidsrecht"
	PRIMARY KEY ("ZekerheidsrechtID");

ALTER TABLE "Aantekening" ADD CONSTRAINT fk_tenaamstelling_aantekening
	FOREIGN KEY ("TenaamstellingID") REFERENCES "Tenaamstelling" ("TenaamstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Adresbuitenland" ADD CONSTRAINT fk_heeft_rechtspersoon
	FOREIGN KEY ("RechtspersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Adresseerbaarobjectaanduiding" ADD CONSTRAINT "fk_heeftAlsHoofdadres_hoofdadr"
	FOREIGN KEY ("HoofdadresID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Appartementsrecht" ADD CONSTRAINT "Fk_appartementsrecht_kadastraleonroerendezaak"
	FOREIGN KEY ("AppartementsrechtID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Begroeidterreindeel" ADD CONSTRAINT "Fk_begroeidterreindeel_geo_object"
	FOREIGN KEY ("BegroeidterreindeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Benoemdobject" ADD CONSTRAINT "fk_isOntstaanUit/OvergegaanIn_"
	FOREIGN KEY ("BenoemdobjectID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Benoemdobject" ADD CONSTRAINT "Fk_benoemdobject_object"
	FOREIGN KEY ("BenoemdobjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Benoemdterrein" ADD CONSTRAINT "Fk_benoemdterrein_benoemdobject"
	FOREIGN KEY ("BenoemdterreinID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Briefadres" ADD CONSTRAINT "FK_Briefadres_Nummeraanduiding"
	FOREIGN KEY ("NummeraanduidingID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Buurt" ADD CONSTRAINT "FK_Buurt_Wijk"
	FOREIGN KEY ("WijkID") REFERENCES "Wijk" ("WijkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Buurt" ADD CONSTRAINT "fk_komtOvereen_gebied"
	FOREIGN KEY ("GebiedID") REFERENCES "Gebied" ("GebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Buurt" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Functioneelgebied" ADD CONSTRAINT "Fk_functioneelgebied_geo_object"
	FOREIGN KEY ("FunctioneelgebiedID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebouwdobject" ADD CONSTRAINT "Fk_gebouwdobject_benoemdobject"
	FOREIGN KEY ("GebouwdobjectID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gebouwinstallatie" ADD CONSTRAINT "Fk_gebouwinstallatie_geo_object"
	FOREIGN KEY ("GebouwinstallatieID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Gemeente" ADD CONSTRAINT "fk_isOvergegaanIn_gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Huishouden" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT "FK_Ingeschrevenpersoon_Nummeraanduiding"
	FOREIGN KEY ("NummeraanduidingID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT fk_ouder1_ouder_1
	FOREIGN KEY ("Ouder_1ID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT fk_ouder2_ouder_2
	FOREIGN KEY ("Ouder_2ID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT "Fk_ingeschrevenpersoon_natuurlijkpersoon"
	FOREIGN KEY ("IngeschrevenpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingeschrevenpersoon" ADD CONSTRAINT "FK_Ingeschrevenpersoon_Briefadres"
	FOREIGN KEY ("BriefadresID") REFERENCES "Briefadres" ("BriefadresID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingezetene" ADD CONSTRAINT "Fk_ingezetene_ingeschrevenpersoon"
	FOREIGN KEY ("IngezeteneID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingezetene" ADD CONSTRAINT "FK_Ingezetene_Verblijfstitel"
	FOREIGN KEY (verblijfstitel) REFERENCES "Verblijfstitel" ("VerblijfstitelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ingezetene" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inrichtingselement" ADD CONSTRAINT "Fk_inrichtingselement_geo_object"
	FOREIGN KEY ("InrichtingselementID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Inrichtingselement" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraalperceel" ADD CONSTRAINT "Fk_kadastraalperceel_kadastraleonroerendezaak"
	FOREIGN KEY ("KadastraalperceelID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraalperceel" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraleonroerendezaak" ADD CONSTRAINT fk_gerelateerd_kadastraleonroe
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraleonroerendezaak" ADD CONSTRAINT "Fk_kadastraleonroerendezaak_object"
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraleonroerendezaak" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraleonroerendezaak" ADD CONSTRAINT "fk_betreft_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kadastraleonroerendezaakaantek" ADD CONSTRAINT "FK_Kadastraleonroerendezaakaantek_Kadastraleonroerendezaak"
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_gebouwdobject_gebruiksdoel" ADD CONSTRAINT "Fk_kp_gebouwdobject_gebruiksdoel_gebouwdobject"
	FOREIGN KEY ("GebouwdobjectID") REFERENCES "Gebouwdobject" ("GebouwdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_kadoz_adraan" ADD CONSTRAINT "Fk_kp_kadoz_adraan_kadoz"
	FOREIGN KEY ("KadozID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_natuurlijkpersoon_socialeG" ADD CONSTRAINT "Fk_kp_natuurlijkpersoon_socialeg_natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nevenadres_adresseerbaarobj" ADD CONSTRAINT "Fk_kp_nevenadres_adresseerbaarobj_adresseerbaarobjectaanduidin"
	FOREIGN KEY ("AdresseerbaarobjectaanduidinID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nevenadres_adresseerbaarobj" ADD CONSTRAINT "Fk_kp_nevenadres_adresseerbaarobj_nevenadres"
	FOREIGN KEY ("NevenadresID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nietnatuurlijkpersoon_natuu" ADD CONSTRAINT "Fk_kp_nietnatuurlijkpersoon_natuu_natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nietnatuurlijkpersoon_natuu" ADD CONSTRAINT "Fk_kp_nietnatuurlijkpersoon_natuu_nietnatuurlijkpersoon"
	FOREIGN KEY ("NietnatuurlijkpersoonID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nummeraanduiding_gebied" ADD CONSTRAINT "Fk_kp_nummeraanduiding_gebied_gebied"
	FOREIGN KEY ("GebiedID") REFERENCES "Gebied" ("GebiedID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_nummeraanduiding_gebied" ADD CONSTRAINT "Fk_kp_nummeraanduiding_gebied_nummeraanduiding"
	FOREIGN KEY ("NummeraanduidingID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_opr_wpl" ADD CONSTRAINT "Fk_kp_opr_wpl_wpl"
	FOREIGN KEY ("WplID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_opr_wpl" ADD CONSTRAINT "Fk_kp_opr_wpl_opr"
	FOREIGN KEY ("OprID") REFERENCES "Openbareruimte" ("OpenbareruimteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_socialeRelatie_natuurlijkp" ADD CONSTRAINT "Fk_kp_socialerelatie_natuurlijkp_natuurlijkpersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vastgoedobject_kadastraalpe" ADD CONSTRAINT "Fk_kp_vastgoedobject_kadastraalpe_kadastraalperceel"
	FOREIGN KEY ("KadastraalperceelID") REFERENCES "Kadastraalperceel" ("KadastraalperceelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verbobj_pand" ADD CONSTRAINT "Fk_kp_verbobj_pand_pand"
	FOREIGN KEY ("PandID") REFERENCES "Pand" ("PandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_verbobj_pand" ADD CONSTRAINT "Fk_kp_verbobj_pand_verbobj"
	FOREIGN KEY ("VerbobjID") REFERENCES "Verblijfsobject" ("VerblijfsobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vestiging_benoemdobject" ADD CONSTRAINT "Fk_kp_vestiging_benoemdobject_benoemdobject"
	FOREIGN KEY ("BenoemdobjectID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vestiging_benoemdobject" ADD CONSTRAINT "Fk_kp_vestiging_benoemdobject_vestiging"
	FOREIGN KEY ("VestigingID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_vstgobj_kadoz" ADD CONSTRAINT "Fk_kp_vstgobj_kadoz_kadoz"
	FOREIGN KEY ("KadozID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_woz_object_kadastraleonroer" ADD CONSTRAINT "Fk_kp_woz_object_kadastraleonroer_kadastraleonroerendezaak"
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_woz_object_kadastraleonroer" ADD CONSTRAINT "Fk_kp_woz_object_kadastraleonroer_woz_object"
	FOREIGN KEY ("Woz_objectID") REFERENCES "Woz_object" ("Woz-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zakelijkrecht_tenaamstellin" ADD CONSTRAINT "Fk_kp_zakelijkrecht_tenaamstellin_tenaamstelling"
	FOREIGN KEY ("TenaamstellingID") REFERENCES "Tenaamstelling" ("TenaamstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zakelijkrecht_tenaamstellin" ADD CONSTRAINT "Fk_kp_zakelijkrecht_tenaamstellin_zakelijkrecht"
	FOREIGN KEY ("ZakelijkrechtID") REFERENCES "Zakelijkrecht" ("ZakelijkrechtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kunstwerkdeel" ADD CONSTRAINT "Fk_kunstwerkdeel_geo_object"
	FOREIGN KEY ("KunstwerkdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kunstwerkdeel" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ligplaats" ADD CONSTRAINT "Fk_ligplaats_benoemdterrein"
	FOREIGN KEY ("LigplaatsID") REFERENCES "Benoemdterrein" ("BenoemdterreinID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ligplaats" ADD CONSTRAINT "Fk_ligplaats_adresseerbaarobjectaanduidin"
	FOREIGN KEY ("LigplaatsID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ligplaats" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Maatschappelijkeactiviteit" ADD CONSTRAINT "fk_isHoofdvestigingVan_vestigi"
	FOREIGN KEY ("VestigingID") REFERENCES "Vestiging" ("VestigingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Maatschappelijkeactiviteit" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nationaliteit" ADD CONSTRAINT fk_heeft_natuurlijkpersoon
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Natuurlijkpersoon" ("NatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT "Fk_natuurlijkpersoon_rechtspersoon"
	FOREIGN KEY ("NatuurlijkpersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT fk_is_betrokkene
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT fk_heeft_gemeentebegrafenis
	FOREIGN KEY ("GemeentebegrafenisID") REFERENCES "Gemeentebegrafenis" ("GemeentebegrafenisID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Natuurlijkpersoon" ADD CONSTRAINT "fk_is_aanwezigeDeelnemer"
	FOREIGN KEY ("AanwezigeDeelnemerID") REFERENCES "AanwezigeDeelnemer" ("AanwezigeDeelnemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nietnatuurlijkpersoon" ADD CONSTRAINT "Fk_nietnatuurlijkpersoon_rechtspersoon"
	FOREIGN KEY ("NietnatuurlijkpersoonID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nietnatuurlijkpersoon" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nietnatuurlijkpersoon" ADD CONSTRAINT fk_is_betrokkene
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "FK_Nummeraanduiding_Openbareruimte"
	FOREIGN KEY ("OpenbareruimteID") REFERENCES "Openbareruimte" ("OpenbareruimteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "FK_Nummeraanduiding_Woonplaats"
	FOREIGN KEY ("WoonplaatsID") REFERENCES "Woonplaats" ("WoonplaatsID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "FK_Nummeraanduiding_Buurt"
	FOREIGN KEY ("BuurtID") REFERENCES "Buurt" ("BuurtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "Fk_nummeraanduiding_object"
	FOREIGN KEY ("NummeraanduidingID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Nummeraanduiding" ADD CONSTRAINT "fk_verwijstNaar_adresaanduidin"
	FOREIGN KEY ("AdresaanduidingID") REFERENCES "Adresaanduiding" ("AdresaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Onbegroeidterreindeel" ADD CONSTRAINT "Fk_onbegroeidterreindeel_geo_object"
	FOREIGN KEY ("OnbegroeidterreindeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "OnbestemdAdres" ADD CONSTRAINT "Fk_onbestemdAdres_object"
	FOREIGN KEY ("OnbestemdAdresID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ondersteunendwaterdeel" ADD CONSTRAINT "Fk_ondersteunendwaterdeel_geo_object"
	FOREIGN KEY ("OndersteunendwaterdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Ondersteunendwegdeel" ADD CONSTRAINT "Fk_ondersteunendwegdeel_geo_object"
	FOREIGN KEY ("OndersteunendwegdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Openbareruimte" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Openbareruimte" ADD CONSTRAINT "fk_betreft_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overbruggingsdeel" ADD CONSTRAINT "Fk_overbruggingsdeel_geo_object"
	FOREIGN KEY ("OverbruggingsdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbenoemdterrein" ADD CONSTRAINT "Fk_overigbenoemdterrein_benoemdterrein"
	FOREIGN KEY ("OverigbenoemdterreinID") REFERENCES "Benoemdterrein" ("BenoemdterreinID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbenoemdterrein" ADD CONSTRAINT "Fk_overigbenoemdterrein_geo_object"
	FOREIGN KEY ("OverigbenoemdterreinID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbenoemdterrein" ADD CONSTRAINT "fk_ligtOp_veld"
	FOREIGN KEY ("VeldID") REFERENCES "Veld" ("VeldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbenoemdterrein" ADD CONSTRAINT "fk_ligtOp_sportpark"
	FOREIGN KEY ("SportparkID") REFERENCES "Sportpark" ("SportparkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbouwwerk" ADD CONSTRAINT "Fk_overigbouwwerk_geo_object"
	FOREIGN KEY ("OverigbouwwerkID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigbouwwerk" ADD CONSTRAINT "fk_heeftAlsEquivalent_overigge"
	FOREIGN KEY ("OveriggebouwdobjectID") REFERENCES "Overiggebouwdobject" ("OveriggebouwdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigeadresseerbaarobjectaand" ADD CONSTRAINT "Fk_overigeadresseerbaarobjectaa_nummeraanduiding"
	FOREIGN KEY ("OverigeadresseerbaarobjectaaID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigeadresseerbaarobjectaand" ADD CONSTRAINT "fk_heeftAlsOfficieelAdres_over"
	FOREIGN KEY ("OverigbenoemdterreinID") REFERENCES "Overigbenoemdterrein" ("OverigbenoemdterreinID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overigescheiding" ADD CONSTRAINT "Fk_overigescheiding_geo_object"
	FOREIGN KEY ("OverigescheidingID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overiggebouwdobject" ADD CONSTRAINT "Fk_overiggebouwdobject_gebouwdobject"
	FOREIGN KEY ("OveriggebouwdobjectID") REFERENCES "Gebouwdobject" ("GebouwdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Overiggebouwdobject" ADD CONSTRAINT "Fk_overiggebouwdobject_adresseerbaarobjectaanduidin"
	FOREIGN KEY ("OveriggebouwdobjectID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pand" ADD CONSTRAINT "FK_Pand_Buurt"
	FOREIGN KEY ("BuurtID") REFERENCES "Buurt" ("BuurtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pand" ADD CONSTRAINT "Fk_pand_geo_object"
	FOREIGN KEY ("PandID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pand" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Pand" ADD CONSTRAINT "fk_betreft_beschermdeStatus"
	FOREIGN KEY ("BeschermdeStatusID") REFERENCES "BeschermdeStatus" ("BeschermdeStatusID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rechtspersoon" ADD CONSTRAINT "fk_heeftAlsEigenaar_maatschapp"
	FOREIGN KEY ("MaatschappelijkeactiviteitID") REFERENCES "Maatschappelijkeactiviteit" ("MaatschappelijkeactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Rechtspersoon" ADD CONSTRAINT fk_is_indiener
	FOREIGN KEY ("IndienerID") REFERENCES "Indiener" ("IndienerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Reisdocument" ADD CONSTRAINT "fk_isVerstrektAan_ingeschreven"
	FOREIGN KEY ("IngeschrevenpersoonID") REFERENCES "Ingeschrevenpersoon" ("IngeschrevenpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Scheiding" ADD CONSTRAINT "Fk_scheiding_geo_object"
	FOREIGN KEY ("ScheidingID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Spoor" ADD CONSTRAINT "Fk_spoor_geo_object"
	FOREIGN KEY ("SpoorID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Standplaats" ADD CONSTRAINT "Fk_standplaats_benoemdterrein"
	FOREIGN KEY ("StandplaatsID") REFERENCES "Benoemdterrein" ("BenoemdterreinID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Standplaats" ADD CONSTRAINT "Fk_standplaats_adresseerbaarobjectaanduidin"
	FOREIGN KEY ("StandplaatsID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Standplaats" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tenaamstelling" ADD CONSTRAINT fk_heeft_rechtsp
	FOREIGN KEY ("RechtspID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tenaamstelling" ADD CONSTRAINT "FK_Tenaamstelling_Zakelijkrecht"
	FOREIGN KEY ("ZakelijkrechtID") REFERENCES "Zakelijkrecht" ("ZakelijkrechtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Tunneldeel" ADD CONSTRAINT "Fk_tunneldeel_geo_object"
	FOREIGN KEY ("TunneldeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vegetatieobject" ADD CONSTRAINT "Fk_vegetatieobject_geo_object"
	FOREIGN KEY ("VegetatieobjectID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfsobject" ADD CONSTRAINT "Fk_verblijfsobject_gebouwdobject"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Gebouwdobject" ("GebouwdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Verblijfsobject" ADD CONSTRAINT "Fk_verblijfsobject_adresseerbaarobjectaanduidin"
	FOREIGN KEY ("VerblijfsobjectID") REFERENCES "Adresseerbaarobjectaanduiding" ("AdresseerbaarobjectaanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vestiging" ADD CONSTRAINT "FK_Vestiging_Nummeraanduiding"
	FOREIGN KEY ("NummeraanduidingID") REFERENCES "Nummeraanduiding" ("NummeraanduidingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vestiging" ADD CONSTRAINT "FK_Vestiging_Benoemdobject"
	FOREIGN KEY ("BenoemdobjectID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vestiging" ADD CONSTRAINT "FK_Vestiging_Maatschappelijkeactiviteit"
	FOREIGN KEY ("MaatschappelijkeactiviteitID") REFERENCES "Maatschappelijkeactiviteit" ("MaatschappelijkeactiviteitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vestiging" ADD CONSTRAINT fk_heeft_nietnatuurlijkpersoon
	FOREIGN KEY ("NietnatuurlijkpersoonID") REFERENCES "Nietnatuurlijkpersoon" ("NietnatuurlijkpersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waterdeel" ADD CONSTRAINT "Fk_waterdeel_geo_object"
	FOREIGN KEY ("WaterdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Waterdeel" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Wegdeel" ADD CONSTRAINT "Fk_wegdeel_geo_object"
	FOREIGN KEY ("WegdeelID") REFERENCES "Geo_object" ("Geo-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Wijk" ADD CONSTRAINT "FK_Wijk_Gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woonplaats" ADD CONSTRAINT "FK_Woonplaats_Gemeente"
	FOREIGN KEY ("GemeenteID") REFERENCES "Gemeente" ("GemeenteID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woz_deelobject" ADD CONSTRAINT "FK_Woz_deelobject_Benoemdobject"
	FOREIGN KEY ("BenoemdobjectID") REFERENCES "Benoemdobject" ("BenoemdobjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woz_deelobject" ADD CONSTRAINT "FK_Woz_deelobject_Pand"
	FOREIGN KEY ("PandID") REFERENCES "Pand" ("PandID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woz_deelobject" ADD CONSTRAINT "FK_Woz_deelobject_Woz_object"
	FOREIGN KEY ("Woz_objectID") REFERENCES "Woz_object" ("Woz-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Woz_waarde" ADD CONSTRAINT "FK_Woz_waarde_Woz_object"
	FOREIGN KEY ("Woz_objectID") REFERENCES "Woz_object" ("Woz-objectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zakelijkrecht" ADD CONSTRAINT "FK_Zakelijkrecht_Kadastraleonroerendezaak"
	FOREIGN KEY ("KadozID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zakelijkrecht" ADD CONSTRAINT "fk_isBelastMet_zakelijkrecht"
	FOREIGN KEY ("ZakelijkrechtID") REFERENCES "Zakelijkrecht" ("ZakelijkrechtID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zakelijkrecht" ADD CONSTRAINT "fk_heeftBetrekkingOp_kadastral"
	FOREIGN KEY ("KadastralemutatieID") REFERENCES "Kadastralemutatie" ("KadastralemutatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zekerheidsrecht" ADD CONSTRAINT "FK_Zekerheidsrecht_Kadastraleonroerendezaak"
	FOREIGN KEY ("KadastraleonroerendezaakID") REFERENCES "Kadastraleonroerendezaak" ("KadastraleonroerendezaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zekerheidsrecht" ADD CONSTRAINT "FK_Zekerheidsrecht_Tenaamstelling"
	FOREIGN KEY ("TenaamstellingID") REFERENCES "Tenaamstelling" ("TenaamstellingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enum_geslachtsaanduidingMedew" ADD CONSTRAINT "PK_Enum_geslachtsaanduidingMedew"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_soortenKlantcontact" ADD CONSTRAINT "PK_Enum_soortenKlantcontact"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vertrouwelijkAanduiding" ADD CONSTRAINT "PK_Enum_vertrouwelijkAanduiding"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_vervalredenBesluit" ADD CONSTRAINT "PK_Enum_vervalredenBesluit"
	PRIMARY KEY ("ID");

ALTER TABLE "Brondocumenten" ADD CONSTRAINT "PK_Brondocumenten"
	PRIMARY KEY ("BrondocumentenID");

ALTER TABLE "Formelehistorie" ADD CONSTRAINT "PK_Formelehistorie"
	PRIMARY KEY ("FormelehistorieID");

ALTER TABLE "Inonderzoek" ADD CONSTRAINT "PK_Inonderzoek"
	PRIMARY KEY ("InonderzoekID");

ALTER TABLE "Materielehistorie" ADD CONSTRAINT "PK_Materielehistorie"
	PRIMARY KEY ("MaterielehistorieID");

ALTER TABLE "Strijdigheidofnietigheid" ADD CONSTRAINT "PK_Strijdigheidofnietigheid"
	PRIMARY KEY ("StrijdigheidofnietigheidID");

ALTER TABLE "Bedrijfsproces" ADD CONSTRAINT "PK_Bedrijfsproces"
	PRIMARY KEY ("BedrijfsprocesID");

ALTER TABLE "Bedrijfsprocestype" ADD CONSTRAINT "PK_Bedrijfsprocestype"
	PRIMARY KEY ("BedrijfsprocestypeID");

ALTER TABLE "Besluit" ADD CONSTRAINT "PK_Besluit"
	PRIMARY KEY ("BesluitID");

ALTER TABLE "Besluittype" ADD CONSTRAINT "PK_Besluittype"
	PRIMARY KEY ("BesluittypeID");

ALTER TABLE "Betaling" ADD CONSTRAINT "PK_Betaling"
	PRIMARY KEY ("BetalingID");

ALTER TABLE "Betrokkene" ADD CONSTRAINT "PK_Betrokkene"
	PRIMARY KEY ("BetrokkeneID");

ALTER TABLE "Deelproces" ADD CONSTRAINT "PK_Deelproces"
	PRIMARY KEY ("DeelprocesID");

ALTER TABLE "Deelprocestype" ADD CONSTRAINT "PK_Deelprocestype"
	PRIMARY KEY ("DeelprocestypeID");

ALTER TABLE "Document" ADD CONSTRAINT "PK_Document"
	PRIMARY KEY ("DocumentID");

ALTER TABLE "Documenttype" ADD CONSTRAINT "PK_Documenttype"
	PRIMARY KEY ("DocumenttypeID");

ALTER TABLE "Enkelvoudigdocument" ADD CONSTRAINT "PK_Enkelvoudigdocument"
	PRIMARY KEY ("EnkelvoudigdocumentID");

ALTER TABLE "Heffing" ADD CONSTRAINT "PK_Heffing"
	PRIMARY KEY ("HeffingID");

ALTER TABLE "Identificatiekenmerk" ADD CONSTRAINT "PK_Identificatiekenmerk"
	PRIMARY KEY ("IdentificatiekenmerkID");

ALTER TABLE "Klantcontact" ADD CONSTRAINT "PK_Klantcontact"
	PRIMARY KEY ("KlantcontactID");

ALTER TABLE "Medewerker" ADD CONSTRAINT "PK_Medewerker"
	PRIMARY KEY ("MedewerkerID");

ALTER TABLE "Object" ADD CONSTRAINT "PK_Object"
	PRIMARY KEY ("ObjectID");

ALTER TABLE "Offerte" ADD CONSTRAINT "PK_Offerte"
	PRIMARY KEY ("OfferteID");

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT "PK_Organisatorischeeenheid"
	PRIMARY KEY ("OrganisatorischeeenheidID");

ALTER TABLE "Samengestelddocument" ADD CONSTRAINT "PK_Samengestelddocument"
	PRIMARY KEY ("SamengestelddocumentID");

ALTER TABLE "Status" ADD CONSTRAINT "PK_Status"
	PRIMARY KEY ("StatusID");

ALTER TABLE "Statustype" ADD CONSTRAINT "PK_Statustype"
	PRIMARY KEY ("StatustypeID");

ALTER TABLE "Vestigingvanzaakbehandelendeor" ADD CONSTRAINT "PK_Vestigingvanzaakbehandelendeor"
	PRIMARY KEY ("VestigingvanzaakbehandelendeorganisatieID");

ALTER TABLE "Zaak" ADD CONSTRAINT "PK_Zaak"
	PRIMARY KEY ("ZaakID");

ALTER TABLE "Zaak_Origineel" ADD CONSTRAINT "PK_Zaak_Origineel"
	PRIMARY KEY ("Zaak-OrigineelID");

ALTER TABLE "Zaaktype" ADD CONSTRAINT "PK_Zaaktype"
	PRIMARY KEY ("ZaaktypeID");

ALTER TABLE "Bedrijfsprocestype" ADD CONSTRAINT "fk_isOnderdeelVan_onderdeelvan"
	FOREIGN KEY ("OnderdeelvanID") REFERENCES "Bedrijfsprocestype" ("BedrijfsprocestypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Bedrijfsprocestype" ADD CONSTRAINT "fk_isDeelVan_deelprocestype"
	FOREIGN KEY ("DeelprocestypeID") REFERENCES "Deelprocestype" ("DeelprocestypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Besluit" ADD CONSTRAINT "FK_Besluit_Besluittype"
	FOREIGN KEY (type) REFERENCES "Besluittype" ("BesluittypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Besluit" ADD CONSTRAINT "FK_Besluit_Zaak"
	FOREIGN KEY (zaak) REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Besluit" ADD CONSTRAINT fk_is_object
	FOREIGN KEY ("ObjectID") REFERENCES "Object" ("ObjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Betaling" ADD CONSTRAINT "FK_Betaling_Bankafschriftregel"
	FOREIGN KEY ("BankafschriftregelID") REFERENCES "Bankafschriftregel" ("BankafschriftregelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Betaling" ADD CONSTRAINT "fk_heeftBetaling_zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Betaling" ADD CONSTRAINT fk_van_bankrekening
	FOREIGN KEY ("BankrekeningID") REFERENCES "Bankrekening" ("BankrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Betaling" ADD CONSTRAINT fk_naar_bankrekening
	FOREIGN KEY ("BankrekeningID") REFERENCES "Bankrekening" ("BankrekeningID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Betrokkene" ADD CONSTRAINT "Fk_betrokkene_rechtspersoon"
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Rechtspersoon" ("RechtspersoonID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Deelproces" ADD CONSTRAINT "FK_Deelproces_Bedrijfsproces"
	FOREIGN KEY ("BedrijfsprocesID") REFERENCES "Bedrijfsproces" ("BedrijfsprocesID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Deelprocestype" ADD CONSTRAINT "fk_isVan_deelproces"
	FOREIGN KEY ("DeelprocesID") REFERENCES "Deelproces" ("DeelprocesID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT "fk_isVastgelegdIn_besluit"
	FOREIGN KEY ("BesluitID") REFERENCES "Besluit" ("BesluitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT "FK_Document_Identificatiekenmerk"
	FOREIGN KEY ("IdentificatiekenmerkID") REFERENCES "Identificatiekenmerk" ("IdentificatiekenmerkID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT "FK_Document_Documenttype"
	FOREIGN KEY (type) REFERENCES "Documenttype" ("DocumenttypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT "fk_heeftDocumenten_aanvraagofm"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT fk_heeft_rapportagemoment
	FOREIGN KEY ("RapportagemomentID") REFERENCES "Rapportagemoment" ("RapportagemomentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Document" ADD CONSTRAINT "fk_isVastgelegdIn_verkeersbesl"
	FOREIGN KEY ("VerkeersbesluitID") REFERENCES "Verkeersbesluit" ("VerkeersbesluitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enkelvoudigdocument" ADD CONSTRAINT "Fk_enkelvoudigdocument_document"
	FOREIGN KEY ("EnkelvoudigdocumentID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Enkelvoudigdocument" ADD CONSTRAINT fk_omvat_samengestelddocument
	FOREIGN KEY ("SamengestelddocumentID") REFERENCES "Samengestelddocument" ("SamengestelddocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffing" ADD CONSTRAINT "FK_Heffing_Enum_heffingsoort"
	FOREIGN KEY ("HeffingsoortID") REFERENCES "Enum_heffingsoort" ("ID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffing" ADD CONSTRAINT "FK_Heffing_Heffinggrondslag"
	FOREIGN KEY ("HeffinggrondslagID") REFERENCES "Heffinggrondslag" ("HeffinggrondslagID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Heffing" ADD CONSTRAINT fk_heeft_zaak
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "FK_Klantcontact_Betrokkene"
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "FK_Klantcontact_Medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "FK_Klantcontact_Zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "FK_Klantcontact_Vestigingvanzaakbehandelendeor"
	FOREIGN KEY ("VestigingvanzaakbehandelendeID") REFERENCES "Vestigingvanzaakbehandelendeor" ("VestigingvanzaakbehandelendeorganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "fk_mondtUitIn_telefoontje"
	FOREIGN KEY ("TelefoontjeID") REFERENCES "Telefoontje" ("TelefoontjeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT fk_heeft_telefoononderwerp
	FOREIGN KEY ("TelefoononderwerpID") REFERENCES "Telefoononderwerp" ("TelefoononderwerpID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Klantcontact" ADD CONSTRAINT "fk_mondtUitIn_balieafspraak"
	FOREIGN KEY ("BalieafspraakID") REFERENCES "Balieafspraak" ("BalieafspraakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bedrijfsproces_bedrijfsproc" ADD CONSTRAINT "Fk_kp_bedrijfsproces_bedrijfsproc_bedrijfsprocestype"
	FOREIGN KEY ("BedrijfsprocestypeID") REFERENCES "Bedrijfsprocestype" ("BedrijfsprocestypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bedrijfsproces_bedrijfsproc" ADD CONSTRAINT "Fk_kp_bedrijfsproces_bedrijfsproc_bedrijfsproces"
	FOREIGN KEY ("BedrijfsprocesID") REFERENCES "Bedrijfsproces" ("BedrijfsprocesID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bedrijfsproces_zaak" ADD CONSTRAINT "Fk_kp_bedrijfsproces_zaak_zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_bedrijfsproces_zaak" ADD CONSTRAINT "Fk_kp_bedrijfsproces_zaak_bedrijfsproces"
	FOREIGN KEY ("BedrijfsprocesID") REFERENCES "Bedrijfsproces" ("BedrijfsprocesID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_besluit_document" ADD CONSTRAINT "Fk_kp_besluit_document_document"
	FOREIGN KEY (document) REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_besluit_document" ADD CONSTRAINT "Fk_kp_besluit_document_besluit"
	FOREIGN KEY ("BesluitID") REFERENCES "Besluit" ("BesluitID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_medewerker_organisatorische" ADD CONSTRAINT "Fk_kp_medewerker_organisatorische_organisatorischeEenheid"
	FOREIGN KEY ("organisatorische eenheid") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_medewerker_organisatorische" ADD CONSTRAINT "Fk_kp_medewerker_organisatorische_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zaak_medewerker" ADD CONSTRAINT "Fk_kp_zaak_medewerker_medewerker"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_zaak_medewerker" ADD CONSTRAINT "Fk_kp_zaak_medewerker_zaak"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Medewerker" ADD CONSTRAINT fk_is_betrokkene
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Medewerker" ADD CONSTRAINT "FK_Medewerker_Leverancier"
	FOREIGN KEY ("LeverancierID") REFERENCES "Leverancier" ("LeverancierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Medewerker" ADD CONSTRAINT "FK_Medewerker_UitvoerendeInstantie"
	FOREIGN KEY ("UitvoerendeInstantieID") REFERENCES "UitvoerendeInstantie" ("UitvoerendeInstantieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT fk_is_betrokkene
	FOREIGN KEY ("BetrokkeneID") REFERENCES "Betrokkene" ("BetrokkeneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT "fk_isContactpersoonVoor_medewe"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT "fk_isVerantwoordelijkVoor_mede"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT "FK_Organisatorischeeenheid_Vestigingvanzaakbehandelendeor"
	FOREIGN KEY (vestiging) REFERENCES "Vestigingvanzaakbehandelendeor" ("VestigingvanzaakbehandelendeorganisatieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Organisatorischeeenheid" ADD CONSTRAINT "fk_isDeelVan_onderdeelvan"
	FOREIGN KEY ("OnderdeelvanID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Samengestelddocument" ADD CONSTRAINT "Fk_samengestelddocument_document"
	FOREIGN KEY ("SamengestelddocumentID") REFERENCES "Document" ("DocumentID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Status" ADD CONSTRAINT "FK_Status_Statustype"
	FOREIGN KEY (type) REFERENCES "Statustype" ("StatustypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Status" ADD CONSTRAINT fk_heeft_zaak
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Statustype" ADD CONSTRAINT fk_heeft_zaaktype
	FOREIGN KEY ("ZaaktypeID") REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "fk_heeftBetrekkingOpAndere_zaa"
	FOREIGN KEY ("ZaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "FK_Zaak_Zaaktype"
	FOREIGN KEY (type) REFERENCES "Zaaktype" ("ZaaktypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "fk_isDeelzaakVan_hoofdzaak"
	FOREIGN KEY ("HoofdzaakID") REFERENCES "Zaak" ("ZaakID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "FK_Zaak_Project"
	FOREIGN KEY ("ProjectID") REFERENCES "Project" ("ProjectID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "fk_kanLeidenTot_aanvraagofmeld"
	FOREIGN KEY ("AanvraagofmeldingID") REFERENCES "Aanvraagofmelding" ("AanvraagofmeldingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "fk_afhandeling_aanvraagInkoopo"
	FOREIGN KEY ("AanvraagInkooporderID") REFERENCES "AanvraagInkooporder" ("AanvraagInkooporderID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT fk_betreft_aanbesteding
	FOREIGN KEY ("AanbestedingID") REFERENCES "Aanbesteding" ("AanbestedingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT fk_heeft_subsidie
	FOREIGN KEY ("SubsidieID") REFERENCES "Subsidie" ("SubsidieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak" ADD CONSTRAINT "fk_leidtTot_verzoek"
	FOREIGN KEY ("VerzoekID") REFERENCES "Verzoek" ("VerzoekID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak_Origineel" ADD CONSTRAINT "fk_heeftBetrekkingOpAndere_zaa"
	FOREIGN KEY ("Zaak_OrigineelID") REFERENCES "Zaak_Origineel" ("Zaak-OrigineelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaak_Origineel" ADD CONSTRAINT "fk_isDeelzaakVan_zaak_Originee"
	FOREIGN KEY ("Zaak_OrigineelID") REFERENCES "Zaak_Origineel" ("Zaak-OrigineelID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaaktype" ADD CONSTRAINT fk_heeft_bedrijfsprocestype
	FOREIGN KEY ("BedrijfsprocestypeID") REFERENCES "Bedrijfsprocestype" ("BedrijfsprocestypeID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaaktype" ADD CONSTRAINT "fk_isVerantwoordelijkeVoor_med"
	FOREIGN KEY ("MedewerkerID") REFERENCES "Medewerker" ("MedewerkerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaaktype" ADD CONSTRAINT "fk_isVerantwoordelijkeVoor_org"
	FOREIGN KEY ("OrganisatorischeeenheidID") REFERENCES "Organisatorischeeenheid" ("OrganisatorischeeenheidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Zaaktype" ADD CONSTRAINT fk_betreft_product
	FOREIGN KEY ("ProductID") REFERENCES "Product" ("ProductID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanwezigeDeelnemer" ADD CONSTRAINT "PK_AanwezigeDeelnemer"
	PRIMARY KEY ("AanwezigeDeelnemerID");

ALTER TABLE "Agendapunt" ADD CONSTRAINT "PK_Agendapunt"
	PRIMARY KEY ("AgendapuntID");

ALTER TABLE "Categorie" ADD CONSTRAINT "PK_Categorie"
	PRIMARY KEY ("CategorieID");

ALTER TABLE "Collegelid" ADD CONSTRAINT "PK_Collegelid"
	PRIMARY KEY ("CollegelidID");

ALTER TABLE "Dossier" ADD CONSTRAINT "PK_Dossier"
	PRIMARY KEY ("DossierID");

ALTER TABLE "Enum_deelnemersrol" ADD CONSTRAINT "PK_Enum_deelnemersrol"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_stemmingsresultaattype" ADD CONSTRAINT "PK_Enum_stemmingsresultaattype"
	PRIMARY KEY ("ID");

ALTER TABLE "Enum_stemmingstype" ADD CONSTRAINT "PK_Enum_stemmingstype"
	PRIMARY KEY ("ID");

ALTER TABLE "Indiener" ADD CONSTRAINT "PK_Indiener"
	PRIMARY KEY ("IndienerID");

ALTER TABLE "Programma" ADD CONSTRAINT "PK_Programma"
	PRIMARY KEY ("ProgrammaID");

ALTER TABLE "Raadscommissie" ADD CONSTRAINT "PK_Raadscommissie"
	PRIMARY KEY ("RaadscommissieID");

ALTER TABLE "Raadslid" ADD CONSTRAINT "PK_Raadslid"
	PRIMARY KEY ("RaadslidID");

ALTER TABLE "Raadsstuk" ADD CONSTRAINT "PK_Raadsstuk"
	PRIMARY KEY ("RaadsstukID");

ALTER TABLE "Stemming" ADD CONSTRAINT "PK_Stemming"
	PRIMARY KEY ("StemmingID");

ALTER TABLE "Taakveld" ADD CONSTRAINT "PK_Taakveld"
	PRIMARY KEY ("TaakveldID");

ALTER TABLE "Vergadering" ADD CONSTRAINT "PK_Vergadering"
	PRIMARY KEY ("VergaderingID");

ALTER TABLE "AanwezigeDeelnemer" ADD CONSTRAINT fk_is_raadslid
	FOREIGN KEY ("RaadslidID") REFERENCES "Raadslid" ("RaadslidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "AanwezigeDeelnemer" ADD CONSTRAINT "fk_vergadering_aanwezigeDeelne"
	FOREIGN KEY ("VergaderingID") REFERENCES "Vergadering" ("VergaderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Agendapunt" ADD CONSTRAINT fk_heeft_vergadering
	FOREIGN KEY ("VergaderingID") REFERENCES "Vergadering" ("VergaderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Agendapunt" ADD CONSTRAINT fk_betreft_video_opname
	FOREIGN KEY ("Video_opnameID") REFERENCES "Video_opname" ("Video-opnameID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Collegelid" ADD CONSTRAINT "fk_is_aanwezigeDeelnemer"
	FOREIGN KEY ("AanwezigeDeelnemerID") REFERENCES "AanwezigeDeelnemer" ("AanwezigeDeelnemerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Collegelid" ADD CONSTRAINT fk_is_indiener
	FOREIGN KEY ("IndienerID") REFERENCES "Indiener" ("IndienerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Collegelid" ADD CONSTRAINT "Fk_collegelid_ingezetene"
	FOREIGN KEY ("CollegelidID") REFERENCES "Ingezetene" ("IngezeteneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dossier_raadsstuk" ADD CONSTRAINT "Fk_kp_dossier_raadsstuk_raadsstuk"
	FOREIGN KEY ("RaadsstukID") REFERENCES "Raadsstuk" ("RaadsstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_dossier_raadsstuk" ADD CONSTRAINT "Fk_kp_dossier_raadsstuk_dossier"
	FOREIGN KEY ("DossierID") REFERENCES "Dossier" ("DossierID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_indiener_raadsstuk" ADD CONSTRAINT "Fk_kp_indiener_raadsstuk_raadsstuk"
	FOREIGN KEY ("RaadsstukID") REFERENCES "Raadsstuk" ("RaadsstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_indiener_raadsstuk" ADD CONSTRAINT "Fk_kp_indiener_raadsstuk_indiener"
	FOREIGN KEY ("IndienerID") REFERENCES "Indiener" ("IndienerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadslid_raadscommissie" ADD CONSTRAINT "Fk_kp_raadslid_raadscommissie_raadscommissie"
	FOREIGN KEY ("RaadscommissieID") REFERENCES "Raadscommissie" ("RaadscommissieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadslid_raadscommissie" ADD CONSTRAINT "Fk_kp_raadslid_raadscommissie_raadslid"
	FOREIGN KEY ("RaadslidID") REFERENCES "Raadslid" ("RaadslidID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_agendapunt" ADD CONSTRAINT "Fk_kp_raadsstuk_agendapunt_agendapunt"
	FOREIGN KEY ("AgendapuntID") REFERENCES "Agendapunt" ("AgendapuntID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_agendapunt" ADD CONSTRAINT "Fk_kp_raadsstuk_agendapunt_raadsstuk"
	FOREIGN KEY ("RaadsstukID") REFERENCES "Raadsstuk" ("RaadsstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_programma" ADD CONSTRAINT "Fk_kp_raadsstuk_programma_programma"
	FOREIGN KEY ("ProgrammaID") REFERENCES "Programma" ("ProgrammaID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_programma" ADD CONSTRAINT "Fk_kp_raadsstuk_programma_raadsstuk"
	FOREIGN KEY ("RaadsstukID") REFERENCES "Raadsstuk" ("RaadsstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_vergadering" ADD CONSTRAINT "Fk_kp_raadsstuk_vergadering_vergadering"
	FOREIGN KEY ("VergaderingID") REFERENCES "Vergadering" ("VergaderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Kp_raadsstuk_vergadering" ADD CONSTRAINT "Fk_kp_raadsstuk_vergadering_raadsstuk"
	FOREIGN KEY ("RaadsstukID") REFERENCES "Raadsstuk" ("RaadsstukID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadslid" ADD CONSTRAINT fk_is_indiener
	FOREIGN KEY ("IndienerID") REFERENCES "Indiener" ("IndienerID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadslid" ADD CONSTRAINT "Fk_raadslid_ingezetene"
	FOREIGN KEY ("RaadslidID") REFERENCES "Ingezetene" ("IngezeteneID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadsstuk" ADD CONSTRAINT fk_heeft_categorie
	FOREIGN KEY ("CategorieID") REFERENCES "Categorie" ("CategorieID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadsstuk" ADD CONSTRAINT "FK_Raadsstuk_Taakveld"
	FOREIGN KEY ("TaakveldID") REFERENCES "Taakveld" ("TaakveldID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadsstuk" ADD CONSTRAINT fk_betreft_stemming
	FOREIGN KEY ("StemmingID") REFERENCES "Stemming" ("StemmingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Raadsstuk" ADD CONSTRAINT "fk_heeftVerslag_vergadering"
	FOREIGN KEY ("VergaderingID") REFERENCES "Vergadering" ("VergaderingID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Stemming" ADD CONSTRAINT "FK_Stemming_Agendapunt"
	FOREIGN KEY ("AgendapuntID") REFERENCES "Agendapunt" ("AgendapuntID") ON DELETE No Action ON UPDATE No Action;

ALTER TABLE "Vergadering" ADD CONSTRAINT fk_heeft_raadscommissie
	FOREIGN KEY ("RaadscommissieID") REFERENCES "Raadscommissie" ("RaadscommissieID") ON DELETE No Action ON UPDATE No Action;