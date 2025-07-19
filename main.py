"""
Excel Data Manager Pro - Application principale
Architecture MVC propre avec séparation des responsabilités
Hackathon Codon 2025
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from controllers.excel_controller import ExcelController
from components.ui_components import (
    load_styles, render_main_header, render_navigation_sidebar,
    render_admin_controls, render_metric_card, render_chart_container,
    show_empty_state, show_loading, show_success, show_error, show_info,
    create_download_button
)

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Excel Data Manager Pro", 
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement des styles CSS
load_styles()

# En-tête principal
render_main_header()

# Initialisation du contrôleur
@st.cache_resource
def init_controller():
    return ExcelController()

controller = init_controller()

# Navigation et contrôles
page = render_navigation_sidebar()
refresh_clicked, clear_clicked = render_admin_controls()

# Gestion des boutons d'administration
if refresh_clicked:
    st.rerun()

if clear_clicked:
    st.cache_data.clear()
    st.cache_resource.clear()
    try:
        controller.db.clear_all_data()
        show_success("Cache vidé et données supprimées !")
    except Exception as e:
        show_error(f"Erreur lors de la suppression : {str(e)}")

# PAGE 1: TABLEAU DE BORD
if page == "Tableau de Bord":
    st.header("Tableau de Bord Exécutif")
    
    stats = controller.get_statistics()
    df = controller.db.get_all_data()
    
    if stats['total_employes'] > 0:
        # Métriques principales
        st.markdown("### Indicateurs Clés")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card("Total Employés", stats['total_employes'], "Effectif global", "#667eea")
        with col2:
            render_metric_card("Salaire Moyen", f"{stats['salaire_moyen']:,.0f} FCFA", "Rémunération moyenne", "#28a745")
        with col3:
            render_metric_card("Salaire Maximum", f"{stats['salaire_max']:,.0f} FCFA", "Plus haute rémunération", "#fd7e14")
        with col4:
            total_cat = stats['nombre_departements'] + stats['nombre_postes']
            render_metric_card("Catégories", total_cat, "Dép. + Postes", "#6f42c1")
        
        # Graphiques
        st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
        st.markdown("### Analyses Visuelles")
        has_dept = ('departement' in df.columns and 
                   df['departement'].notna().sum() > 0 and 
                   (df['departement'] != 'None').sum() > 0 and
                   (df['departement'] != '').sum() > 0)
        has_poste = ('poste' in df.columns and 
                    df['poste'].notna().sum() > 0 and 
                    (df['poste'] != 'None').sum() > 0 and
                    (df['poste'] != '').sum() > 0)
        
        # Première ligne - Distribution principale
        col1, col2 = st.columns(2)
        
        with col1:
            def main_distribution_chart():
                if has_dept:
                    # Distribution par département (prioritaire)
                    st.markdown("**Distribution par Département**")
                    dept_count = df['departement'].value_counts()
                    total_emp = len(df)
                    
                    # Créer un graphique donut avec go.Figure
                    fig = go.Figure(data=[go.Pie(
                        labels=dept_count.index, 
                        values=dept_count.values,
                        hole=0.4,
                        marker=dict(
                            colors=px.colors.qualitative.Set3,
                            line=dict(color='#FFFFFF', width=2)
                        ),
                        textinfo='label+percent+value',
                        textposition='outside',
                        hovertemplate='<b>%{label}</b><br>' +
                                    'Employés: %{value}<br>' +
                                    'Pourcentage: %{percent}<br>' +
                                    '<extra></extra>'
                    )])
                    
                    # Ajouter une annotation centrale
                    fig.add_annotation(
                        text=f"<b>Total<br>{total_emp}</b><br>employés",
                        x=0.5, y=0.5,
                        font_size=14,
                        showarrow=False,
                        font_color="darkblue"
                    )
                    
                    fig.update_layout(
                        title="Répartition par Département",
                        height=350,
                        showlegend=True,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=11)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                elif has_poste:
                    # Seulement poste si pas de département
                    st.markdown("**Distribution par Poste**")
                    poste_count = df['poste'].value_counts()
                    total_emp = len(df)
                    
                    # Créer un graphique donut avec go.Figure
                    fig = go.Figure(data=[go.Pie(
                        labels=poste_count.index, 
                        values=poste_count.values,
                        hole=0.4,
                        marker=dict(
                            colors=px.colors.qualitative.Pastel,
                            line=dict(color='#FFFFFF', width=2)
                        ),
                        textinfo='label+percent+value',
                        textposition='outside',
                        hovertemplate='<b>%{label}</b><br>' +
                                    'Employés: %{value}<br>' +
                                    'Pourcentage: %{percent}<br>' +
                                    '<extra></extra>'
                    )])
                    
                    # Ajouter une annotation centrale
                    fig.add_annotation(
                        text=f"<b>Total<br>{total_emp}</b><br>employés",
                        x=0.5, y=0.5,
                        font_size=14,
                        showarrow=False,
                        font_color="darkblue"
                    )
                    
                    fig.update_layout(
                        title="Répartition par Poste",
                        height=350,
                        showlegend=True,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=11)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Aucune donnée de département ou poste disponible")
            render_chart_container(main_distribution_chart)
            
        with col2:
            def salary_comparison_chart():
                if has_poste:
                    # Graphique par poste (prioritaire pour la complémentarité)
                    st.markdown("**Salaires Moyens par Poste**")
                    poste_stats = df.groupby('poste')['salaire'].mean().sort_values(ascending=False)
                    
                    # Graphique en barres amélioré avec couleurs multiples
                    colors = ['#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22']
                    bar_colors = [colors[i % len(colors)] for i in range(len(poste_stats))]
                    
                    fig = go.Figure(go.Bar(
                        x=poste_stats.values, 
                        y=poste_stats.index, 
                        orientation='h',
                        marker=dict(color=bar_colors, line=dict(color='white', width=1)),
                        text=[f'{val:,.0f} FCFA' for val in poste_stats.values],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>' +
                                    'Salaire moyen: %{x:,.0f} FCFA<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # Ajouter ligne de référence pour la moyenne générale
                    avg_salary = df['salaire'].mean()
                    fig.add_vline(x=avg_salary, line_dash="dash", line_color="red", 
                                 annotation_text=f"Moyenne: {avg_salary:,.0f}")
                    
                    fig.update_layout(
                        title="Salaires par Poste", 
                        height=350,
                        xaxis_title="Salaire (FCFA)", 
                        yaxis_title="Poste",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        font=dict(size=11)
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                elif has_dept:
                    # Seulement département si pas de poste
                    st.markdown("**Salaires Moyens par Département**")
                    dept_stats = df.groupby('departement')['salaire'].mean().sort_values(ascending=False)
                    
                    # Graphique en barres amélioré avec couleurs multiples
                    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#E377C2', '#7F7F7F']
                    bar_colors = [colors[i % len(colors)] for i in range(len(dept_stats))]
                    
                    fig = go.Figure(go.Bar(
                        x=dept_stats.values, 
                        y=dept_stats.index, 
                        orientation='h',
                        marker=dict(color=bar_colors, line=dict(color='white', width=1)),
                        text=[f'{val:,.0f} FCFA' for val in dept_stats.values],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>' +
                                    'Salaire moyen: %{x:,.0f} FCFA<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # Ajouter ligne de référence pour la moyenne générale
                    avg_salary = df['salaire'].mean()
                    fig.add_vline(x=avg_salary, line_dash="dash", line_color="red", 
                                 annotation_text=f"Moyenne: {avg_salary:,.0f}")
                    
                    fig.update_layout(
                        title="Salaires par Département", 
                        height=350,
                        xaxis_title="Salaire (FCFA)", 
                        yaxis_title="Département",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        font=dict(size=11)
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Aucune donnée de département ou poste disponible")
            render_chart_container(salary_comparison_chart)
        
        # Deuxième ligne - Analyses complémentaires
        col3, col4 = st.columns(2)
        
        with col3:
            def secondary_analysis_chart():
                if has_dept and has_poste:
                    # Cas complet : graphique croisé département vs poste
                    st.markdown("**Effectifs Croisés Département-Poste**")
                    cross_tab = pd.crosstab(df['departement'], df['poste'])
                    fig = px.imshow(cross_tab.values,
                                  x=cross_tab.columns,
                                  y=cross_tab.index,
                                  title="Répartition Croisée",
                                  aspect="auto",
                                  color_continuous_scale="Blues")
                    fig.update_layout(height=350)
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                elif has_dept:
                    # Seulement département : effectifs par département
                    st.markdown("**Effectifs par Département**")
                    dept_count = df['departement'].value_counts()
                    
                    # Graphique en barres amélioré avec couleurs multiples
                    colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B']
                    bar_colors = [colors[i % len(colors)] for i in range(len(dept_count))]
                    
                    fig = go.Figure(go.Bar(
                        x=dept_count.index, 
                        y=dept_count.values,
                        marker=dict(color=bar_colors, line=dict(color='white', width=1)),
                        text=dept_count.values,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>' +
                                    'Nombre d\'employés: %{y}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Nombre d'Employés par Département",
                        height=350,
                        xaxis_title="Département", 
                        yaxis_title="Nombre d'Employés",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        font=dict(size=11)
                    )
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                elif has_poste:
                    # Seulement poste : effectifs par poste
                    st.markdown("**Effectifs par Poste**")
                    poste_count = df['poste'].value_counts()
                    
                    # Graphique en barres amélioré avec couleurs multiples
                    colors = ['#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B', '#E377C2']
                    bar_colors = [colors[i % len(colors)] for i in range(len(poste_count))]
                    
                    fig = go.Figure(go.Bar(
                        x=poste_count.index, 
                        y=poste_count.values,
                        marker=dict(color=bar_colors, line=dict(color='white', width=1)),
                        text=poste_count.values,
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>' +
                                    'Nombre d\'employés: %{y}<br>' +
                                    '<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Nombre d'Employés par Poste",
                        height=350,
                        xaxis_title="Poste", 
                        yaxis_title="Nombre d'Employés",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        font=dict(size=11),
                        xaxis_tickangle=-45
                    )
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Aucune donnée de catégorie disponible")
            render_chart_container(secondary_analysis_chart)
            
        with col4:
            def scatter_chart():
                st.markdown("**Nuage de Points - Analyse des Salaires**")
                if len(df) > 1:
                    df_scatter = df.copy()
                    df_scatter['index'] = range(len(df_scatter))
                    
                    # Choisir la couleur selon les données disponibles
                    color_col = None
                    if has_dept and has_poste:
                        color_col = 'departement'  # Priorité au département si les deux existent
                    elif has_dept:
                        color_col = 'departement'
                    elif has_poste:
                        color_col = 'poste'
                    
                    # Normaliser les tailles des marqueurs
                    min_salary = df['salaire'].min()
                    max_salary = df['salaire'].max()
                    size_range = [8, 25]
                    
                    if color_col:
                        # Créer des couleurs distinctes pour chaque catégorie
                        categories = df_scatter[color_col].unique()
                        color_map = {cat: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)] 
                                   for i, cat in enumerate(categories)}
                        
                        fig = go.Figure()
                        
                        for cat in categories:
                            df_cat = df_scatter[df_scatter[color_col] == cat]
                            fig.add_trace(go.Scatter(
                                x=df_cat['index'],
                                y=df_cat['salaire'],
                                mode='markers',
                                name=cat,
                                marker=dict(
                                    size=[(s - min_salary) / (max_salary - min_salary) * (size_range[1] - size_range[0]) + size_range[0] 
                                          for s in df_cat['salaire']],
                                    color=color_map[cat],
                                    line=dict(width=1, color='white'),
                                    opacity=0.8
                                ),
                                hovertemplate='<b>Employé %{x}</b><br>' +
                                            f'{color_col.capitalize()}: {cat}<br>' +
                                            'Salaire: %{y:,.0f} FCFA<br>' +
                                            '<extra></extra>'
                            ))
                    else:
                        # Pas de catégorie de couleur
                        fig = go.Figure(go.Scatter(
                            x=df_scatter['index'],
                            y=df_scatter['salaire'],
                            mode='markers',
                            marker=dict(
                                size=[(s - min_salary) / (max_salary - min_salary) * (size_range[1] - size_range[0]) + size_range[0] 
                                      for s in df_scatter['salaire']],
                                color='rgba(102, 126, 234, 0.8)',
                                line=dict(width=1, color='white')
                            ),
                            hovertemplate='<b>Employé %{x}</b><br>' +
                                        'Salaire: %{y:,.0f} FCFA<br>' +
                                        '<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title="Distribution des Salaires",
                        height=350,
                        xaxis_title="Employé", 
                        yaxis_title="Salaire (FCFA)",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        showlegend=bool(color_col),
                        font=dict(size=11)
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Pas assez de données pour le nuage de points")
            render_chart_container(scatter_chart)
        
        # Troisième ligne
        col5, col6 = st.columns(2)
        
        with col5:
            def line_chart():
                st.markdown("**Tendance des Salaires**")
                if len(df) > 2:
                    df_sorted = df.sort_values('salaire').reset_index(drop=True)
                    df_sorted['rang'] = range(1, len(df_sorted) + 1)
                    
                    # Créer le graphique linéaire avec go.Figure
                    fig = go.Figure()
                    
                    # Ligne principale
                    fig.add_trace(go.Scatter(
                        x=df_sorted['rang'],
                        y=df_sorted['salaire'],
                        mode='lines+markers',
                        name='Progression',
                        line=dict(color='rgba(102, 126, 234, 0.8)', width=3),
                        marker=dict(size=6, color='rgba(102, 126, 234, 1)', 
                                  line=dict(width=1, color='white')),
                        hovertemplate='<b>Rang %{x}</b><br>' +
                                    'Salaire: %{y:,.0f} FCFA<br>' +
                                    '<extra></extra>'
                    ))
                    
                    # Ajouter des annotations pour min et max
                    min_salary = df_sorted['salaire'].min()
                    max_salary = df_sorted['salaire'].max()
                    min_pos = df_sorted[df_sorted['salaire'] == min_salary]['rang'].iloc[0]
                    max_pos = df_sorted[df_sorted['salaire'] == max_salary]['rang'].iloc[0]
                    
                    fig.add_annotation(
                        x=min_pos, y=min_salary,
                        text=f"Min: {min_salary:,.0f}",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="red",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="red"
                    )
                    
                    fig.add_annotation(
                        x=max_pos, y=max_salary,
                        text=f"Max: {max_salary:,.0f}",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="green",
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="green"
                    )
                    
                    # Ligne de référence pour la moyenne
                    avg_salary = df['salaire'].mean()
                    fig.add_hline(y=avg_salary, line_dash="dash", line_color="orange",
                                 annotation_text=f"Moyenne: {avg_salary:,.0f} FCFA")
                    
                    fig.update_layout(
                        title="Progression des Salaires",
                        height=350,
                        xaxis_title="Rang", 
                        yaxis_title="Salaire (FCFA)",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        showlegend=False,
                        font=dict(size=11)
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Pas assez de données pour le graphique linéaire")
            render_chart_container(line_chart)
            
        with col6:
            def histogram_chart():
                st.markdown("**Histogramme des Salaires**")
                if len(df) > 0:
                    nbins = min(10, max(3, len(df) // 2))
                    
                    # Créer l'histogramme avec go.Figure
                    fig = go.Figure(data=[go.Histogram(
                        x=df['salaire'],
                        nbinsx=nbins,
                        marker=dict(
                            color='rgba(102, 126, 234, 0.7)',
                            line=dict(color='white', width=1)
                        ),
                        hovertemplate='Salaire: %{x:,.0f} FCFA<br>' +
                                    'Nombre d\'employés: %{y}<br>' +
                                    '<extra></extra>'
                    )])
                    
                    # Ajouter des lignes de référence
                    mean_salary = df['salaire'].mean()
                    median_salary = df['salaire'].median()
                    
                    fig.add_vline(x=mean_salary, line_dash="dash", line_color="red",
                                 annotation_text=f"Moyenne: {mean_salary:,.0f}")
                    fig.add_vline(x=median_salary, line_dash="dot", line_color="orange",
                                 annotation_text=f"Médiane: {median_salary:,.0f}")
                    
                    fig.update_layout(
                        title="Distribution des Salaires",
                        height=350,
                        xaxis_title="Salaire (FCFA)", 
                        yaxis_title="Nombre d'employés",
                        plot_bgcolor='rgba(248,248,255,0.8)',
                        showlegend=False,
                        font=dict(size=11)
                    )
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    show_info("Aucune donnée de salaire disponible")
            render_chart_container(histogram_chart)
        
        # Données détaillées
        st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
        st.markdown("### Données Détaillées")
        show_all = st.checkbox("Afficher toutes les données", value=False)
        
        if show_all:
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.dataframe(df.head(10), use_container_width=True)
            if len(df) > 10:
                show_info(f"Affichage de 10 lignes sur {len(df)} au total")
        
        # Analyses détaillées
        st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
        st.markdown("### Analyses Détaillées")
        col7, col8 = st.columns(2)
        
        with col7:
            if has_dept:
                # Statistiques par département
                st.markdown("**Statistiques par Département**")
                dept_detailed = df.groupby('departement').agg({
                    'salaire': ['count', 'mean', 'max', 'min']
                }).round(0)
                dept_detailed.columns = ['Effectif', 'Salaire Moyen', 'Salaire Max', 'Salaire Min']
                st.dataframe(dept_detailed, use_container_width=True)
            elif has_poste:
                # Seulement poste
                st.markdown("**Statistiques par Poste**")
                poste_detailed = df.groupby('poste').agg({
                    'salaire': ['count', 'mean', 'max', 'min']
                }).round(0)
                poste_detailed.columns = ['Effectif', 'Salaire Moyen', 'Salaire Max', 'Salaire Min']
                st.dataframe(poste_detailed, use_container_width=True)
            else:
                show_info("Aucune donnée de catégorie pour les statistiques")
        
        with col8:
            if has_poste and has_dept:
                # Cas complet : statistiques par poste (complémentaire)
                st.markdown("**Statistiques par Poste**")
                poste_detailed = df.groupby('poste').agg({
                    'salaire': ['count', 'mean', 'max', 'min']
                }).round(0)
                poste_detailed.columns = ['Effectif', 'Salaire Moyen', 'Salaire Max', 'Salaire Min']
                st.dataframe(poste_detailed, use_container_width=True)
            elif len(df) > 0:
                # Top 10 des salaires (dans tous les autres cas)
                st.markdown("**Top 10 des Salaires**")
                columns_to_show = ['nom', 'salaire']
                if has_dept:
                    columns_to_show.append('departement')
                if has_poste:
                    columns_to_show.append('poste')
                # Vérifier que toutes les colonnes existent
                columns_to_show = [col for col in columns_to_show if col in df.columns]
                top_salaries = df.nlargest(min(10, len(df)), 'salaire')[columns_to_show]
                st.dataframe(top_salaries, use_container_width=True)
            else:
                show_info("Aucune donnée disponible")
    else:
        show_empty_state()

# PAGE 2: IMPORTATION
elif page == "Importation":
    st.header("Importation de Fichiers Excel")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier Excel (.xlsx)",
        type=['xlsx'],
        help="Formats supportés : .xlsx"
    )
    
    if uploaded_file:
        show_success("Fichier sélectionné !")
        st.write(f"**Nom :** {uploaded_file.name}")
        st.write(f"**Taille :** {uploaded_file.size} octets")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("IMPORTER", type="primary"):
                with show_loading("Importation en cours..."):
                    try:
                        result = controller.import_excel(uploaded_file)
                        if result["success"]:
                            show_success("Importation réussie !")
                            col_s, col_e = st.columns(2)
                            with col_s:
                                st.metric("Lignes importées", result["imported"])
                            with col_e:
                                st.metric("Erreurs", result["errors"])
                        else:
                            show_error(result['message'])
                    except Exception as e:
                        show_error(f"Erreur système : {str(e)}")
        
        with col2:
            try:
                df_preview = pd.read_excel(uploaded_file, nrows=5)
                st.write("**Aperçu :**")
                st.dataframe(df_preview, use_container_width=True)
            except Exception as e:
                st.warning(f"Impossible de prévisualiser : {e}")

# PAGE 3: GESTION
elif page == "Gestion":
    st.header("Gestion des Données")
    
    df = controller.db.get_all_data()
    
    if not df.empty:
        # Recherche
        st.subheader("Recherche et Filtres")
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Rechercher (nom ou email)")
        with col2:
            sort_by = st.selectbox("Trier par", ["nom", "email", "salaire"])
        
        # Application des filtres
        filtered_df = df.copy()
        if search_term:
            mask = (
                filtered_df['nom'].str.contains(search_term, case=False, na=False) |
                filtered_df['email'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if sort_by in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by=sort_by)
        
        st.dataframe(filtered_df, use_container_width=True)
        show_info(f"{len(filtered_df)} employé(s) affiché(s) sur {len(df)} au total")
        
        # Modification d'employé
        st.subheader("Modifier un Employé")
        if len(filtered_df) > 0:
            employee_options = [f"ID {row['id']} - {row['nom']}" for _, row in filtered_df.iterrows()]
            selected_option = st.selectbox("Choisir un employé", employee_options)
            
            if selected_option:
                employee_id = int(selected_option.split(' - ')[0].replace('ID ', ''))
                selected_row = df[df['id'] == employee_id].iloc[0]
                
                with st.form("modify_employee"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_nom = st.text_input("Nom", value=str(selected_row['nom'] or ""))
                        new_email = st.text_input("Email", value=str(selected_row['email'] or ""))
                        new_telephone = st.text_input("Téléphone", value=str(selected_row['telephone'] or ""))
                    
                    with col2:
                        new_departement = st.text_input("Département", value=str(selected_row['departement'] or ""))
                        new_poste = st.text_input("Poste", value=str(selected_row['poste'] or ""))
                        new_salaire = st.number_input("Salaire", value=float(selected_row['salaire'] or 0))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("METTRE À JOUR", type="primary"):
                            try:
                                controller.db.update_employee(employee_id, 'nom', new_nom)
                                controller.db.update_employee(employee_id, 'email', new_email)
                                controller.db.update_employee(employee_id, 'telephone', new_telephone)
                                controller.db.update_employee(employee_id, 'departement', new_departement)
                                controller.db.update_employee(employee_id, 'poste', new_poste)
                                controller.db.update_employee(employee_id, 'salaire', new_salaire)
                                show_success("Employé mis à jour !")
                                st.rerun()
                            except Exception as e:
                                show_error(f"Erreur : {str(e)}")
                    
                    with col2:
                        if st.form_submit_button("SUPPRIMER", type="secondary"):
                            try:
                                controller.db.delete_employee(employee_id)
                                show_success("Employé supprimé !")
                                st.rerun()
                            except Exception as e:
                                show_error(f"Erreur : {str(e)}")
    else:
        show_empty_state()

# PAGE 4: EXPORTATION
elif page == "Exportation":
    st.header("Exportation des Données")
    
    df = controller.db.get_all_data()
    
    if not df.empty:
        st.subheader("Statistiques d'Export")
        st.metric("Nombre d'employés à exporter", len(df))
        
        st.subheader("Aperçu")
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Configuration Export")
        filename = st.text_input("Nom du fichier", value="export_employees.xlsx")
        
        if st.button("GÉNÉRER FICHIER EXCEL", type="primary"):
            try:
                result = controller.export_to_excel(filename)
                if result["success"]:
                    show_success(f"Export réussi ! {result['message']}")
                    
                    try:
                        with open(filename, "rb") as file:
                            create_download_button(
                                data=file.read(),
                                filename=filename,
                                label="TÉLÉCHARGER LE FICHIER EXCEL",
                                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        show_error(f"Erreur de téléchargement : {str(e)}")
                else:
                    show_error(f"Erreur d'export : {result['message']}")
            except Exception as e:
                show_error(f"Erreur système : {str(e)}")
    else:
        show_empty_state()
