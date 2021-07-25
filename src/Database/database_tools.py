# https://www.nb.no/sbfil/leksikalske_databaser/ordbank/20190123_norsk_ordbank_nob_2005.tar.gz
from logging import error
import pathlib
import sqlite3 as sl
import pandas as pd

def get_db(filename = "database.db"):
    db_file = str(pathlib.Path().absolute()) + "\src\Database\\" + filename
    return sl.connect(db_file)

def get_source_folder():
    return str(pathlib.Path().absolute()) + "\src\Database\\" + "sources\\"

def import_politicians():
    source_file = get_source_folder() + "valglisterogkandidaterstortingsvalget2021.csv"
    cols_to_use = ["partikode", "partinavn", "kandidatnr", "navn"]
    df = pd.read_csv(source_file, usecols=cols_to_use)

    con = get_db()

    # Only consider some parties
    #   to reduce number of operations
    #   when classifying
    parties_to_consider = [
        "A",
        "FNB",
        "FRP",
        "H",
        "KRF",
        "MDG",
        "RØDT",
        "SP",
        "SV",
        "V",
    ]
    df = df[df["partikode"].isin(parties_to_consider)]

    df.to_sql("POLITICIANS", con, if_exists = 'replace')

    return df

    


def store_article_data(art, refresh = False):
    art_data = art.text
    datacolumns = art_data.columns.tolist()
    if len(datacolumns) != 2 or "WORD" not in datacolumns or "GRUNNFORM" not in datacolumns:
        raise TypeError("Passed arguments must have columns ['WORD', 'GRUNNFORM'], has: " + datacolumns)

    con = get_db()

    # Container for log-messages returned to caller
    log = []

    if refresh == True:
        delete_from_database(art.URL)
        log.append(f"Previously stored data for {art.URL} flushed.")

    if len(art_data) > 0:
        # Check if data is already is stored
        db_data = fetch_from_database(art.URL)
        if len(db_data[0].index) == 0:
            # Insert new data
            # dataset
            new_db_data = art_data
            new_db_data["URL"] = art.URL
            new_db_data.to_sql('LEMMATIZED', con, if_exists = 'append')
            # Raw text
            store_raw_text(art)
            log.append(f"{art.URL} saved into database.")
        else:
            log.append(f"{art.URL} already found in database.")

    return log

def store_raw_text(art):
    con = get_db()
    cursor = con.cursor()

    create_statement = """
    CREATE TABLE IF NOT EXISTS RAWTEXT (
        IX INTEGER PRIMARY KEY,
        URL TEXT NOT NULL UNIQUE,
        RAWTEXT TEXT NOT NULL
    )
    """
    con.execute(create_statement)

    insert_statement = """
    INSERT INTO RAWTEXT (URL, RAWTEXT)
        VALUES (?, ?)
    """
    cursor.execute(insert_statement, (art.URL, art.raw_text))
    con.commit()

def delete_from_database(URL = None):
    con = get_db()
    cursor = con.cursor()

    for table_name in ["LEMMATIZED", "RAWTEXT"]:
        if URL == None:
            # Delete all records
            delete_statement = f"""
                DELETE FROM
                    {table_name}
                """
            cursor.execute(delete_statement)
        else:
            # Delete only for supplied URL
            delete_statement = f"""
                DELETE FROM
                    {table_name}
                WHERE
                    URL = :URL
                """
            cursor.execute(delete_statement, {"URL" : URL})
    con.commit()

def fetch_from_database(URL):

    con = get_db()
    cursor = con.cursor()

    select_statement_df = """
    SELECT
	    WORD, GRUNNFORM
    FROM
	    LEMMATIZED
    WHERE
	    URL = :URL
    """

    select_statement_raw = """
    SELECT
	    RAWTEXT
    FROM
	    RAWTEXT
    WHERE
	    URL = :URL
    """

    raw_text_record = cursor.execute(select_statement_raw, {"URL" : URL}).fetchone()
    if raw_text_record == None:
        raw_text = ""
    else:
        raw_text = raw_text_record[0]

    data = [pd.read_sql(select_statement_df, con, params={"URL" : URL}),
            raw_text]
    
    return data

    

def build_worddatabase():
    # db_file = str(pathlib.Path().absolute()) + "\src\Database\\" + "WordBank.db"
    # source_folder = str(pathlib.Path().absolute()) + "\src\Database\\" + "sources\\" \
    #     + "20190123_Norsk_ordbank_nob_2005\\"
    source_folder = get_source_folder() + "20190123_Norsk_ordbank_nob_2005\\"
    con = get_db("WordBank.db")

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
    fullform_cols = ["LEMMA_ID", "OPPSLAG"]
    df_fullform = pd.read_csv(source_folder + "fullformsliste.txt", sep="\t",
        dtype=fullform_dtypes, usecols=fullform_cols, encoding=encoding)

    lemma_cols = ["LEMMA_ID", "GRUNNFORM"]
    df_lemma = pd.read_csv(source_folder + "lemma.txt", sep="\t",
        usecols=lemma_cols, encoding=encoding)

    df_lemma_translations = pd.merge(df_lemma, df_fullform, how="inner",
        on="LEMMA_ID", indicator=True)
    
    con.close()


def build_lemma_translations():
    source_folder = get_source_folder() + "20190123_Norsk_ordbank_nob_2005\\"
    encoding = 'latin-1'

    # Fullform data
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

    fullform_cols = ["LEMMA_ID", "OPPSLAG"]
    df_fullform = pd.read_csv(source_folder + "fullformsliste.txt", sep="\t",
        dtype=fullform_dtypes, usecols=fullform_cols, encoding=encoding)
    
    # Lemma data
    lemma_cols = ["LEMMA_ID", "GRUNNFORM"]
    df_lemma = pd.read_csv(source_folder + "lemma.txt", sep="\t",
        usecols=lemma_cols, encoding=encoding)


    df_lemma_translations = pd.merge(df_lemma, df_fullform, how="inner",
        on="LEMMA_ID", indicator=False)
    
    # A simplification: We will only use the first unique lookup-record
    df_lemma_translations.drop_duplicates(subset=["OPPSLAG"], inplace=True)
    
    return df_lemma_translations.drop(columns=["LEMMA_ID"])

    
def import_stopwords():
    source_folder = str(pathlib.Path().absolute()) + "\src\Database\\"
    df = pd.read_csv(source_folder + "stopwords.txt", names=["stopword"], comment="#")
    return set(df.stopword)

if __name__ == "__main__":
    # build_lemma_translations()
    # print(build_lemma_translations())
    print(import_stopwords())
