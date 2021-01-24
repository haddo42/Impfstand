# Ploty-Dash-Applikation
Mit [**HEROKU**](https://www.heroku.com) ist der Test einer Plotly-Dash-Applikation im Web möglich. Die zahlreichen Beispiele im Netz machen den Einstieg leicht. Schwierigkeiten macht die Datei `requirements.txt`. Was gehört für meine Applikation zwingend in die Datei hinein? 

Zunächst übernahm ich einfach "blind" die Angaben aus meinem [Einsteigerbeispiel](https://medium.com/@austinlasseter/how-to-deploy-a-simple-plotly-dash-app-to-heroku-622a2216eb73) - danke **Austin Lasseter**. Dann sagte mir meine IDE `PyCharm`, dass  wegen `import requests` auch `requests` in die Datei `requirements.txt` gehört. Danach erhielt ich beim Versuch, die Applikation auf HEROKU zu starten, weiterhin eine Fehlermeldung.
 
Der mit der Fehlermeldung verbundene Hinweis, die Logdatei zu befragen, lautete in meinem Fall 
- `heroku logs -a=impfstand --tail`

und erbrachte den Hinweis, dass der Pythonmodul **`xlrd`** nicht gefunden wurde. In der lokalen Lösung spielt der Modul explizit keine Rolle. Nach seiner Aufnahme in `requirements.txt` lief die App dann wie erwartet.
