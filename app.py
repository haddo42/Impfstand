import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import requests

""" RKI-Daten Impfquotenmonitoring.xlsx
"""
url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/' \
      'Daten/Impfquotenmonitoring.xlsx;' \
      'jsessionid=0FAB8623D95E5DF62147A144E1D768D9.internet081?__blob=publicationFile'
datum = pd.read_excel(requests.get(url).content, 0)
tag = re.search(r'\d\d\.\d\d\.\d\d', datum.iloc[1][0])
stand = tag[0][:6]+'20'+tag[0][6:]
rki_raw = pd.read_excel(requests.get(url).content, 1)[2:]
rki_raw = rki_raw.iloc[list(range(18)), [1, 2, 3, 7, 8, 9, 12, 13]]
rki_raw.index = list(range(18))
rki_cols = ['Bundesland', 'Gesamt_Impf_kum', 'Erst_Impf_kum', 'Erst_Impf_Tag',
            'Erst_Impf_Quote', 'Zweit_Impf_kum', 'Zweit_Impf_Tag', 'Zweit_Impf_Quote']
rki_raw.columns = rki_cols
rki = rki_raw[rki_raw.index != 16]
bund = rki[-1:]
rki = rki.set_index('Bundesland')[:16]
rki_sort = rki.sort_values("Erst_Impf_Quote", ascending=False)

""" RKI-Daten Zeitreihen
"""
url = "https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv"
rki_raw = pd.read_csv(url, sep="\t")
rki_zr = rki_raw[['date', 'dosen_kumulativ', 'dosen_differenz_zum_vortag',
                  'dosen_erst_differenz_zum_vortag', 'dosen_zweit_differenz_zum_vortag',
                  'personen_erst_kumulativ', 'personen_voll_kumulativ']]

rki_zr.columns = ['Datum', 'Gesamt_kum', 'Gesamt_tag', 'Erst_Impf_Tag',
                  'Zweit_Impf_Tag', 'Erst_Impf_kum', 'Voll_Impf_kum']

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
        y=rki["Erst_Impf_Tag"],
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
        y=rki["Zweit_Impf_Tag"],
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
        y=rki["Erst_Impf_kum"],
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
        y=rki["Zweit_Impf_kum"],
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
bund_erst_tag = f'{bund.iloc[0][3]:,}'.replace(',', '.')
bund_zweit_tag = f'{bund.iloc[0][6]:,}'.replace(',', '.')
bund_erst_kum = f'{bund.iloc[0][2]:,}'.replace(',', '.')
bund_zweit_kum = f'{bund.iloc[0][5]:,}'.replace(',', '.')


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
        y=rki_sort['Erst_Impf_Quote'],
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
        y=rki_sort['Zweit_Impf_Quote'],
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
gesamt_erst_proz = f'{bund.iloc[0][4]:.2f} %'.replace('.', ',')
gesamt_zweit_proz = f'{bund.iloc[0][7]:.2f} %'.replace('.', ',')


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
        x=rki_zr.Datum,
        y=rki_zr['Gesamt_kum'],
        mode="lines+markers",
    ),
    secondary_y=True)
fig.add_trace(
    go.Scatter(
        name="Erstimpfung kumulativ",
        x=rki_zr.Datum,
        y=rki_zr['Erst_Impf_kum'],
        mode='lines+markers',
    ),
    secondary_y=True)
fig.add_trace(
    go.Scatter(
        name="Zweit-(Voll-)impfung kumulativ",
        x=rki_zr.Datum,
        y=rki_zr['Voll_Impf_kum'],
        mode='lines+markers',
        fill='tozeroy',
    ),
    secondary_y=True)
fig.update_layout(
    title_text="Zeitlicher Verlauf der Impfungen (Länder gesamt)",
    barmode="stack",
    legend=dict(yanchor="top", y=.98,
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
                        children='Datenquelle: Robert-Koch-Institut'),
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
                        html.Span("Stand 07.02.2021 "),
                        html.A("Quellcode hier", href="https://github.com/haddo42/Impfstand")
                    ]
                ),
                className="div-source"
            )
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
