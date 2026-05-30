import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator, FuncFormatter

# Carregando os dados e ajustando o visual geral dos gráficos do matplotlib
df = pd.read_csv("mercado_entretenimento.csv")

plt.style.use('dark_background')
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.facecolor': '#1e293b',
    'figure.facecolor': '#1e293b',
    'text.color': '#f8fafc',
    'axes.labelcolor': '#94a3b8',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'grid.color': '#334155',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.edgecolor': '#334155',
    'axes.titleweight': 'bold',
    'axes.titlepad': 18,
    'axes.titlesize': 15,
})

def fig_to_uri(fig):
    # Converte a figura gerada pro formato base64 pra gente conseguir jogar no Dash
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='#1e293b')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('ascii')
    plt.close(fig)
    return f"data:image/png;base64,{encoded}"

# Funções para criar os gráficos que não mudam
def criar_grafico_parte1(df):
    generos_alvo = ["Ação", "Terror", "Drama", "Comédia"]
    Genero_por_NomeItem = df[df["Nome_Item"].isin(generos_alvo)]
    receita_total_porAno = Genero_por_NomeItem.groupby(["Ano", "Nome_Item"], as_index=False)["Receita_Bilhoes"].sum()

    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor='#1e293b')
    ax.set_facecolor('#0f172a')

    cores_generos = {
        "Ação": "#E50914",
        "Terror": "#CBD5E1", 
        "Drama": "#2E7D32",
        "Comédia": "#F57C00",
    }

    sns.lineplot(
        data=receita_total_porAno, x="Ano", y="Receita_Bilhoes", hue="Nome_Item",
        palette=cores_generos, errorbar=None, linewidth=3.5, ax=ax
    )

    ax.set_title("O Impacto da Covid-19 e a Guerra dos Streamings na Bilheteria: Queda generalizada em todos os gêneros",
                 fontsize=14, fontweight='bold', loc='left', pad=25, color='#f8fafc')

    ax.axvline(x=2020, color='#64748b', linestyle='--', linewidth=2.0)
    ax.text(2020.1, receita_total_porAno['Receita_Bilhoes'].max() * 0.8,
             "2020: Começo da Pandemia\nFechamento dos cinemas",
             color='#94a3b8', fontsize=11.5, fontweight='bold')

    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')
    ax.grid(axis='y', linestyle='-', alpha=0.2, color='#334155')

    ax.set_xlabel("Ano", fontsize=12, labelpad=10, color='#94a3b8')
    ax.set_ylabel("Receita (em Bilhões)", fontsize=12, labelpad=10, color='#94a3b8')
    ax.tick_params(colors='#94a3b8')

    ax.legend(title="Gêneros", bbox_to_anchor=(0.5, -0.15), loc="upper center",
              ncol=4, frameon=False, fontsize=13, title_fontsize=15, labelcolor='#f8fafc')
    
    return fig_to_uri(fig)


def criar_grid_contexto_p3(df):
    BRAND_COLORS = {
        'Netflix':     '#e50914',
        'Disney+':     '#3b82f6',
        'Prime Video': '#06b6d4',
    }
    df_stream = df[df['Tipo'] == 'Streaming'].copy()
    churn_df = df_stream.groupby(['Ano', 'Nome_Item'])['Churn_Rate'].mean().reset_index()
    df_2025 = df_stream[df_stream['Ano'] == 2025]
    market_share = df_2025.groupby('Nome_Item')['Receita_Bilhoes'].sum().reset_index()
    total_ms = market_share['Receita_Bilhoes'].sum()

    fig = plt.figure(figsize=(15, 10), facecolor='#1e293b')
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.4, 1], hspace=0.55, wspace=0.35)

    ax_top  = fig.add_subplot(gs[0, :])
    ax_net  = fig.add_subplot(gs[1, 0])
    ax_dis  = fig.add_subplot(gs[1, 1])
    ax_pri  = fig.add_subplot(gs[1, 2])

    for ax in [ax_top, ax_net, ax_dis, ax_pri]:
        ax.set_facecolor('#0f172a')

    for platform, color in BRAND_COLORS.items():
        data = churn_df[churn_df['Nome_Item'] == platform].sort_values('Ano')
        ax_top.plot(data['Ano'], data['Churn_Rate'], label=platform, color=color, linewidth=3, marker='o')
        last = data.iloc[-1]
        ax_top.annotate(f" {last['Churn_Rate']:.1f}%", xy=(last['Ano'], last['Churn_Rate']), fontweight='bold', color=color, va='center')

    ax_top.set_title("Evolução Global do Churn Rate por Plataforma (2010–2025)")
    ax_top.grid(axis='y', linestyle='--', alpha=0.25)
    ax_top.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax_top.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.1f}%"))

    ax_top.axvspan(2020, 2021, alpha=0.08, color='#fbbf24')
    ax_top.annotate("Pós-pandemia:\nGuerras de cancelamento\naceleraram o Churn", 
                    xy=(2020.5, churn_df[churn_df['Ano'] == 2021]['Churn_Rate'].max()),
                    xytext=(2016.2, churn_df['Churn_Rate'].max() - 0.3),
                    arrowprops=dict(facecolor='#fbbf24', shrink=0.05, width=1.5, headwidth=7),
                    color='#fef3c7', weight='bold', bbox=dict(boxstyle="round,pad=0.5", fc="#1c1917", ec="#fbbf24", lw=1.5))

    def draw_donut(ax, platform):
        row = market_share[market_share['Nome_Item'] == platform]
        val = row['Receita_Bilhoes'].values[0] if len(row) else 0
        pct = val / total_ms * 100
        color = BRAND_COLORS.get(platform, '#64748b')
        ax.pie([pct, 100 - pct], colors=[color, '#334155'], startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor='#1e293b', linewidth=3))
        ax.text(0, 0.08, f"{pct:.1f}%", ha='center', va='center', fontsize=22, fontweight='bold', color=color)
        ax.text(0, -0.22, f"US$ {val:.1f} B", ha='center', va='center', fontsize=11, color='#94a3b8')
        ax.set_title(f"{platform}\nMarket Share — 2025", color='#f8fafc', pad=14)

    draw_donut(ax_net, 'Netflix')
    draw_donut(ax_dis, 'Disney+')
    draw_donut(ax_pri, 'Prime Video')

    fig.suptitle("Grid de Contexto — Macro & Micro View  |  Streaming 2010–2025", fontsize=20, fontweight='bold', color='#f8fafc', y=0.96)
    return fig_to_uri(fig)

# Já deixa os gráficos gerados de antemão
imagem_parte1_base64 = criar_grafico_parte1(df)
imagem_grid_base64 = criar_grid_contexto_p3(df)

# Criação do app Dash e do layout da página
app = dash.Dash(__name__)
app.title = "Mercado de Entretenimento - Dashboard Integrado"

regioes = df['Regiao'].dropna().unique()

app.layout = html.Div(style={'backgroundColor': '#0f172a', 'padding': '30px', 'fontFamily': 'Arial', 'minHeight': '100vh'}, children=[
    
    html.H1("Dashboard Integrado - Mercado de Entretenimento", style={'color': '#f8fafc', 'textAlign': 'center', 'marginBottom': '40px'}),
    
    # Primeiro bloco: impacto geral na bilheteria
    html.Div([
        html.H2("Parte 1: Impacto da Pandemia e Streaming na Bilheteria", style={'color': '#f8fafc', 'marginBottom': '20px'}),
        html.Img(
            src=imagem_parte1_base64,
            style={'width': '100%', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)', 'backgroundColor': '#1e293b', 'padding': '10px'}
        )
    ], style={'marginBottom': '50px', 'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '12px'}),
    
    # Segundo bloco: gráfico interativo com filtros
    html.Div([
        html.H2("Parte 2: Ponto de Virada - Cinema vs Streaming", style={'color': '#f8fafc', 'marginBottom': '20px', 'textAlign': 'center'}),
        
        html.Div([
            html.Label("SELECIONE A REGIÃO:", style={'fontWeight': '600', 'marginRight': '15px', 'color': '#94A3B8'}),
            dcc.Dropdown(
                id='regiao-dropdown',
                options=[{'label': r, 'value': r} for r in regioes],
                value=regioes[0],
                clearable=False,
                style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle', 'color': '#000'}
            )
        ], style={'textAlign': 'center', 'paddingBottom': '20px'}),
        
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px', 'justifyContent': 'center'},
            children=[
                html.Div([html.P("Ano da Virada", style={'color': '#94A3B8', 'fontWeight': '600'}), html.H2(id='virada-ano', style={'color': '#FBBF24', 'margin': '0'})], style={'backgroundColor': '#0f172a', 'borderRadius': '12px', 'padding': '20px', 'textAlign': 'center', 'flex': '1'}),
                html.Div([html.P("Pico Cinema", style={'color': '#94A3B8', 'fontWeight': '600'}), html.H2(id='pico-cinema', style={'color': '#F43F5E', 'margin': '0'})], style={'backgroundColor': '#0f172a', 'borderRadius': '12px', 'padding': '20px', 'textAlign': 'center', 'flex': '1'}),
                html.Div([html.P("Pico Streaming", style={'color': '#94A3B8', 'fontWeight': '600'}), html.H2(id='pico-streaming', style={'color': '#3B82F6', 'margin': '0'})], style={'backgroundColor': '#0f172a', 'borderRadius': '12px', 'padding': '20px', 'textAlign': 'center', 'flex': '1'}),
            ]
        ),
        
        html.Img(id='plot-imagem-p2', style={'width': '100%', 'height': 'auto', 'borderRadius': '8px', 'backgroundColor': '#0f172a', 'padding': '10px'})
        
    ], style={'marginBottom': '50px', 'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '12px'}),
    
    # Terceiro bloco: os pequenos gráficos de contexto
    html.Div([
        html.H2("Parte 3: O Grid de Contexto (Macro & Micro View - Streaming)", style={'color': '#f8fafc', 'marginBottom': '20px'}),
        html.Img(
            src=imagem_grid_base64,
            style={'width': '100%', 'height': 'auto', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)', 'backgroundColor': '#1e293b', 'padding': '10px'}
        )
    ], style={'marginBottom': '50px', 'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '12px'})
])

# Callback para fazer o dropdown da região atualizar o gráfico e os números
@app.callback(
    [
        Output('plot-imagem-p2', 'src'),
        Output('virada-ano', 'children'),
        Output('pico-cinema', 'children'),
        Output('pico-streaming', 'children')
    ],
    Input('regiao-dropdown', 'value')
)
def update_graph_p2(regiao):
    df_regiao = df[df['Regiao'] == regiao]
    
    # Separa as receitas de cinema e streaming e soma por ano
    df_cinema = df_regiao[df_regiao['Tipo'] == 'Cinema'].groupby('Ano')['Receita_Bilhoes'].sum().reset_index()
    df_streaming = df_regiao[df_regiao['Tipo'] == 'Streaming'].groupby('Ano')['Receita_Bilhoes'].sum().reset_index()
    
    df_merged = pd.merge(df_cinema, df_streaming, on='Ano', suffixes=('_cinema', '_streaming')).sort_values('Ano')
    
    anos = df_merged['Ano'].values
    rev_cinema = df_merged['Receita_Bilhoes_cinema'].values
    rev_streaming = df_merged['Receita_Bilhoes_streaming'].values
    
    peak_cinema = df_cinema['Receita_Bilhoes'].max() if not df_cinema.empty else 0.0
    peak_streaming = df_streaming['Receita_Bilhoes'].max() if not df_streaming.empty else 0.0
    
    pico_cinema_text = f"US$ {peak_cinema:.2f} Bi"
    pico_streaming_text = f"US$ {peak_streaming:.2f} Bi"
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150, facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    
    ax.plot(anos, rev_cinema, label='Cinema', color='#F43F5E', linewidth=3, marker='o', markersize=6, markerfacecolor='#F43F5E', markeredgecolor='#0f172a', markeredgewidth=1.5)
    ax.plot(anos, rev_streaming, label='Streaming', color='#3B82F6', linewidth=3, marker='o', markersize=6, markerfacecolor='#3B82F6', markeredgecolor='#0f172a', markeredgewidth=1.5)
    
    intersection_x = None
    intersection_y = None
    intersection_year_text = None
    
    # Encontra o ponto exato onde a linha de streaming passa a do cinema
    for i in range(len(anos) - 1):
        x1, x2 = anos[i], anos[i+1]
        c1, c2 = rev_cinema[i], rev_cinema[i+1]
        s1, s2 = rev_streaming[i], rev_streaming[i+1]
        
        if s1 <= c1 and s2 > c2:
            diff1 = c1 - s1
            diff2 = s2 - c2
            if diff1 + diff2 > 0:
                t = diff1 / (diff1 + diff2)
                intersection_x = x1 + t * (x2 - x1)
                intersection_y = c1 + t * (c2 - c1)
                intersection_year_text = str(int(round(intersection_x)))
                break
                
    if intersection_x is not None:
        ax.plot(intersection_x, intersection_y, marker='o', markersize=12, color='#FBBF24', zorder=5, markeredgecolor='#0f172a', markeredgewidth=2)
        
        text_content = f"Em {intersection_year_text}, o Streaming tornou-se\nna força dominante nesta região"
        
        if intersection_x > anos.mean():
            xytext_pos = (0.05, 0.95)
            ha_pos = 'left'
            connection = "arc3,rad=-0.1"
        else:
            xytext_pos = (0.95, 0.95)
            ha_pos = 'right'
            connection = "arc3,rad=0.1"
            
        ax.annotate(
            text_content,
            xy=(intersection_x, intersection_y),
            xytext=xytext_pos,
            textcoords='axes fraction',
            arrowprops=dict(arrowstyle="->", color='#FBBF24', lw=1.5, connectionstyle=connection),
            bbox=dict(boxstyle="round,pad=0.6", fc="#1E293B", ec="#FBBF24", lw=1.2),
            color='#F8FAFC',
            fontsize=10,
            fontweight='600',
            ha=ha_pos,
            va='top'
        )

    ax.set_xlabel('Ano', color='#94A3B8', fontsize=11, labelpad=12, fontweight='600')
    ax.set_ylabel('Receita (Bilhões US$)', color='#94A3B8', fontsize=11, labelpad=12, fontweight='600')
    ax.tick_params(colors='#64748B', labelsize=10)
    ax.set_xticks(anos)
    
    for spine in ax.spines.values():
        spine.set_color('#334155')
        spine.set_linewidth(1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC', fontsize=10, framealpha=0.9)
    ax.grid(True, linestyle='--', alpha=0.5, color='#334155')
    
    intersection_ret = intersection_year_text if intersection_year_text else "N/A"
    return fig_to_uri(fig), intersection_ret, pico_cinema_text, pico_streaming_text

# Roda o app localmente pra gente ver no navegador
if __name__ == '__main__':
    app.run(debug=True)