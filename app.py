import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import requests

""" Bevölkerungsdaten 
    Quelle https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/
           Bevoelkerung/Bevoelkerungsstand/Tabellen/bevoelkerung-nichtdeutsch-laender.html
"""
# Menschen in D. am 31.12.2019
menschen = [
    ["Baden-Württemberg", 11100394, 9338713, 1761681, 15.9],
    ["Bayern", 13124737, 11344979, 1779758, 13.6],
    ["Berlin", 3669491, 2963425, 706066, 19.2],
    ["Brandenburg", 2521893, 2397020, 124873, 5.0],
    ["Bremen", 681202, 555005, 126197, 18.5],
    ["Hamburg", 1847253, 1541632, 305621, 16.5],
    ["Hessen", 6288080, 5244990, 1043090, 16.6],
    ["Mecklenburg-Vorpommern", 1608138, 1533331, 74807, 4.7],
    ["Niedersachsen", 7993608, 7220393, 773215, 9.7],
    ["Nordrhein-Westfalen", 17947221, 15502665, 2444556, 13.6],
    ["Rheinland-Pfalz", 4093903, 3623676, 470227, 11.5],
    ["Saarland", 986887, 873967, 112920, 11.4],
    ["Sachsen", 4071971, 3863937, 208034, 5.1],
    ["Sachsen-Anhalt", 2194782, 2083117, 111665, 5.1],
    ["Schleswig-Holstein", 2903773, 2659604, 244169, 8.4],
    ["Thüringen", 2133378, 2022235, 111143, 5.2],
    ["Gesamt", 83166711, 72768689, 10398022, 12.5]
]
people = pd.DataFrame(menschen)
people.columns = ["Bundesland", "Gesamt", "Deutsche", "nichtDeutsche", "nD%"]

""" RKI-Daten holen
"""
url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/'
url += 'Daten/Impfquotenmonitoring.xlsx;'
url += 'jsessionid=0FAB8623D95E5DF62147A144E1D768D9.internet081?__blob=publicationFile'

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
rki['Menschen'] = people['Gesamt']
rki['Zweitquote_%'] = rki['Zweit_Impfungen_kum'] / rki['Menschen'] * 100
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

""" die Grafiken definieren
"""

# Impfungen
fig_impfungen = go.Figure()
fig_impfungen.add_trace(
    go.Bar(
        name="1.Impf./Tag",
        marker=dict(color="steelblue"),
        width=.3,
        offset=-0.3,
        x=rki.index,
        y=rki["Differenz_zum_Vortag"],
        legendgroup="group1",
    )
)
fig_impfungen.add_trace(
    go.Bar(
        name="2.Impf./Tag",
        marker=dict(color="orange"),
        width=.3,
        offset=-0.3,
        x=rki.index,
        y=rki["Zweit_Differenz_zum_Vortag"],
        legendgroup="group1",
    )
)
fig_impfungen.add_trace(
    go.Bar(
        name="1.Impf./kum.",
        marker=dict(color="blue"),
        width=.3,
        offset=0.05,
        x=rki.index,
        y=rki["Erst_Impfungen_kum"],
        yaxis="y2",
        legendgroup="group2",
    )
)
fig_impfungen.add_trace(
    go.Bar(
        name="2.Impf./kum.",
        marker=dict(color="tomato"),
        width=.3,
        offset=0.05,
        x=rki.index,
        y=rki["Zweit_Impfungen_kum"],
        yaxis="y2",
        legendgroup="group2",
    )
)
fig_impfungen.update_layout(
    title_text=f"Impfungen Stand Berichtstag",
    yaxis=dict(title='Impfungen Tag'),
    barmode="stack",
    legend=dict(orientation='h', yanchor='bottom', y=1.0),
    yaxis2=dict(title='Impfungen kum.', overlaying='y', side='right'),
)

# Tabelle Impfungen Bund
bund_erst_tag = f'{bund.iloc[0][2]:,}'.replace(',', '.')
bund_zweit_tag = f'{bund.iloc[0][5]:,}'.replace(',', '.')
bund_erst_kum = f'{bund.iloc[0][1]:,}'.replace(',', '.')
bund_zweit_kum = f'{bund.iloc[0][4]:,}'.replace(',', '.')


def impf_table():
    return \
        html.Div(
            html.Table(
                children=[
                    html.Tr(
                        children=[
                            html.Th('Länder gesamt'),
                            html.Th('Tag'),
                            html.Th('kumulativ'),
                        ],
                    ),
                    html.Tr(
                        children=[
                            html.Td('Erstimpfung'),
                            html.Td(bund_erst_tag),
                            html.Td(bund_erst_kum),
                        ],
                    ),
                    html.Tr(
                        children=[
                            html.Td('Zweitimpfung'),
                            html.Td(bund_zweit_tag),
                            html.Td(bund_zweit_kum),
                        ],
                    ),
                ],
                className="tbl-impfungen",
            ),
        )


# Impfquoten in %
fig_proz = go.Figure()
fig_proz.add_trace(
    go.Bar(
        name="Erstimpfungen",
        x=rki_sort.index,
        y=rki_sort['Impfquote_%'],
        width=0.3,
        offset=-0.3,
        marker=dict(color="steelblue"),
        offsetgroup=1,
    )
)
fig_proz.add_trace(
    go.Bar(
        name='Zweitimpfungen',
        x=rki_sort.index,
        y=rki_sort['Zweitquote_%'],
        width=0.3,
        offset=0.05,
        marker=dict(color="orange"),
        offsetgroup=2,
    ),
)
fig_proz.update_layout(
    title_text=f"Impfquoten Stand Berichtstag",
    legend=dict(orientation='h', yanchor='bottom', y=1.0),
    yaxis=dict(title="Quote in %")
)

# Tabelle Impfquoten Bund
gesamt_erst_proz = f'{bund.iloc[0][3]:.2f} %'.replace('.', ',')
gesamt_zweit_proz = f'{bund.iloc[0][8]:.2f} %'.replace('.', ',')
what = 'Hi'


def quoten_table():
    return \
        html.Div(
            html.Table(
                children=[
                    html.Tr(
                        children=[
                            html.Th(''),
                            html.Th('Erstimpfung'),
                            html.Th('Zweitimpfung'),
                        ],
                    ),
                    html.Tr(
                        children=[
                            html.Td('Länder gesamt'),
                            html.Td(gesamt_erst_proz),
                            html.Td(gesamt_zweit_proz),
                        ]
                    )
                ],
                className="tbl-impfungen",
            ),
        )


# Zeitlicher Verlauf der Impfungen
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(
        name="Erst- und Zweitimpfung kumulativ",
        x=rki_zr[:-1].Datum,
        y=rki_zr[:-1]['Gesamt_kum'],
        mode="lines+markers",
        marker=dict(color="black"),
    ),
    secondary_y=True)
fig.add_trace(
    go.Bar(
        name="Erstimpfung",
        x=rki_zr[:-1].Datum,
        y=rki_zr[:-1]['Erstimpfung'],
        marker=dict(color="steelblue"),
        offsetgroup=1),
    secondary_y=False)
fig.add_trace(
    go.Bar(
        name="Zweitimpfung",
        x=rki_zr[:-1].Datum,
        y=rki_zr[:-1]['Zweitimpfung'],
        marker=dict(color="orange"),
        offsetgroup=1),
    secondary_y=False)
fig.add_trace(
    go.Scatter(
        name="Erst- und Zweitimpfung",
        x=rki_zr[:-1].Datum,
        y=rki_zr[:-1]['Erstimpfung'] + rki_zr[:-1]['Zweitimpfung'],
        mode="markers",
        marker=dict(
            color="red",
            size=10,
            symbol="triangle-down",
            line=dict(
                width=1,
                color="black",
            )
        )
    ),
    secondary_y=False)
fig.update_layout(
    title_text="Zeitlicher Verlauf der Impfungen (Länder gesamt)",
    barmode="stack",
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
                children=f"Berichtstag {stand}",
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
                        children=[
                            dcc.Graph(figure=fig_impfungen),
                            impf_table(),
                        ],
                        className="card"
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(figure=fig_proz),
                            quoten_table(),
                        ],
                        className="card",
                    ),
                    html.Div(
                        dcc.Graph(figure=fig),
                        className="card"
                    )
                ],
                className="wrapper"
            ),
            html.Div(
                html.P(
                    children=[
                        html.Span("Stand 02.02.2021 "),
                        html.A("Quellcode hier", href="https://github.com/haddo42/Impfstand")
                    ]
                ),
                className="div-source"
            )
        ]
    )

if __name__ == "__main__":
    app.run_server(debug=True)
