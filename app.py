import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import requests

""" Daten holen
"""
url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/' \
      'Daten/Impfquotenmonitoring.xlsx;' \
      'jsessionid=0FAB8623D95E5DF62147A144E1D768D9.internet081?__blob=publicationFile'

datum = pd.read_excel(requests.get(url).content, 0)
tag = re.search(r'\d\d\.\d\d\.\d\d', datum.iloc[1][0])
stand = tag[0][:6] + '20' + tag[0][6:]

rki_raw = pd.read_excel(requests.get(url).content, 1)[2:]  # das 2. Arbeitsblatt, ab 3. Zeile
rki_raw = rki_raw.iloc[list(range(17)), [1, 3, 6, 7, 8, 9]]
rki_raw.index = list(range(17))
rki_raw.columns = ['Bundesland', 'Erst_Impfungen_kum', 'Differenz_zum_Vortag',
                   'Impfquote_%', 'Zweit_Impfungen_kum', 'Zweit_Differenz_zum_Vortag']
rki = rki_raw
rki['Gesamt'] = rki_raw['Erst_Impfungen_kum'] + rki_raw['Zweit_Impfungen_kum']
bund = rki[-1:]
rki = rki.set_index('Bundesland')[:16]
rki_sort = rki.sort_values("Impfquote_%", ascending=False)

# Zeitreihe Impfungen vom Arbeitsblatt Nr. 4 "Impfungen_proTag"
rki_zr = pd.read_excel(requests.get(url).content, 3)
rki_zr.drop(rki_zr[-2:-1].index, inplace=True)
rki_zr.columns = ['Datum', 'Erstimpfung', 'Zweitimpfung', 'Gesamt']
rki_zr = rki_zr[(rki_zr.Gesamt != 0)]
# kumulative Werte errechnen
kum = []
s = 0
for i in rki_zr[:-1].Gesamt:
    s += i
    kum.append(s)
kum.append(s)
rki_zr['Gesamt_kum'] = kum

barbreite = [0.6]*16

""" die Grafiken definieren
"""
# Impfungen am Meldetag
figure_tag = go.Figure(
    [go.Bar(
        x=rki.index,
        y=rki["Differenz_zum_Vortag"].astype(int) + rki['Zweit_Differenz_zum_Vortag'],
        width=barbreite
    )])
gesamt_tag = f'{bund.iloc[0][2] + bund.iloc[0][5]:,}'.replace(',', '.')
figure_tag.update_layout(
    title_text=f"Impfungen gesamt (Länder gesamt {gesamt_tag})"
)

# Impfungen kumulativ bis zum Meldetag
figure_kum = go.Figure(
    [go.Bar(
        x=rki.index,
        y=rki["Gesamt"].astype(int),
        width=barbreite
    )])
gesamt_kum = f'{int(bund.iloc[0][1] + bund.iloc[0][4]):,}'.replace(',', '.')
figure_kum.update_layout(
    title_text=f"Impfungen gesamt kumulativ (Länder gesamt {gesamt_kum})"
)

# Impfungen Bevölkerung in % sortiert
figure_proz = go.Figure(
    go.Bar(
        x=rki_sort.index,
        y=[f'{i:.2f}' for i in rki_sort['Impfquote_%']],
        width=barbreite
    ))
gesamt_proz = f'{bund.iloc[0][3]:.2f} %'.replace('.', ',')
figure_proz.update_layout(
    title_text=f"Erstimpfungen prozentual zur Einwohnerzahl (Länder gesamt {gesamt_proz})"
)

# Zeitlicher Verlauf der Impfungen
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=rki_zr[:-1].Datum,
               y=rki_zr[:-1]['Gesamt_kum'],
               mode="lines+markers",
               name="Erst- und Zweitimpfung kumulativ"),
    secondary_y=True)
fig.add_trace(
    go.Scatter(x=rki_zr[:-1].Datum,
               y=rki_zr[:-1]['Gesamt'],
               name="Erst- und Zweitimpfung"),
    secondary_y=False)
fig.add_trace(
    go.Scatter(x=rki_zr[:-1].Datum,
               y=rki_zr[:-1]['Erstimpfung'],
               name="Erstimpfung"),
    secondary_y=False)
fig.add_trace(
    go.Scatter(x=rki_zr[:-1].Datum,
               y=rki_zr[:-1]['Zweitimpfung'],
               name="Zweitimpfung"),
    secondary_y=False)
fig.update_layout(
    title_text="Zeitlicher Verlauf der täglichen Impfungen (Länder gesamt)",
    legend=dict(yanchor="top", y=0.99,
                xanchor="left", x=0.01)
    )

""" die App anlegen und gestalten
"""
app = dash.Dash(__name__)
server = app.server

app.layout = \
    html.Div(
        children=[
            html.H1(
                children="Covid-19 Impfungen in Deutschland",
                className="header-title"),
            html.H3(
                children=f"Stand vom {stand}",
                className="header-subtitle"),
            html.Div(
                children=[
                    html.Span(
                        children='Datenquelle: RKI "Impfquotenmonitoring.xlsx"'),
                    html.P()
                ],
                className="header-datasource"
            ),
            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(figure=figure_tag),
                        className="card"
                    ),
                    html.Div(
                        children=dcc.Graph(figure=figure_kum),
                        className="card"
                    ),
                    html.Div(
                        children=dcc.Graph(figure=figure_proz),
                        className="card"
                    ),
                    html.Div(
                        children=dcc.Graph(figure=fig),
                        className="card"
                    )
                ],
                className="wrapper"
            ),
            html.Div(
                html.P(
                    children=[
                        html.Span("Stand 26.01.2021 "),
                        html.A("Quellcode hier", href="https://github.com/haddo42/Impfstand")
                    ]
                ),
                className="div-source"
            )
        ]
    )

if __name__ == "__main__":
    app.run_server(debug=True)
