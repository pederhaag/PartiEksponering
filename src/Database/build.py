# https://www.nb.no/sbfil/leksikalske_databaser/ordbank/20190123_norsk_ordbank_nob_2005.tar.gz
import sqlite3 as sl
import pathlib
import pandas as pd

db_file = str(pathlib.Path().absolute()) + "\src\Database\\" + "WordBank.db"
source_folder = str(pathlib.Path().absolute()) + "\src\Database\\" + "sources\\" \
    + "20190123_Norsk_ordbank_nob_2005\\"
con = sl.connect(db_file)


encoding = 'latin-1'

df_boying = pd.read_csv(source_folder + "boying.txt", sep="\t", encoding=encoding)
df_boying.to_sql('BOYING', con, if_exists = 'replace')

df_boyinggr = pd.read_csv(source_folder + "boying_grupper.txt", sep="\t", encoding=encoding)
df_boyinggr.to_sql('BOYING_GRUPPER', con, if_exists = 'replace')

df_leddanalyse = pd.read_csv(source_folder + "leddanalyse.txt", sep="\t", encoding=encoding)
df_leddanalyse.to_sql('LEDDANALYSE', con, if_exists = 'replace')

df_lemmapara = pd.read_csv(source_folder + "lemma_paradigme.txt", sep="\t", encoding=encoding)
df_lemmapara.to_sql('LEMMAPARADIGME', con, if_exists = 'replace')

df_paradigme = pd.read_csv(source_folder + "paradigme.txt", sep="\t", encoding=encoding)
df_paradigme.to_sql('PARADIGME', con, if_exists = 'replace')

df_paradigmeboy = pd.read_csv(source_folder + "paradigme_boying.txt", sep="\t", encoding=encoding)
df_paradigmeboy.to_sql('PARADIGMEBOYING', con, if_exists = 'replace')

df_lemma = pd.read_csv(source_folder + "lemma.txt", sep="\t", encoding=encoding)
df_lemma.to_sql('LEMMA', con, if_exists = 'replace')


fullform_dtypes = {
    "LOEPENR" : int,
    "LEMMA_ID" : int,
    "OPPSLAG" : "string",
    "TAG" : "string",
    "PARADIGME_ID" : "string",
    "BOY_NUMMER" : int,
    "FRADATO" : "string",
    "TILDATO" : "string",
    "NORMERING" : "string",
}
df_fullform = pd.read_csv(source_folder + "fullformsliste.txt", sep="\t",
    dtype=fullform_dtypes, encoding=encoding)
df_fullform.to_sql('FULLFORM', con, if_exists = 'replace')
