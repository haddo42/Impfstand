import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import re
import requests


""" Daten holen
"""
url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/' \
      'Daten/Impfquotenmonitoring.xlsx;' \
      'jsessionid=0FAB8623D95E5DF62147A144E1D768D9.internet081?__blob=publicationFile'

datum = pd.read_excel(requests.get(url).content, 0)
tag = re.search(r'\d\d\.\d\d\.\d\d', datum.iloc[1][0])
stand = tag[0][:6]+'20'+tag[0][6:]

rki_raw = pd.read_excel(requests.get(url).content, 1)[2:] # das zweite Arbeitsblatt
rki_raw = rki_raw.iloc[list(range(17)), [1, 3, 6, 7]]
rki_raw.index = list(range(17))
rki_raw.columns = ['Bundesland', 'Erst_Impfungen_kum', 'Differenz_zum_Vortag', 'Impfquote_%']
rki = rki_raw
bund = rki[-1:]
rki = rki.set_index('Bundesland')[:16]

rki_sort = rki.sort_values("Impfquote_%", ascending=False)

""" Figuren machen
"""
figure_tag = go.Figure(
    [
        go.Bar(
            x=rki.index,
            y=rki["Differenz_zum_Vortag"].astype(int),
        ),
    ]
)
gesamt_tag = f'{int(bund.iloc[0][2]):,}'.replace(',', '.')
figure_tag.update_layout(
    title_text=f"Impfungen am {stand} (Länder gesamt {gesamt_tag})"
    )
figure_tag.update_traces(
    # hovertemplate="%{y:.0f}<extra></extra>"
)

figure_kum = go.Figure(
    [
        go.Bar(
            x=rki.index,
            y=rki["Erst_Impfungen_kum"].astype(int)
        )
    ]
)
gesamt_kum = f'{int(bund.iloc[0][1]):,}'.replace(',', '.')
figure_kum.update_layout(
    title_text=f"Erstimpfungen kumulativ bis zum {stand} (Länder gesamt {gesamt_kum})"
)
figure_kum.update_traces(
    # hovertemplate="%{y:,.0f}<extra></extra>"#.replace(',', '.')
)

figure_proz = go.Figure(
    go.Bar(
        x=rki_sort.index,
        y=[f'{i:.2f}' for i in rki_sort['Impfquote_%']]
        # y=rki_sort["Impfquote_%"]
    )
)
gesamt_proz = f'{bund.iloc[0][3]:.2f} %'.replace('.', ',')
figure_proz.update_layout(
    title_text=f"Quote Erstimpfungen prozentual zur Einwohnerzahl Stand {stand} (Länder gesamt {gesamt_proz})"
)

""" App bauen
"""
app = dash.Dash(__name__)
server = app.server
app.layout = \
    html.Div(
        children=[
            html.H1(
                children="Covid-19 Impfungen in Deutschland",
                className="header-title"),
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
                        children=dcc.Graph(
                            figure=figure_tag,
                        ),
                        className="card"
                    ),
                    html.Div(
                        children=dcc.Graph(
                            figure=figure_kum
                        ),
                        className="card"
                    ),
                    html.Div(
                        children=dcc.Graph(
                            figure=figure_proz
                        ),
                        className="card"
                    )
                ],
                className="wrapper"
            )
        ]
    )

if __name__ == "__main__":
    app.run_server(debug=True)
