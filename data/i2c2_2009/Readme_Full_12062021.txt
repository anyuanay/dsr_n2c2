December 06, 2021

README: RxNorm 12/06/2021 Full Update Release
===================================================

-----------------------------------------------------------------
This Full release contains data that is consistent with the
2020AA version of the UMLS.
-----------------------------------------------------------------
This release contains updates to the following sources:

ATC -  ATC_2021 (Anatomical Therapeutic Chemical Classification System)
GS -  11/04/2021 (Gold Standard Alchemy)
CVX -  11/19/2021 (Vaccines Administered,  2021_11_19)
MMSL -  11/01/2021 (Multum MediSource Lexicon)
MMX -  11/01/2021 (Micromedex DRUGDEX)
MTHSPL -  11/26/2021 (FDA Structured Product Labels)
NDDF -  11/03/2021 (First Databank FDB MedKnowledge (formerly NDDF Plus))
#NDFRT -  (National Drug File - Reference Terminology)
VANDF -  10/31/2021 (Veterans Health Administration National Drug File)
DRUGBANK -  11/01/2021 (DrugBank,  5.0_2021_11_01)
USP -  07/15/2021 (USP Compendial Nomenclature)

For full details, please refer to the RxNorm documentation at
https://www.nlm.nih.gov/research/umls/rxnorm/docs/index.html.

This release contains database control files and SQL
commands for use in the automation of the loading process of
these files into an Oracle RDBMS.In addition, scripts are now
provided for loading the RxNorm files into a MySQL database.

RxNorm release data files are available by download from
the NLM download server at:

        https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html

This link will take you to a page for downloading the latest files:
RxNorm_full_12062021.zip
Once downloaded, it must be unzipped in order to access the files.

HARDWARE AND SOFTWARE RECOMMENDATIONS
-------------------------------------
- Supported operating systems:
        Windows: 7
        Linux
        Solaris: Solaris 10

- Hardware Requirements

  - A MINIMUM 1.96 GB of free hard disk space (To accomodate ZIP files and
        unzipped contents).

CONTENTS OF THE ZIP FILE
-------------------------

The ZIP formatted file is 250,305,021 bytes and contains the
following 44 files and 9 directories:

Readme_Full_12062021.txt            5477                 bytes

rrf directory:

RXNATOMARCHIVE.RRF                  74,132,401           bytes
RXNCONSO.RRF                        122,653,318          bytes
RXNCUICHANGES.RRF                   16,921               bytes
RXNCUI.RRF                          1,717,864            bytes
RXNDOC.RRF                          218,706              bytes
RXNREL.RRF                          511,382,783          bytes
RXNSAB.RRF                          10,705               bytes
RXNSAT.RRF                          522,275,932          bytes
RXNSTY.RRF                          18,170,556           bytes


scripts directory:

        oracle sub-directory:

populate_oracle_rxn_db.bat          1,164                bytes
RXNATOMARCHIVE.ctl                  564                  bytes
RXNCONSO.ctl                        512                  bytes
RXNCUICHANGES.ctl                   346                  bytes
RXNCUI.ctl                          296                  bytes
RXNDOC.ctl                          248                  bytes
rxn_index.sql                       660                  bytes
RxNormDDL.sql                       3,291                bytes
RXNREL.ctl                          471                  bytes
RXNSAB.ctl                          674                  bytes
RXNSAT.ctl                          378                  bytes
RXNSTY.ctl                          267                  bytes

         mysql sub-directory:

Indexes_mysql_rxn.sql               662                  bytes
Load_scripts_mysql_rxn_unix.sql     3,961                bytes
Load_scripts_mysql_rxn_win.sql      3,959                bytes
Populate_mysql_rxn.bat              775                  bytes
populate_mysql_rxn.sh               1,609                bytes
Table_scripts_mysql_rxn.sql         4,205                bytes

prescribe directory:

Readme_Full_Prescribe_12062021.txt  3075                 bytes

      rrf sub-directory:

RXNCONSO.RRF                        29,496,874           bytes
RXNREL.RRF                          198,015,381          bytes
RXNSAT.RRF                          267,490,880          bytes


      scripts sub-directory:

         oracle sub-directory:

populate_oracle_rxn_db.bat          699                  bytes
RXNCONSO.ctl                        512                  bytes
rxn_index.sql                       460                  bytes
RxNormDDL.sql                       1,373                bytes
RXNREL.ctl                          471                  bytes
RXNSAT.ctl                          378                  bytes

         mysql sub-directory:

Indexes_mysql_rxn.sql               463                  bytes
Load_scripts_mysql_rxn_unix.sql     1,469                bytes
Load_scripts_mysql_rxn_win.sql      1,468                bytes
Populate_mysql_rxn.bat              777                  bytes
populate_mysql_rxn.sh               1,609                bytes
Table_scripts_mysql_rxn.sql         1,749                bytes
Additional NOTES:

-----------------

- Most RxNorm users will need applications and data management
  systems such as an RDBMS for storage and retrieval.

- The RxNorm release files contain UTF-8 Unicode encoded data.

- Refer to the RxNorm release documentation at
  https://www.nlm.nih.gov/research/umls/rxnorm/docs/index.html
