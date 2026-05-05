import dash
from dash import html, dcc, dash_table, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('yoruba_platform.db')

# ========== LOAD ALL QUERIES ==========
q1 = pd.read_sql_query("""
    SELECT u.location AS Location,
        COUNT(DISTINCT u.user_id) AS "Total Learners",
        COUNT(DISTINCT up.lesson_id) AS "Lessons Accessed",
        ROUND(AVG(up.score_percentage), 1) AS "Avg Score (%)",
        ROUND(AVG(up.time_spent_mins), 1) AS "Avg Time (mins)"
    FROM users u JOIN user_progress up ON u.user_id = up.user_id
    WHERE u.role = 'learner' GROUP BY u.location ORDER BY "Avg Score (%)" DESC
""", conn)

q2 = pd.read_sql_query("""
    SELECT CASE 
            WHEN (2026 - CAST(strftime('%Y', u.date_of_birth) AS INTEGER)) < 25 THEN '18-24'
            WHEN (2026 - CAST(strftime('%Y', u.date_of_birth) AS INTEGER)) < 35 THEN '25-34'
            WHEN (2026 - CAST(strftime('%Y', u.date_of_birth) AS INTEGER)) < 50 THEN '35-49'
            ELSE '50+' END AS "Age Group",
        COUNT(DISTINCT u.user_id) AS "Total Learners",
        COUNT(up.progress_id) AS "Lesson Attempts",
        ROUND(AVG(up.score_percentage), 1) AS "Avg Score (%)",
        ROUND(AVG(up.time_spent_mins), 1) AS "Avg Time (mins)"
    FROM users u JOIN user_progress up ON u.user_id = up.user_id
    WHERE u.role = 'learner' AND u.date_of_birth IS NOT NULL
    GROUP BY "Age Group" ORDER BY "Age Group"
""", conn)

q3 = pd.read_sql_query("""
    SELECT c.category_name AS Category,
        COUNT(DISTINCT l.lesson_id) AS "Total Lessons",
        COUNT(up.progress_id) AS "Total Attempts",
        COUNT(CASE WHEN up.status = 'completed' THEN 1 END) AS Completions,
        ROUND(100.0 * COUNT(CASE WHEN up.status = 'completed' THEN 1 END) / COUNT(up.progress_id), 1) AS "Completion Rate (%)",
        ROUND(AVG(qr.score_percentage), 1) AS "Avg Quiz Score (%)"
    FROM categories c JOIN lessons l ON c.category_id = l.category_id
    LEFT JOIN user_progress up ON l.lesson_id = up.lesson_id
    LEFT JOIN quiz_results qr ON l.lesson_id = qr.lesson_id AND up.user_id = qr.user_id
    GROUP BY c.category_name ORDER BY "Completion Rate (%)" DESC
""", conn)

q4 = pd.read_sql_query("""
    SELECT l.difficulty_level AS Difficulty,
        COUNT(up.progress_id) AS "Total Attempts",
        COUNT(CASE WHEN up.status = 'completed' THEN 1 END) AS Completions,
        COUNT(CASE WHEN up.status = 'in_progress' THEN 1 END) AS "In Progress",
        ROUND(100.0 * COUNT(CASE WHEN up.status = 'completed' THEN 1 END) / COUNT(up.progress_id), 1) AS "Completion Rate (%)",
        ROUND(100.0 * (COUNT(up.progress_id) - COUNT(CASE WHEN up.status = 'completed' THEN 1 END)) / COUNT(up.progress_id), 1) AS "Drop-off Rate (%)"
    FROM lessons l JOIN user_progress up ON l.lesson_id = up.lesson_id
    GROUP BY l.difficulty_level
    ORDER BY CASE l.difficulty_level WHEN 'beginner' THEN 1 WHEN 'intermediate' THEN 2 WHEN 'advanced' THEN 3 END
""", conn)

q5 = pd.read_sql_query("""
    SELECT cc.content_type AS "Content Type",
        COUNT(cc.cultural_id) AS "Total Contributions",
        COUNT(CASE WHEN cc.approved = 1 THEN 1 END) AS Approved,
        COUNT(CASE WHEN cc.approved = 0 THEN 1 END) AS Pending
    FROM cultural_content cc JOIN users u ON cc.contributed_by = u.user_id
    GROUP BY cc.content_type ORDER BY "Total Contributions" DESC
""", conn)

q6 = pd.read_sql_query("""
    SELECT u.display_name AS "Display Name", u.location AS Location, u.proficiency_level AS Proficiency,
        COUNT(DISTINCT cp.post_id) AS "Discussion Posts",
        COUNT(DISTINCT cc.cultural_id) AS "Cultural Contributions",
        COUNT(DISTINCT f.feedback_id) AS "Feedback Given",
        (COUNT(DISTINCT cp.post_id) + COUNT(DISTINCT cc.cultural_id) + COUNT(DISTINCT f.feedback_id)) AS "Engagement Score"
    FROM users u
    LEFT JOIN community_posts cp ON u.user_id = cp.user_id
    LEFT JOIN cultural_content cc ON u.user_id = cc.contributed_by
    LEFT JOIN feedback f ON u.user_id = f.user_id
    WHERE u.role IN ('learner', 'tutor', 'elder')
    GROUP BY u.user_id HAVING "Engagement Score" > 0
    ORDER BY "Engagement Score" DESC LIMIT 10
""", conn)

q7 = pd.read_sql_query("""
    SELECT u.display_name AS Learner, u.proficiency_level AS Proficiency,
        up.time_spent_mins AS "Time Spent (mins)",
        qr.score_percentage AS "Quiz Score (%)", l.title AS Lesson
    FROM user_progress up
    JOIN users u ON up.user_id = u.user_id
    JOIN quiz_results qr ON up.user_id = qr.user_id AND up.lesson_id = qr.lesson_id
    JOIN lessons l ON up.lesson_id = l.lesson_id
    WHERE up.status = 'completed' ORDER BY up.time_spent_mins
""", conn)

q8 = pd.read_sql_query("""
    SELECT u.proficiency_level AS "Proficiency Level",
        COUNT(DISTINCT u.user_id) AS "Total Learners",
        COUNT(up.progress_id) AS "Total Attempts",
        COUNT(CASE WHEN up.status = 'completed' THEN 1 END) AS Completions,
        ROUND(100.0 * COUNT(CASE WHEN up.status = 'completed' THEN 1 END) / COUNT(up.progress_id), 1) AS "Completion Rate (%)",
        ROUND(AVG(up.score_percentage), 1) AS "Avg Score (%)",
        ROUND(AVG(up.time_spent_mins), 1) AS "Avg Time (mins)"
    FROM users u JOIN user_progress up ON u.user_id = up.user_id
    WHERE u.role = 'learner' AND u.proficiency_level IS NOT NULL
    GROUP BY u.proficiency_level
    ORDER BY CASE u.proficiency_level WHEN 'beginner' THEN 1 WHEN 'intermediate' THEN 2 WHEN 'advanced' THEN 3 END
""", conn)

# KPI metrics
total_learners = pd.read_sql_query("SELECT COUNT(*) as c FROM users WHERE role='learner'", conn).iloc[0]['c']
lessons_completed = pd.read_sql_query("SELECT COUNT(*) as c FROM user_progress WHERE status='completed'", conn).iloc[0]['c']
avg_score = pd.read_sql_query("SELECT ROUND(AVG(score_percentage),1) as c FROM user_progress WHERE score_percentage IS NOT NULL", conn).iloc[0]['c']
cultural_items = pd.read_sql_query("SELECT COUNT(*) as c FROM cultural_content", conn).iloc[0]['c']
community_posts_count = pd.read_sql_query("SELECT COUNT(*) as c FROM community_posts", conn).iloc[0]['c']

conn.close()

# ========== STYLING ==========
FONT = '"EB Garamond", Georgia, serif'

def style_fig(fig, xtitle='', ytitle=''):
    fig.update_layout(
        font_family=FONT,
        xaxis_title=dict(text=f'<b>{xtitle}</b>', font=dict(size=14)),
        yaxis_title=dict(text=f'<b>{ytitle}</b>', font=dict(size=14)),
        hoverlabel=dict(font_size=12, font_family=FONT),
        plot_bgcolor='#FAFAFA', paper_bgcolor='#FAFAFA',
        legend_title=dict(text='<b>Key</b>', font=dict(size=14)),
        legend_font=dict(size=11), clickmode='event+select', hovermode='closest'
    )
    # Fix hover for bar charts - show clean labels not raw variable names
    for trace in fig.data:
        if hasattr(trace, 'type') and trace.type == 'bar':
            name = trace.name if trace.name else ''
            trace.hovertemplate = f'<b>%{{x}}</b><br>{name}: %{{y}}<extra></extra>'
    return fig

def calc_stats(data, stat, label):
    data = data.dropna()
    if len(data) == 0:
        return "N/A"
    if stat == 'Mean': return f"{data.mean():.1f}"
    elif stat == 'Median': return f"{data.median():.1f}"
    elif stat == 'Range': return f"{data.min():.0f} – {data.max():.0f}"
    elif stat == 'IQR': return f"{data.quantile(0.25):.0f} – {data.quantile(0.75):.0f}"
    return "N/A"

# ========== STATIC FIGURES ==========
# Section 4: Dual chart
fig4_stacked = go.Figure()
fig4_stacked.add_trace(go.Bar(name='Completed', x=q4['Difficulty'], y=q4['Completion Rate (%)'],
                               marker_color='#27AE60', hovertemplate='<b>%{x}</b><br>Completed: %{y}%<extra></extra>'))
fig4_stacked.add_trace(go.Bar(name='Dropped', x=q4['Difficulty'], y=q4['Drop-off Rate (%)'],
                               marker_color='#E74C3C', hovertemplate='<b>%{x}</b><br>Dropped: %{y}%<extra></extra>'))
fig4_stacked.update_layout(barmode='stack', font_family=FONT,
    xaxis_title=dict(text='<b>Difficulty Level</b>', font=dict(size=14)),
    yaxis_title=dict(text='<b>Percentage (%)</b>', font=dict(size=14)),
    legend_title=dict(text='<b>Key</b>', font=dict(size=14)),
    plot_bgcolor='#FAFAFA', paper_bgcolor='#FAFAFA')

# Funnel: beginner at top, advanced at bottom
q4_funnel = q4.copy()
q4_funnel['Difficulty'] = pd.Categorical(q4_funnel['Difficulty'], categories=['advanced', 'intermediate', 'beginner'], ordered=True)
q4_funnel = q4_funnel.sort_values('Difficulty')
fig4_funnel = px.bar(q4_funnel, x='Total Attempts', y='Difficulty', orientation='h',
                     color_discrete_sequence=['#3498DB'])
fig4_funnel.update_layout(font_family=FONT, showlegend=False,
    xaxis_title=dict(text='<b>Volume of Learners</b>', font=dict(size=14)),
    yaxis_title=dict(text='<b>Difficulty Level</b>', font=dict(size=14)),
    plot_bgcolor='#FAFAFA', paper_bgcolor='#FAFAFA')
fig4_funnel.update_traces(hovertemplate='<b>%{y}</b><br>Learners: %{x}<extra></extra>')

# Section 5
fig5 = px.pie(q5, values='Total Contributions', names='Content Type',
              color_discrete_sequence=px.colors.qualitative.Set3)
fig5.update_layout(font_family=FONT, legend_title=dict(text='<b>Key</b>', font=dict(size=14)))
fig5.update_traces(hovertemplate='<b>%{label}</b><br>Contributions: %{value}<br>Percentage: %{percent}<extra></extra>')

# ========== REUSABLE COMPONENTS ==========
def add_total_row(df):
    """Add a TOTAL row for numeric sum columns, leave averages/percentages blank"""
    total_row = {}
    for col in df.columns:
        if col in df.select_dtypes(include=['number']).columns:
            col_lower = col.lower()
            # Sum countable columns, leave rates/averages/percentages blank
            if any(word in col_lower for word in ['avg', 'rate', 'score', 'time', '%']):
                total_row[col] = ''
            else:
                total_row[col] = df[col].sum()
        else:
            total_row[col] = 'TOTAL' if df.columns.get_loc(col) == 0 else ''
    return pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

def make_table(df, table_id):
    df_with_total = add_total_row(df)
    return dash_table.DataTable(
        id=table_id, data=df_with_total.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_with_total.columns],
        sort_action='native', filter_action='native', export_format='csv',
        style_table={'marginTop': '10px', 'overflowX': 'auto'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0', 'fontFamily': FONT},
        style_cell={'textAlign': 'center', 'padding': '8px', 'fontFamily': FONT, 'fontSize': '13px'},
        style_data_conditional=[{'if': {'filter_query': '{' + df.columns[0] + '} = "TOTAL"'}, 'fontWeight': 'bold', 'backgroundColor': '#e8f4e8'}],
        page_size=20)

def kpi_card(title, value, color='#2E86AB'):
    return html.Div(style={
        'backgroundColor': '#fff', 'padding': '20px', 'borderRadius': '8px',
        'border': f'2px solid {color}', 'textAlign': 'center', 'minWidth': '150px'
    }, children=[
        html.P(title, style={'fontSize': '0.85em', 'color': '#555', 'marginBottom': '5px', 'fontWeight': '600'}),
        html.H2(str(value), style={'color': color, 'margin': '0', 'fontSize': '2em'})
    ])

def stats_panel(panel_id):
    return html.Div(id=panel_id, style={
        'display': 'flex', 'justifyContent': 'center', 'gap': '30px', 'marginBottom': '15px',
        'backgroundColor': '#fff', 'padding': '12px 20px', 'borderRadius': '6px', 'border': '1px solid #e0e0e0'
    })

def analysis_brief(brief_id):
    return html.Details([
        html.Summary('Analyst Notes', style={'cursor': 'pointer', 'color': '#A23B72', 'fontWeight': '600', 'marginTop': '8px'}),
        dcc.Textarea(id=brief_id, placeholder='Write your analytical observations here (max 1000 characters)...',
                     maxLength=1000,
                     style={'width': '100%', 'height': '80px', 'fontSize': '0.9em', 'fontFamily': FONT,
                            'padding': '10px', 'borderRadius': '6px', 'border': '1px solid #e0e0e0',
                            'marginTop': '8px', 'resize': 'vertical'})
    ])

# ========== DASH APP ==========
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style={'fontFamily': FONT, 'maxWidth': '1200px', 'margin': '0 auto', 'padding': '30px', 'backgroundColor': '#FAFAFA'}, children=[

    html.Link(href='https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700&display=swap', rel='stylesheet'),

    # Header
    html.H1('Yoruba Learning Platform: Analytics Dashboard',
            style={'textAlign': 'center', 'color': '#1a1a1a', 'fontSize': '2.4em', 'fontWeight': '700', 'marginBottom': '5px'}),
    html.P(f"Last updated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
           style={'textAlign': 'center', 'color': '#999', 'fontSize': '0.8em', 'marginBottom': '25px'}),

    # KPI Cards
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'flexWrap': 'wrap', 'marginBottom': '30px'}, children=[
        kpi_card('Active Learners', total_learners, '#2E86AB'),
        kpi_card('Lessons Completed', lessons_completed, '#27AE60'),
        kpi_card('Avg Score (%)', avg_score, '#F18F01'),
        kpi_card('Cultural Items', cultural_items, '#A23B72'),
        kpi_card('Community Posts', community_posts_count, '#C73E1D'),
    ]),

    # Summary
    html.Div(style={'backgroundColor': '#fff', 'padding': '25px', 'borderRadius': '8px', 'marginBottom': '35px', 'border': '1px solid #e0e0e0'}, children=[
        html.P("This interactive analytics dashboard presents Business Intelligence insights from the Yoruba Diaspora Learning Platform. "
               "It visualises learner engagement, lesson effectiveness, cultural contributions and community participation "
               "across UK diaspora communities — enabling data-driven decisions for platform development and cultural preservation.",
               style={'fontSize': '1.05em', 'lineHeight': '1.7', 'marginBottom': '18px'}),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '15px'}, children=[
            html.Div([html.P(html.Strong("Data Source"), style={'marginBottom': '5px'}),
                html.P("~2000 records across 9 SQLite tables. Synthetic user data + authentic Yoruba linguistic content.", style={'fontSize': '0.9em', 'color': '#555'})]),
            html.Div([html.P(html.Strong("How to Interact"), style={'marginBottom': '5px'}),
                html.P("Hover for details. Click legend to isolate. Drag to zoom, double-click to reset. Use dropdowns to filter. Tables sortable, filterable, exportable to CSV.", style={'fontSize': '0.9em', 'color': '#555'})]),
        ])
    ]),

    # ===== SECTION 1: LOCATION =====
    html.H3('Learner Engagement by Location', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Compares platform activity across UK diaspora communities. Identifies geographic engagement hotspots for targeted outreach.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '10px', 'flexWrap': 'wrap'}, children=[
        html.Div([html.Label('Location:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='location-filter', options=[{'label': 'All', 'value': 'All'}] + [{'label': l, 'value': l} for l in q1['Location'].unique()],
                value='All', clearable=False, style={'width': '200px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-1', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-1'),
    dcc.Graph(id='location-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q1, 'table-1')]),
    analysis_brief('brief-1'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 2: AGE GROUP =====
    html.H3('Learner Engagement by Age Group', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Segments learners by age to reveal which demographics engage most. Supports tailored content for underrepresented groups.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '10px', 'flexWrap': 'wrap'}, children=[
        html.Div([html.Label('Age Group:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='age-filter', options=[{'label': 'All', 'value': 'All'}] + [{'label': a, 'value': a} for a in q2['Age Group'].unique()],
                value='All', clearable=False, style={'width': '200px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-2', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-2'),
    dcc.Graph(id='age-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q2, 'table-2')]),
    analysis_brief('brief-2'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 3: CATEGORY =====
    html.H3('Lesson Effectiveness by Category', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Evaluates completion and quiz scores across categories. Identifies areas requiring strategic content redesign.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '10px', 'flexWrap': 'wrap'}, children=[
        html.Div([html.Label('Category:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='category-filter', options=[{'label': 'All', 'value': 'All'}] + [{'label': c, 'value': c} for c in q3['Category'].unique()],
                value='All', clearable=False, style={'width': '200px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-3', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-3'),
    dcc.Graph(id='category-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q3, 'table-3')]),
    analysis_brief('brief-3'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 4: DIFFICULTY (DUAL CHART) =====
    html.H3('Lesson Completion by Difficulty Level', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Stacked bar shows relative completion/drop-off rates. Funnel visualises absolute attrition volume from beginner to advanced.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
        dcc.Graph(figure=fig4_stacked, config={'displayModeBar': True, 'displaylogo': False}),
        dcc.Graph(figure=fig4_funnel, config={'displayModeBar': True, 'displaylogo': False}),
    ]),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q4, 'table-4')]),
    analysis_brief('brief-4'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 5: CULTURAL CONTENT =====
    html.H3('Cultural Content Contributions', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Analyses community contributions by type. Guides content strategy and moderation priorities.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    dcc.Graph(figure=fig5, config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q5, 'table-5')]),
    analysis_brief('brief-5'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 6: ENGAGEMENT LEADERS =====
    html.H3('Community Engagement Leaders', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Composite score from posts, contributions and feedback. Identifies champions for mentoring and recognition.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}, children=[
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-6', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-6'),
    dcc.Graph(id='engagement-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q6, 'table-6')]),
    analysis_brief('brief-6'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 7: SCATTER =====
    html.H3('Time Spent vs Quiz Performance', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Tests correlation between study duration and outcomes. OLS trendline shows predictive relationship for personalised pace recommendations.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '10px', 'flexWrap': 'wrap'}, children=[
        html.Div([html.Label('Proficiency:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='proficiency-filter', options=[{'label': 'All', 'value': 'All'}] + [{'label': p, 'value': p} for p in q7['Proficiency'].dropna().unique()],
                value='All', clearable=False, style={'width': '200px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-7', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-7'),
    dcc.Graph(id='scatter-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        dash_table.DataTable(id='scatter-table', sort_action='native', filter_action='native', export_format='csv',
            style_table={'marginTop': '10px', 'overflowX': 'auto'}, style_header={'fontWeight': 'bold', 'backgroundColor': '#f0f0f0'},
            style_cell={'textAlign': 'center', 'padding': '8px', 'fontFamily': FONT, 'fontSize': '13px'}, page_size=15)]),
    analysis_brief('brief-7'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 8: PROFICIENCY =====
    html.H3('Proficiency Level Progression', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Compares metrics across proficiency levels. Supports adaptive content-difficulty algorithms.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 15px auto'}),
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}, children=[
        html.Div([html.Label('Statistic:', style={'fontWeight': '600', 'fontSize': '0.9em', 'marginRight': '10px'}),
            dcc.Dropdown(id='stat-8', options=[{'label': s, 'value': s} for s in ['Mean', 'Median', 'Range', 'IQR']],
                value='Mean', clearable=False, style={'width': '150px', 'fontFamily': FONT})], style={'display': 'flex', 'alignItems': 'center'}),
    ]),
    stats_panel('stats-panel-8'),
    dcc.Graph(id='proficiency-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Details([html.Summary('View Data Table · Export CSV', style={'cursor': 'pointer', 'color': '#2E86AB', 'fontWeight': '600', 'marginTop': '10px'}),
        make_table(q8, 'table-8')]),
    analysis_brief('brief-8'),
    html.Div(style={'marginBottom': '50px'}),

    # ===== SECTION 9: MONTE CARLO SIMULATION =====
    html.H3('Projected Learner Growth: Monte Carlo Simulation', style={'textAlign': 'center', 'fontWeight': '700', 'marginTop': '40px', 'fontSize': '1.4em'}),
    html.P("Runs 1,000 simulated growth scenarios over 12 quarters using ±6.2% variance derived from Duolingo's quarterly MAU standard deviation (Statista, 2026). Demonstrates prescriptive analytics for strategic platform planning.",
           style={'textAlign': 'center', 'color': '#555', 'fontSize': '0.95em', 'maxWidth': '800px', 'margin': '0 auto 5px auto'}),
    html.A("Source: Statista — Duolingo Quarterly MAU (2020-2025)", href="https://www.statista.com/statistics/1309610/duolingo-quarterly-mau/", target="_blank",
           style={'display': 'block', 'textAlign': 'center', 'color': '#2E86AB', 'fontSize': '0.8em', 'marginBottom': '15px'}),
    dcc.Graph(id='monte-carlo-chart', config={'displayModeBar': True, 'displaylogo': False}),
    html.Div(id='monte-carlo-stats', style={
        'display': 'flex', 'justifyContent': 'center', 'gap': '30px', 'marginTop': '15px',
        'backgroundColor': '#fff', 'padding': '12px 20px', 'borderRadius': '6px', 'border': '1px solid #e0e0e0'
    }),
    html.Div(style={'marginBottom': '50px'}),

    # Footer
    html.Hr(style={'marginTop': '40px'}),
    html.P("Built with Python Dash & Plotly · ~2,000 records, 9 SQLite tables · Hosted on Render · Yoruba Diaspora Learning Platform © 2026",
           style={'textAlign': 'center', 'color': '#888', 'fontSize': '0.85em', 'marginTop': '15px'})
])

# ========== CALLBACKS ==========

# Section 1
@callback([Output('location-chart', 'figure'), Output('stats-panel-1', 'children')],
          [Input('location-filter', 'value'), Input('stat-1', 'value')])
def update_s1(location, stat):
    filtered = q1 if location == 'All' else q1[q1['Location'] == location]
    fig = px.bar(filtered, x='Location', y=['Total Learners', 'Lessons Accessed'], barmode='group',
                 color_discrete_sequence=['#2E86AB', '#A23B72'])
    fig = style_fig(fig, 'Location', 'Count')
    stats = [
        html.Span([html.Strong(f'{stat} Score: '), calc_stats(filtered['Avg Score (%)'], stat, '')], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Time: '), calc_stats(filtered['Avg Time (mins)'], stat, '') + ' mins'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Locations: '), str(len(filtered))], style={'fontSize': '0.95em'}),
    ]
    return fig, stats

# Section 2
@callback([Output('age-chart', 'figure'), Output('stats-panel-2', 'children')],
          [Input('age-filter', 'value'), Input('stat-2', 'value')])
def update_s2(age_group, stat):
    filtered = q2 if age_group == 'All' else q2[q2['Age Group'] == age_group]
    fig = px.bar(filtered, x='Age Group', y=['Total Learners', 'Avg Score (%)'], barmode='group',
                 color_discrete_sequence=['#F18F01', '#C73E1D'])
    fig = style_fig(fig, 'Age Group', 'Count / Percentage (%)')
    stats = [
        html.Span([html.Strong(f'{stat} Score: '), calc_stats(filtered['Avg Score (%)'], stat, '')], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Time: '), calc_stats(filtered['Avg Time (mins)'], stat, '') + ' mins'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Groups: '), str(len(filtered))], style={'fontSize': '0.95em'}),
    ]
    return fig, stats

# Section 3
@callback([Output('category-chart', 'figure'), Output('stats-panel-3', 'children')],
          [Input('category-filter', 'value'), Input('stat-3', 'value')])
def update_s3(category, stat):
    filtered = q3 if category == 'All' else q3[q3['Category'] == category]
    fig = px.bar(filtered, x='Category', y=['Completion Rate (%)', 'Avg Quiz Score (%)'], barmode='group',
                 color_discrete_sequence=['#2E86AB', '#F18F01'])
    fig = style_fig(fig, 'Lesson Category', 'Percentage (%)')
    stats = [
        html.Span([html.Strong(f'{stat} Completion: '), calc_stats(filtered['Completion Rate (%)'], stat, '') + '%'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Quiz: '), calc_stats(filtered['Avg Quiz Score (%)'], stat, '') + '%'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Categories: '), str(len(filtered))], style={'fontSize': '0.95em'}),
    ]
    return fig, stats

# Section 6
@callback([Output('engagement-chart', 'figure'), Output('stats-panel-6', 'children')], Input('stat-6', 'value'))
def update_s6(stat):
    fig = px.bar(q6, x='Engagement Score', y='Display Name', orientation='h', color='Location',
                 color_discrete_sequence=['#2E86AB', '#A23B72', '#F18F01'])
    fig = style_fig(fig, 'Engagement Score (composite)', '')
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Score: %{x}<extra></extra>')
    stats = [
        html.Span([html.Strong(f'{stat} Score: '), calc_stats(q6['Engagement Score'], stat, '')], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Posts: '), calc_stats(q6['Discussion Posts'], stat, '')], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Users: '), str(len(q6))], style={'fontSize': '0.95em'}),
    ]
    return fig, stats

# Section 7
@callback([Output('scatter-chart', 'figure'), Output('scatter-table', 'data'),
           Output('scatter-table', 'columns'), Output('stats-panel-7', 'children')],
          [Input('proficiency-filter', 'value'), Input('stat-7', 'value')])
def update_s7(proficiency, stat):
    filtered = q7 if proficiency == 'All' else q7[q7['Proficiency'] == proficiency]
    fig = px.scatter(filtered, x='Time Spent (mins)', y='Quiz Score (%)', color='Proficiency',
                     hover_data=['Learner', 'Lesson'], trendline='ols',
                     color_discrete_sequence=['#C73E1D', '#F18F01', '#2E86AB'])
    fig = style_fig(fig, 'Time Spent (minutes)', 'Quiz Score (%)')
    fig.update_layout(hovermode='closest')
    stats = [
        html.Span([html.Strong(f'{stat} Time: '), calc_stats(filtered['Time Spent (mins)'], stat, '') + ' mins'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Score: '), calc_stats(filtered['Quiz Score (%)'], stat, '') + '%'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Records: '), str(len(filtered))], style={'fontSize': '0.95em'}),
    ]
    columns = [{"name": i, "id": i} for i in filtered.columns]
    return fig, filtered.to_dict('records'), columns, stats

# Section 8
@callback([Output('proficiency-chart', 'figure'), Output('stats-panel-8', 'children')], Input('stat-8', 'value'))
def update_s8(stat):
    fig = px.bar(q8, x='Proficiency Level', y=['Completion Rate (%)', 'Avg Score (%)'], barmode='group',
                 color_discrete_sequence=['#2E86AB', '#A23B72'])
    fig = style_fig(fig, 'Proficiency Level', 'Percentage (%)')
    stats = [
        html.Span([html.Strong(f'{stat} Completion: '), calc_stats(q8['Completion Rate (%)'], stat, '') + '%'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong(f'{stat} Score: '), calc_stats(q8['Avg Score (%)'], stat, '') + '%'], style={'fontSize': '0.95em'}),
        html.Span([html.Strong('Levels: '), str(len(q8))], style={'fontSize': '0.95em'}),
    ]
    return fig, stats

# Section 9: Monte Carlo Simulation
np.random.seed(42)  # Fixed seed for reproducibility
current_learners = int(total_learners)
quarters_ahead = 12 # Prediction for next 3 years
n_simulations = 1000
variance = 0.062  # ±6.2% quarterly std dev from Duolingo MAU data (Statista, 2026) https://www.statista.com/statistics/1309610/duolingo-quarterly-mau/?srsltid=AfmBOopFJ_7sbldeUeIegGMx5jJDSE1wq2ydHry-ChJ6tE5g90oS60C1
mean_growth = 0.067  # 6.7% mean quarterly growth from Duolingo data

# Run simulations
all_paths = np.zeros((n_simulations, quarters_ahead + 1))
all_paths[:, 0] = current_learners

for sim in range(n_simulations):
    for q in range(1, quarters_ahead + 1):
        growth_rate = np.random.normal(mean_growth, variance)
        all_paths[sim, q] = all_paths[sim, q-1] * (1 + growth_rate)

# Calculate percentiles
p5 = np.percentile(all_paths, 5, axis=0)
p25 = np.percentile(all_paths, 25, axis=0)
p50 = np.percentile(all_paths, 50, axis=0)
p75 = np.percentile(all_paths, 75, axis=0)
p95 = np.percentile(all_paths, 95, axis=0)

quarters = [f'Q{((i-1)%4)+1} {2026 + (i-1)//4}' if i > 0 else 'Now' for i in range(quarters_ahead + 1)]

# Build Monte Carlo figure
mc_fig = go.Figure()
mc_fig.add_trace(go.Scatter(x=quarters, y=p95, mode='lines', line=dict(width=0), showlegend=False, name='95th Percentile', hoverinfo='skip'))
mc_fig.add_trace(go.Scatter(x=quarters, y=p5, mode='lines', line=dict(width=0), fill='tonexty',
                            fillcolor='rgba(46,134,171,0.15)', name='90% Confidence Band', hovertemplate='90% Band Lower: %{y:.0f}<extra></extra>'))
mc_fig.add_trace(go.Scatter(x=quarters, y=p75, mode='lines', line=dict(width=0), showlegend=False, name='75th Percentile', hoverinfo='skip'))
mc_fig.add_trace(go.Scatter(x=quarters, y=p25, mode='lines', line=dict(width=0), fill='tonexty',
                            fillcolor='rgba(46,134,171,0.3)', name='50% Confidence Band', hovertemplate='50% Band Lower: %{y:.0f}<extra></extra>'))
mc_fig.add_trace(go.Scatter(x=quarters, y=p50, mode='lines', line=dict(color='#2E86AB', width=3),
                            name='Median Projection', hovertemplate='Median: %{y:.0f} learners<extra></extra>'))
mc_fig.update_layout(
    font_family=FONT, plot_bgcolor='#FAFAFA', paper_bgcolor='#FAFAFA',
    xaxis_title=dict(text='<b>Quarter</b>', font=dict(size=14)),
    yaxis_title=dict(text='<b>Projected Active Learners</b>', font=dict(size=14)),
    legend_title=dict(text='<b>Key</b>', font=dict(size=14)),
    hovermode='x unified'
)

# Update the monte carlo graph and stats in layout
app.layout.children[-4].children = dcc.Graph(figure=mc_fig, config={'displayModeBar': True, 'displaylogo': False})


for i, child in enumerate(app.layout.children):
    if hasattr(child, 'id') and child.id == 'monte-carlo-chart':
        app.layout.children[i] = dcc.Graph(figure=mc_fig, id='monte-carlo-chart', config={'displayModeBar': True, 'displaylogo': False})
    if hasattr(child, 'id') and child.id == 'monte-carlo-stats':
        app.layout.children[i] = html.Div(style={
            'display': 'flex', 'justifyContent': 'center', 'gap': '30px', 'marginTop': '15px',
            'backgroundColor': '#fff', 'padding': '12px 20px', 'borderRadius': '6px', 'border': '1px solid #e0e0e0'
        }, children=[
            html.Span([html.Strong('Median (3 yrs): '), f'{int(p50[-1])} learners'], style={'fontSize': '0.95em'}),
            html.Span([html.Strong('90% Range: '), f'{int(p5[-1])} – {int(p95[-1])} learners'], style={'fontSize': '0.95em'}),
            html.Span([html.Strong('Simulations: '), '1,000'], style={'fontSize': '0.95em'}),
        ])

if __name__ == '__main__':
    app.run(debug=True)
