# Overheating-in-schools-tool

### ENG version ###
This repository contains the python code for a streamlit tool application to assess the overheating condition of italian schoool classrooms and buildings, both in an italian and english version. 

# Inputs and outputs
This tool allows to evaluate the overheating condition of a school building or of a single classroom, based on these inputs: 
- Location (climate zone: A, B, C, D, E, F)
- Retrofit condition of the building (no retrofit, insulated wall, insulated roof, double window)
- Ventilation rate (high or low)
- Window to floor rate
- Solar heat gain coefficient of the glazings
- Floor and position on the floor (of each classroom)
- Orientation of the window

The results are presented in terms of: 
- Share of hours in the different adaptive comfort bands
- Distribution of temperatures above the thresholds
- Compliance with the TM52 regulations
- Number of heat stress days

# Folder content
The folder contains: 
- 4 python files
   - APP                           = the classroom tool (english version)
   - APP-SCHOOL                    = the school tool (english version)
   - APP-ITA                       = the classroom tool (italian version)
   - APP-SCHOOL-ITA                = the school tool (italian version)

The results are contained in different Zenodo repositories: 
- Base case Middle classroom:      https://zenodo.org/records/20383688
- Base case Corner classroom:      https://zenodo.org/records/20383573
- Shading 0°:                      https://zenodo.org/records/20383414
- Shading 45°:                     https://zenodo.org/records/20383336
- Night ventilation:               https://zenodo.org/records/20383208
- Future weather 2050:             https://zenodo.org/records/20383515
- Future weather 2080:             https://zenodo.org/records/20383503
- Urban Heat Island:               https://zenodo.org/records/20383533

# How to use
To use the tool, open the link and input the requested data. Files for the analysis will be automatically downloaded from the zenodo repository.

- Classroom tool english:          https://overheating-in-schools-tool.streamlit.app/
- Classroom tool italian:          https://overheating-in-schools-tool-ita.streamlit.app/
- School tool english:             https://overheating-in-schools-tool-school.streamlit.app/
- School tool italian:             https://overheating-in-schools-tool-school-ita.streamlit.app/

### ITA version ###
Questo repository contiene il codice Python per un'applicazione Streamlit per valutare le condizioni di surriscaldamento delle aule e degli edifici scolastici italiani, sia in versione italiana che inglese. 

# Input e output
Questo strumento consente di valutare le condizioni di surriscaldamento di un edificio scolastico o di una singola aula, sulla base degli input: 
- Posizione (zona climatica: A, B, C, D, E, F)
- Condizioni di ristrutturazione dell'edificio (nessuna ristrutturazione, parete isolata, tetto isolato, doppia finestra)
- Tasso di ventilazione (alta o bassa)
- Rapporto superficie finestrata-pavimento
- Coefficiente di guadagno termico solare delle vetrate
- Piano e posizione sul piano (di ogni aula)
- Orientamento della finestra

I risultati sono presentati in termini di: 
- Quota di ore nelle diverse fasce di comfort adattive
- Distribuzione delle temperature al di sopra delle soglie
- Conformità alla normativa TM52
- Numero di giorni di stress termico

# Contenuto della cartella
La cartella contiene: 
- 4 file python
   - APP                           = tool per la classe (versione inglese)
   - APP-SCHOOL                    = tool per la scuola (versione inglese)
   - APP-ITA                       = tool per la classe (versione italiana)
   - APP-SCHOOL-ITA                = tool per la scuola (versione italiana)

I risultati sono contenuti in diversi repository Zenodo: 
- Caso base Classe media:          https://zenodo.org/records/20383688
- Caso base Angolo aula:           https://zenodo.org/records/20383573
- Ombreggiatura 0°:                https://zenodo.org/records/20383414
- Ombreggiatura 45°:               https://zenodo.org/records/20383336
- Ventilazione notturna:           https://zenodo.org/records/20383208
- Meteo futuro 2050:               https://zenodo.org/records/20383515
- Meteo futuro 2080:               https://zenodo.org/records/20383503
- Effetto isola di calore:         https://zenodo.org/records/20383533

# Come usarlo
Per utilizzare lo strumento, aprire il link e inserire i dati richiesti. I file per l'analisi verranno scaricati automaticamente dal repository zenodo.

- Tool per la classe in inglese:   https://overheating-in-schools-tool.streamlit.app/
- Tool per la classe in italiano:  https://overheating-in-schools-tool-ita.streamlit.app/
- Tool per la scuola in inglese:   https://overheating-in-schools-tool-school.streamlit.app/
- Tool per la scuola in italiano:  https://overheating-in-schools-tool-school-ita.streamlit.app/
