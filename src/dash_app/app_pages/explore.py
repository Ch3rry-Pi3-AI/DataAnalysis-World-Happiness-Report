# # src/dash_app/app_pages/explore.py
# import dash
# from dash import html, dcc, Input, Output, callback
# import pandas as pd
# import plotly.express as px

# from src.dash_app.data_access import get_gold_df

# dash.register_page(__name__, path="/explore", name="Explore 🔎", order=2)

# # ---------------- Helpers ----------------
# def _df() -> pd.DataFrame:
#     return get_gold_df()

# def _numeric_cols(df: pd.DataFrame) -> list[str]:
#     num = df.select_dtypes(include="number").columns.tolist()
#     headline = [
#         "ladder_score",
#         "logged_gdp_per_capita",
#         "healthy_life_expectancy",
#         "social_support",
#         "freedom_to_make_life_choices",
#         "generosity",
#         "perceptions_of_corruption",
#     ]
#     return [c for c in headline if c in num] + [c for c in num if c not in headline]

# def _year_options(df: pd.DataFrame):
#     years = sorted(pd.Series(df["year"]).dropna().unique().tolist()) if "year" in df.columns else []
#     return [{"label": str(int(y)), "value": int(y)} for y in years]

# def _region_options(df: pd.DataFrame):
#     if "regional_indicator" not in df.columns:
#         return []
#     regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
#     return [{"label": r, "value": r} for r in regs]

# def _labels(s: str) -> str:
#     return s.replace("_", " ").title()

# # ---------------- Data / Defaults ----------------
# _BASE = _df()
# _NUMS = _numeric_cols(_BASE)
# _DEFAULT_X = _NUMS[0] if _NUMS else None
# _DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

# # ---------------- Layout ----------------
# controls_col = html.Div(
#     className="col-12 col-lg-3",
#     children=[
#         html.H5("Controls", className="fw-bold mb-3"),
#         html.Label("Year", className="form-label mb-1"),
#         dcc.Dropdown(
#             id="ex-year-dd",
#             options=_year_options(_BASE),
#             placeholder="(optional)",
#             clearable=True,
#             style={"fontSize": "12px"},
#         ),
#         html.Div(style={"height": "8px"}),

#         html.Label("Region(s)", className="form-label mb-1"),
#         dcc.Dropdown(
#             id="ex-region-dd",
#             options=_region_options(_BASE),
#             placeholder="(optional)",
#             multi=True,
#             clearable=True,
#             style={"fontSize": "12px"},
#         ),
#         html.Div(style={"height": "8px"}),

#         html.Label("X axis", className="form-label mb-1"),
#         dcc.Dropdown(
#             id="ex-x-dd",
#             options=[{"label": _labels(c), "value": c} for c in _NUMS],
#             value=_DEFAULT_X,
#             clearable=False,
#             style={"fontSize": "12px"},
#         ),
#         html.Div(style={"height": "8px"}),

#         html.Label("Y axis", className="form-label mb-1"),
#         dcc.Dropdown(
#             id="ex-y-dd",
#             options=[{"label": _labels(c), "value": c} for c in _NUMS],
#             value=_DEFAULT_Y,
#             clearable=False,
#             style={"fontSize": "12px"},
#         ),
#         html.Hr(),
#         html.Small("Tip: choose X & Y, then refine by year and region.", className="text-muted"),
#     ],
# )

# plots_col = html.Div(
#     className="col-12 col-lg-9",
#     children=[
#         dcc.Graph(id="ex-rel-fig", style={"height": "400px"}, className="mb-3"),
#         dcc.Graph(id="ex-dist-fig", style={"height": "400px"}),
#     ],
# )

# layout = html.Div(
#     className="container-fluid py-4 rounded-2",
#     style={"backgroundColor": "#649ec784"},
#     children=[
#         html.Div(
#             className="text-center mb-4",
#             children=[
#                 html.H2("Explore", className="text-light fw-bold"),
#                 html.P(
#                     "Investigate relationships and distributions in the World Happiness dataset.",
#                     className="text-light fw-bold",
#                 ),
#             ],
#         ),
#         html.Div(
#             className="card shadow-sm rounded-2",
#             children=[
#                 html.Div(
#                     className="card-body",
#                     children=[html.Div(className="row g-3", children=[controls_col, plots_col])],
#                 )
#             ],
#         ),
#     ],
# )

# # ---------------- Callbacks ----------------
# def _apply_filters(df: pd.DataFrame, year_value, regions):
#     if year_value is not None and "year" in df.columns:
#         df = df[df["year"] == int(year_value)]
#     if regions and "regional_indicator" in df.columns:
#         if not isinstance(regions, list):
#             regions = [regions]
#         df = df[df["regional_indicator"].isin(regions)]
#     return df

# @callback(
#     Output("ex-rel-fig", "figure"),
#     Input("ex-x-dd", "value"),
#     Input("ex-y-dd", "value"),
#     Input("ex-year-dd", "value"),
#     Input("ex-region-dd", "value"),
# )
# def _update_relationship(x_col, y_col, year_value, region_values):
#     df = _apply_filters(_df(), year_value, region_values)
#     if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
#         return px.scatter(title="Select X and Y to view their relationship")

#     color = "regional_indicator" if "regional_indicator" in df.columns else None
#     fig = px.scatter(
#         df,
#         x=x_col,
#         y=y_col,
#         color=color,
#         hover_data=["country_name", "year"] if {"country_name", "year"}.issubset(df.columns) else None,
#         title=f"{_labels(x_col)} vs {_labels(y_col)}"
#               + (f" — Year {year_value}" if year_value else ""),
#         opacity=0.9,
#     )
#     fig.update_traces(marker={"line": {"width": 0.5}})
#     fig.update_layout(
#         margin={"t": 60, "l": 10, "r": 10, "b": 10},
#         legend=dict(title="Region", bgcolor="rgba(255,255,255,0.6)"),
#     )
#     return fig

# @callback(
#     Output("ex-dist-fig", "figure"),
#     Input("ex-x-dd", "value"),
#     Input("ex-year-dd", "value"),
#     Input("ex-region-dd", "value"),
# )
# def _update_distribution(metric, year_value, regions):
#     df = _apply_filters(_df(), year_value, regions)
#     if not metric or metric not in df.columns:
#         return px.histogram(title="Select a metric to view its distribution")

#     color = "regional_indicator" if "regional_indicator" in df.columns else None
#     fig = px.histogram(
#         df,
#         x=metric,
#         color=color,
#         barmode="overlay" if color else "relative",
#         opacity=0.75,
#         title=f"Distribution of {_labels(metric)}"
#               + (f" — Year {year_value}" if year_value else ""),
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_layout(
#         margin={"t": 60, "l": 10, "r": 10, "b": 10},
#         legend=dict(title="Region", bgcolor="rgba(255,255,255,0.6)"),
#     )
#     return fig
