import urllib.request
import tarfile

def download_ordbank():
    url = "https://www.nb.no/sbfil/leksikalske_databaser/ordbank/20190123_norsk_ordbank_nob_2005.tar.gz"
    sources_dir = "src\\Database\\sources\\"
    downloaded_filename = sources_dir + "20190123_norsk_ordbank_nob_2005.tar.gz"

    urllib.request.urlretrieve(url, downloaded_filename)

    tar = tarfile.open(downloaded_filename, "r:gz")
    tar.extractall(path = sources_dir)
    tar.close()

def download_politicians():
    url = "https://www.valg.no/globalassets/dokumenter-2021/lister-og-partier/valglisterogkandidaterstortingsvalget2021.csv"
    sources_dir = "src\\Database\\sources\\"
    downloaded_filename = sources_dir + "valglisterogkandidaterstortingsvalget2021.csv"
    ## Hack - specify this user-agent in order to bypass status-code 403
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req).read()
    with open(downloaded_filename, "w", newline="") as file:
        file.write(data.decode("utf-8"))

if __name__ == "__main__":
    download_politicians()
    download_ordbank()