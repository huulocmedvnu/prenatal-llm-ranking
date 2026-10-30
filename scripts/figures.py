"""Figures 2-4 (plotly, plotly_white, Arial, black text, no gridlines) from outputs/fig_data.json."""
import json, os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.stats.proportion import proportion_confint

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "docs", "figures"); os.makedirs(FIG, exist_ok=True)
D = json.load(open(os.path.join(ROOT, "outputs", "fig_data.json")))
BLUE, RED, GREEN, PURPLE = "#636EFA", "#EF553B", "#00CC96", "#AB63FA"
K = "#111111"
FONT = dict(family="Arial", size=13, color=K)


def style(fig, w, h):
    fig.update_layout(template="plotly_white", font=FONT, width=w, height=h, margin=dict(l=10, r=20, t=40, b=60),
                      legend=dict(orientation="h", y=-0.16, x=0.5, xanchor="center", font=FONT))
    fig.update_xaxes(showgrid=False, showline=True, linecolor=K, ticks="outside", tickcolor=K, tickfont=FONT,
                     title_font=FONT, zeroline=False)
    fig.update_yaxes(showgrid=False, tickfont=FONT, title_font=FONT, zeroline=False)
    fig.update_annotations(font=dict(family="Arial", size=14, color=K))
    return fig


def save(fig, name):
    fig.write_image(os.path.join(FIG, f"{name}.png"), scale=4)
    fig.write_image(os.path.join(FIG, f"{name}.pdf"))


def wilson(x, n):
    lo, hi = proportion_confint(x, n, method="wilson"); return 100 * x / n, 100 * lo, 100 * hi


# Figure 2: top-10 and top-1 by method, pre- vs post-cutoff
order = ["HPO semantic similarity", "Exomiser hiPHIVE", "Exomiser human-only", "Llama 3.1 8B", "Gemma 3 12B",
         "Qwen3 14B", "gpt-oss 20B", "Claude Haiku 5.5", "Claude Sonnet 5.5", "Claude Opus 5.5"]
order = [m for m in order if m in D["methods"]]
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                    subplot_titles=("a  Causal gene in the top 10", "b  Causal gene ranked first"))
for col, t in [(1, "top10"), (2, "top1")]:
    for per, colour, lab, off in [("pre", BLUE, "Fetuses reported before 1 July 2026 (n=299)", 0.15),
                                  ("post", RED, "Fetuses reported from 1 July 2026 (n=153)", -0.15)]:
        xs = [D["methods"][m][per][t]["p"] for m in order]
        lo = [D["methods"][m][per][t]["lo"] for m in order]; hi = [D["methods"][m][per][t]["hi"] for m in order]
        ys = [i + off for i in range(len(order))]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(symbol="diamond", size=10, color=colour),
                                 error_x=dict(type="data", symmetric=False, array=[h - x for h, x in zip(hi, xs)],
                                              arrayminus=[x - l for x, l in zip(xs, lo)], color=colour, thickness=1.2, width=0),
                                 name=lab, showlegend=(col == 1)), row=1, col=col)
fig.update_yaxes(tickvals=list(range(len(order))), ticktext=order, row=1, col=1)
fig.update_xaxes(title_text="Fetuses (%)", range=[0, 60], row=1, col=1)
fig.update_xaxes(title_text="Fetuses (%)", range=[0, 30], row=1, col=2)
save(style(fig, 1000, 520), "figure2")

# Figure 3: (a) adjusted odds ratio post vs pre, (b) input perturbations (335 fetuses)
adj = D["adjusted"]["models"]
am = [("resnik", "HPO semantic similarity"), ("exomiser_hiphive", "Exomiser hiPHIVE"), ("haiku_r1", "Claude Haiku 5.5"),
      ("sonnet_r1", "Claude Sonnet 5.5"), ("opus_r1", "Claude Opus 5.5")]
tk = D["analysis_v2"]; n = 335
cond = [("As written in the source", "{m}-5-5_r1"), ("Order of findings shuffled", "{m}-5-5_T3a_order"),
        ("HPO exact synonyms", "{m}-5-5_T3b_synonym"), ("HPO labels", "{m}-5-5_S2_hpolabel"),
        ("HPO identifiers only", "{m}-5-5_T3c_hpoid"), ("Findings of another fetus", "{m}-5-5_N1p1"),
        ("Citation and case number only", "{m}-5-5_T2")]
fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.32, column_widths=[0.45, 0.55],
                    subplot_titles=("a  Odds ratio, later vs earlier fetuses", "b  Causal gene in the top 10 (335 fetuses)"))
for i, (k, lab) in enumerate(am):
    v = adj[k]["adjusted"]; u = adj[k]["unadjusted"]
    for vv, colour, name, off in [(u, "#999999", "Unadjusted", 0.15), (v, BLUE, "Adjusted for case features", -0.15)]:
        fig.add_trace(go.Scatter(x=[vv["OR"]], y=[i + off], mode="markers", marker=dict(symbol="diamond", size=10, color=colour),
                                 error_x=dict(type="data", symmetric=False, array=[vv["ci"][1] - vv["OR"]],
                                              arrayminus=[vv["OR"] - vv["ci"][0]], color=colour, thickness=1.2, width=0),
                                 name=name, showlegend=(i == 0), legendgroup=name), row=1, col=1)
fig.add_vline(x=1, line=dict(color="#888888", width=1, dash="dot"), row=1, col=1)
fig.update_xaxes(type="log", title_text="Odds ratio (log scale)", tickvals=[0.1, 0.2, 0.5, 1, 2, 5, 10], row=1, col=1)
fig.update_yaxes(tickvals=list(range(len(am))), ticktext=[l for _, l in am], row=1, col=1)
for m, colour, lab, off in [("haiku", GREEN, "Claude Haiku 5.5", 0.15), ("opus", PURPLE, "Claude Opus 5.5", -0.15)]:
    xs, lo, hi, ys = [], [], [], []
    for j, (c, pat) in enumerate(cond):
        if c == "Findings of another fetus" and m == "haiku":
            x = sum(tk[f"haiku-5-5_N1p{p}"]["all"]["top10"] for p in range(1, 6)) / 5
        else:
            x = tk[pat.format(m=m)]["all"]["top10"]
        p_, l_, h_ = wilson(round(x), n)
        xs.append(100 * x / n); lo.append(l_); hi.append(h_); ys.append(j + off)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(symbol="diamond", size=10, color=colour),
                             error_x=dict(type="data", symmetric=False, array=[h - x for h, x in zip(hi, xs)],
                                          arrayminus=[x - l for x, l in zip(xs, lo)], color=colour, thickness=1.2, width=0),
                             name=lab), row=1, col=2)
b1 = 100 * tk["B1_popularity"]["all"]["top10"] / n
fig.add_vline(x=b1, line=dict(color="#888888", width=1, dash="dot"), row=1, col=2)
fig.add_annotation(x=b1, y=-0.75, text="Gene frequency only", showarrow=False, xanchor="left", xshift=4,
                   font=dict(family="Arial", size=12, color=K), row=1, col=2)
fig.update_yaxes(tickvals=list(range(len(cond))), ticktext=[c for c, _ in cond], autorange="reversed", row=1, col=2)
fig.update_xaxes(title_text="Fetuses (%)", range=[0, 60], row=1, col=2)
save(style(fig, 1100, 460), "figure3")

# Figure 4: clinical simulation, causal gene ranked first
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                    subplot_titles=("a  Fetuses reported from 1 July 2026 (n=66)", "b  Largest earlier cohort (n=185)"))
rows = ["Exomiser with variants", "LLM re-ranking", "Exomiser and LLM combined"]
for col, src in [(1, "v1p"), (2, "v1")]:
    v0 = D[src][f"{src}_rerank_opus-5-5"]; nn = v0["n"]; v0 = v0.get("summary", v0)
    x, l, h = wilson(v0["exomiser"]["top1"], nn)
    fig.add_trace(go.Scatter(x=[x], y=[0], mode="markers", marker=dict(symbol="diamond", size=10, color="#555555"),
                             error_x=dict(type="data", symmetric=False, array=[h - x], arrayminus=[x - l], color="#555555",
                                          thickness=1.2, width=0), name="Exomiser", showlegend=(col == 1)), row=1, col=col)
    for m, colour, lab, off in [("haiku-5-5", GREEN, "Claude Haiku 5.5", 0.2), ("sonnet-5-5", RED, "Claude Sonnet 5.5", 0.0),
                                ("opus-5-5", PURPLE, "Claude Opus 5.5", -0.2)]:
        v = D[src][f"{src}_rerank_{m}"]; v = v.get("summary", v)
        vals = [v["llm_rerank"]["top1"], v["fusion"]["top1"]]
        xs, lo, hi = zip(*[wilson(x, nn) for x in vals])
        fig.add_trace(go.Scatter(x=xs, y=[i + 1 + off for i in range(2)], mode="markers",
                                 marker=dict(symbol="diamond", size=10, color=colour),
                                 error_x=dict(type="data", symmetric=False, array=[h - x for h, x in zip(hi, xs)],
                                              arrayminus=[x - l for x, l in zip(xs, lo)], color=colour, thickness=1.2, width=0),
                                 name=lab, showlegend=(col == 1)), row=1, col=col)
fig.update_yaxes(tickvals=[0, 1, 2], ticktext=rows, autorange="reversed", row=1, col=1)
for c in (1, 2):
    fig.update_xaxes(title_text="Causal gene ranked first (%)", range=[0, 100], row=1, col=c)
fig = style(fig, 1000, 400); fig.update_layout(legend=dict(y=-0.28), margin=dict(b=90))
save(fig, "figure4")
print("figures written to", FIG)
