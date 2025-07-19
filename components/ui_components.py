"""
Composants UI pour l'application Excel Data Manager Pro
Architecture MVC - Séparation des responsabilités
Hackathon Codon 2025
"""
import streamlit as st
import os

def load_styles():
    """Charge le CSS externe depuis assets/styles.css"""
    css_path = os.path.join("assets", "styles.css")
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        return True
    except FileNotFoundError:
        st.error("❌ Fichier CSS non trouvé : assets/styles.css")
        return False
    except Exception as e:
        st.error(f"❌ Erreur CSS : {str(e)}")
        return False

def render_main_header():
    """En-tête principal de l'application"""
    st.markdown("""
    <div class="main-header">
        <h1>Excel Data Manager Pro</h1>
        <p>Gestion complète des fichiers Excel • Architecture MVC • Base de données relationnelle</p>
    </div>
    """, unsafe_allow_html=True)

def render_navigation_sidebar():
    """Navigation dans la barre latérale"""
    st.sidebar.markdown("### Navigation")
    
    # Configuration des pages
    pages = {
        "Tableau de Bord": "Tableau de Bord",
        "Importation": "Importation", 
        "Gestion": "Gestion",
        "Exportation": "Exportation"
    }
    
    # Initialisation de la page courante
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Tableau de Bord"
    
    # Boutons de navigation
    for display_name, page_name in pages.items():
        if st.sidebar.button(display_name, 
                            key=f"nav_{page_name}",
                            use_container_width=True):
            st.session_state.current_page = page_name
    
    return st.session_state.current_page

def render_admin_controls():
    """Contrôles d'administration dans la sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Administration")
    
    refresh_clicked = st.sidebar.button("Actualiser", 
                                       help="Actualiser les données",
                                       use_container_width=True)
    
    clear_clicked = st.sidebar.button("Vider Cache", 
                                     help="Vider le cache et supprimer toutes les données",
                                     use_container_width=True)
    
    return refresh_clicked, clear_clicked

def render_metric_card(title, value, description, color="#667eea"):
    """Affiche une carte métrique moderne avec alignement parfait"""
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {color};">
        <div class="metric-title" style="color: {color};">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chart_container(content):
    """Conteneur pour les graphiques"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    content()
    st.markdown('</div>', unsafe_allow_html=True)

def show_empty_state():
    """Affichage quand aucune donnée n'est disponible"""
    st.warning("Aucune donnée disponible")
    st.markdown("""
    ### Pour commencer :
    1. **Importez** un fichier Excel (.xlsx)
    2. **Gérez** vos données  
    3. **Exportez** vos résultats
    """)

def show_loading(message="Traitement en cours..."):
    """Affichage de chargement"""
    return st.spinner(message)

def show_success(message):
    """Message de succès"""
    st.success(message)

def show_error(message):
    """Message d'erreur"""
    st.error(message)

def show_info(message):
    """Message d'information"""
    st.info(message)

def show_warning(message):
    """Message d'avertissement"""
    st.warning(message)

def create_download_button(data, filename, label="Télécharger", mime_type="application/octet-stream"):
    """Bouton de téléchargement standardisé"""
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type,
        type="primary",
        use_container_width=True
    )

def render_sidebar_stats(controller):
    """Affiche les statistiques dans la sidebar"""
    st.sidebar.markdown("### Statistiques")
    try:
        total_employees = controller.db.get_employee_count()
        st.sidebar.metric("Employés", total_employees)
        if total_employees > 0:
            stats = controller.get_statistics()
            st.sidebar.metric("Salaire Moyen", f"{stats['salaire_moyen']:,.0f} FCFA")
    except:
        st.sidebar.error("Erreur DB")

def render_chart_section_header():
    """Affiche l'en-tête de la section graphiques"""
    st.markdown("""
    <div class="chart-section">
        <h2>Analyses Graphiques Avancées</h2>
    </div>
    """, unsafe_allow_html=True)

def render_print_button():
    """Affiche le bouton d'impression"""
    col_print, col_space = st.columns([1, 4])
    with col_print:
        if st.button("IMPRIMER RAPPORT", help="Imprimer les graphiques et statistiques"):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
