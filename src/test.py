

import DB.DBAnalyzer as DB
import time
import logging
from Visuals.Visualizer import Visualizer
# import Visuals.Visualizer as Visualizer


# num_articles = 1
# obj = DB.DBAnalyzer(num_articles, block_size = 5, logging_level = logging.WARNING)
# obj.build_articles()
# obj.fetch_articles()
# a = obj.articles[0]
# a.read()
# print(a.text)

text = ['', 'Politiet advarer dyreeiere', 'Politiet har fått flere meldinger om hunder som sitter igjen i varme biler.', 'Politiet i Agder går onsdag formiddag ut med en advarsel til dyreeiere i distriktet.', 'De skriver at de har fått flere meldinger om hunder som sitter igjen i varme biler.', '- Vi ber eiere av dyr være oppmerksomme på dette nå i sommer, skriver Agder politidistrikt.', 'Onsdag er det meldt godt over 20 grader en rekke steder i Sør-Norge.', 'Til nå har poliitet i Agder fått inn tre meldinger om hunder i varme biler før klokka tolv i dag. Det opplyser politiet i Agder til Dagbladet.', '- Det kan være skygge når de parkerer bilen sin, og så hender det fort at sola kommer etter kort tid. Dette er noe politiet får meldinger om hver sommer, sier operasjonsleder i politiet i Agder, Eivind Formo, og legger til:', '- Vi pleier å ringe eieren av bilen, slik at de kan hente hunden sin. Det pleier å løse seg fort. Det blir jo veldig fort varmt i bilen, og folk må passe på dyrene sine. Noen ganger er det bare ubetenksomhet, og det går som regel bra.', 'Mystisk fugledød: - Trist', 'Nettstedet du nå besøker blir i stor del finansiert av annonseinntekter. Basert på din tidligere aktivitet hos oss, vil du få annonser vi tror kan interessere deg.', 'Du velger selv om du ønsker å endre dine innstillinger', 'Aller Media eier nettstedene Dagbladet, Sol, DinSide, KK, Se og Hør, Lommelegen, Topp og Vi', 'dagbladet er en del av Aller Media, som er ansvarlig for dine data. Vi bruker dataene til å forbedre og tilpasse tjenestene, tilbudene og annonsene våre.']

# Visualizer.wordcloud(text)
dict = Visualizer.frequency_from_list(text)
print(dict)
