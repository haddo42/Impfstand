# Ploty-Dash-Applikation
Die Applikation zeigt den täglichen Stand der Covid-19 Impfkampagne für Deutschland 
und seine Bundesländern. Die Daten hierfür stammen vom Rober-Koch-Instituts, das 
[hier](https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Impfquotenmonitoring.xlsx;jsessionid=0FAB8623D95E5DF62147A144E1D768D9.internet081?__blob=publicationFile) 
eine werktäglich um ca. 13:00 Uhr aktualisierte Excel-Datei bereitstellt. 
Das Programm liest diese Daten direkt in ein Pandas-Dataframe ein und stellt sie in 
Plotly-Grafiken in der Dash-Anwendung bereit. Mit Hilfe dieses [Beispiels](https://medium.com/@austinlasseter/how-to-deploy-a-simple-plotly-dash-app-to-heroku-622a2216eb73) 
gelingen die ersten Schritte.

Auf [**HEROKU**](https://www.heroku.com) ist der Test einer Plotly-Dash-Applikation 
im Web möglich. Das oben genannte Beispiel macht auch hier den Einstieg leicht. 
Schwierigkeiten gab es bei der Datei `requirements.txt`. Was gehört für eine 
Applikation zwingend in die Datei hinein? Hinweise können den Logdateien auf HEROKU
entnommen werden. Für das Beispiel waren diese mit
- `heroku logs -a=impfstand --tail`

erreichbar und zeigten an, dass der Pythonmodul **`xlrd`** nicht gefunden wurde. 
In der lokalen Lösung spielt der Modul explizit keine Rolle. Offenbar wird er 
aber von `Pandas` beim Laden eines Dataframes mit einer aus dem Web direkt 
übernommenen Datei vom Typ `xlsx` benötigt. Nach seiner Aufnahme in 
`requirements.txt` lief die App dann wie erwartet ([siehe hier](https://impfstand.herokuapp.com)).
