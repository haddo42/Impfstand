# Ploty-Dash-Applikation
Die Applikation zeigt den täglichen Stand der Impfkampagne in Deutschland und seinen Bundesländern. Die Daten hierfür stammen vom Rober-Koch-Instituts, das [hier]() eine werktäglich aktualisierte Excel-Datei bereitstellt. Das Programm liest diese Daten direkt in ein Pandas-Dataframe ein und stellt sie in Plotly-Grafiken in der Dash-Anwendung bereit.

Mit [**HEROKU**](https://www.heroku.com) ist der Test einer Plotly-Dash-Applikation im Web möglich. Die zahlreichen Beispiele im Netz machen den Einstieg leicht. Schwierigkeiten gibt es bei der Datei `requirements.txt`. Was gehört für eine Applikation zwingend in die Datei hinein? 

Mit Hilfe des [Beispiels](https://medium.com/@austinlasseter/how-to-deploy-a-simple-plotly-dash-app-to-heroku-622a2216eb73) von **Austin Lasseter** gelingen die ersten Schritte. Hilfreich sind auch die Tips einer guten IDE. So sagte im vorliegenden Beispiel `PyCharm`, dass  wegen `import requests` auch `requests` in die Datei `requirements.txt` gehört. Weitere Hinweise können den Logdateien auf HEROKU entnommen werden. Für das Beispiel sind diese mit
- `heroku logs -a=impfstand --tail`

erreichbar und erbrachte den Hinweis, dass der Pythonmodul **`xlrd`** nicht gefunden wurde. In der lokalen Lösung spielt der Modul explizit keine Rolle. Offenbar wird er aber von `Pandas` beim Laden eines Dataframes mit einer aus dem Web direkt übernommenen Datei vom Typ `xlsx` benötigt. Nach seiner Aufnahme in `requirements.txt` lief die App dann wie erwartet.
