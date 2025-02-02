"""
GeoReveal

GeoReveal è un'applicazione che ti permette di caricare una cartella di foto e visualizzarle su una mappa interattiva con i marker che segnano la posizione di ciascuna foto. Al primo avvio, verrà creato automaticamente un database per gestire i tuoi casi.

Requisiti:
1. Python 3.x
2. Librerie Python necessarie (vedi sotto)
3. Una cartella contenente le tue foto

Installazione:
1. Clona il repository:
   git clone https://github.com/GiuseppeVaccaro27/GeoReveal.git
   cd GeoReveal

2. Installa le dipendenze:
   pip install -r requirements.txt

Come utilizzare l'app:
1. Prepara la cartella delle foto:
   L'applicazione richiede una cartella con delle foto da visualizzare sulla mappa. Crea una cartella chiamata 'foto' (o un altro nome di tua scelta) e metti dentro tutte le foto che desideri visualizzare.

2. Avvio dell'applicazione:
   Esegui l'app Python. Al primo avvio, l'app creerà automaticamente un database chiamato 'cases.db' per memorizzare le informazioni sui casi.

   python app.py

3. Creazione del caso:
   Quando avvii l'app per la prima volta, ti verrà chiesto di creare un "caso" che consisterà nell'insieme delle foto da visualizzare. Dopo aver creato il caso, il database salverà tutte le informazioni relative alle foto e alle loro posizioni.

4. Selezione delle foto:
   Una volta che il caso è stato creato e le foto sono state aggiunte al database, potrai selezionare le foto che vuoi visualizzare sulla mappa. Le foto selezionate saranno caricate sulla mappa con dei marker che segnano le rispettive posizioni.

5. Visualizzazione sulla mappa:
   Dopo aver selezionato le foto, si aprirà una mappa interattiva (basata su Folium) che ti mostrerà i marker corrispondenti alle posizioni delle tue foto.

Struttura dei file:
- 'app.py': Il file principale per eseguire l'applicazione.
- 'cases.db': Il database che contiene i dati sui casi e le posizioni delle foto.
- 'foto/': La cartella che contiene le tue foto (crea questa cartella prima di avviare l'app).
- 'requirements.txt': Il file delle dipendenze necessarie per eseguire l'applicazione.

Contribuire:
Se desideri contribuire a migliorare GeoReveal, sentiti libero di fare un fork di questo repository, apportare le modifiche e fare una pull request.

Licenza:
Questo progetto è sotto licenza MIT. Vedi il file LICENSE per ulteriori dettagli.

"""
