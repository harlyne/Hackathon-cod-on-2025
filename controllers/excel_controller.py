import pandas as pd
from models.database import EmployeeDatabase

class ExcelController:
    """
    Contrôleur principal pour la gestion des fichiers Excel.
    Gère l'import, l'export et la normalisation des données entre Excel et la base SQLite.
    Architecture MVC : ce contrôleur fait le lien entre la Vue (Streamlit) et le Modèle (Database).
    """
    
    def __init__(self):
        """
        Initialise le contrôleur avec une instance de la base de données.
        """
        # Création de l'instance de base de données (Modèle)
        self.db = EmployeeDatabase()
    
    def import_excel(self, uploaded_file):
        """
        Importe un fichier Excel vers la base de données SQLite.
        Fonctionnalité 1 du hackathon : IMPORTATION .xlsx
        
        Args:
            uploaded_file: Fichier Excel uploadé via Streamlit
            
        Returns:
            dict: {
                "success": bool,
                "message": str,
                "imported": int,
                "errors": int,
                "error_details": list
            }
        """
        try:
            # Étape 1: Lecture du fichier Excel avec pandas
            df = pd.read_excel(uploaded_file)
            
            # Étape 2: Validation basique du fichier
            if df.empty:
                return {
                    "success": False,
                    "message": "Le fichier Excel est vide",
                    "imported": 0,
                    "errors": 1,
                    "error_details": ["Le fichier Excel est vide"]
                }
            
            # Étape 3: Normalisation des données selon vos 2 formats
            normalized_df = self.normalize_data(df)
            
            # Étape 4: Insertion en base de données SQLite
            count = self.db.insert_from_dataframe(normalized_df)
            
            # Succès : retour des informations
            return {
                "success": True,
                "message": f"{count} employés importés avec succès",
                "imported": count,
                "errors": 0,
                "error_details": []
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "message": "Fichier non trouvé",
                "imported": 0,
                "errors": 1,
                "error_details": ["Fichier non trouvé"]
            }
        except pd.errors.EmptyDataError:
            return {
                "success": False,
                "message": "Le fichier Excel est vide ou corrompu",
                "imported": 0,
                "errors": 1,
                "error_details": ["Le fichier Excel est vide ou corrompu"]
            }
        except KeyError as e:
            return {
                "success": False,
                "message": f"Colonne manquante dans le fichier Excel: {str(e)}",
                "imported": 0,
                "errors": 1,
                "error_details": [f"Colonne manquante: {str(e)}"]
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur lors de l'import: {str(e)}",
                "imported": 0,
                "errors": 1,
                "error_details": [f"Erreur: {str(e)}"]
            }
    
    def normalize_data(self, df):
        """
        Normalise les différents formats Excel vers une structure unique.
        Gère vos 2 formats : employees-1.xlsx et employees-2.xlsx
        
        Args:
            df (pandas.DataFrame): DataFrame lu depuis Excel
            
        Returns:
            pandas.DataFrame: DataFrame normalisé pour la base de données
        """
        # Création du DataFrame de sortie normalisé
        normalized = pd.DataFrame()
        
        # Colonnes communes obligatoires (présentes dans les 2 formats)
        try:
            normalized['nom'] = df['Nom']
            normalized['email'] = df['Email'] 
            normalized['salaire'] = df['Salaire']
        except KeyError as e:
            raise KeyError(f"Colonne obligatoire manquante: {str(e)}")
        
        # Gestion des différentes combinaisons de colonnes possibles
        # Colonnes téléphone (plusieurs noms possibles)
        if 'Téléphone' in df.columns:
            normalized['telephone'] = df['Téléphone']
        elif 'Phone' in df.columns:
            normalized['telephone'] = df['Phone']
        else:
            normalized['telephone'] = None
            
        # Colonnes département 
        if 'Département' in df.columns:
            normalized['departement'] = df['Département']
        else:
            normalized['departement'] = None
            
        # Colonnes poste
        if 'Poste' in df.columns:
            normalized['poste'] = df['Poste']
        else:
            normalized['poste'] = None
        
        # Nettoyage des données : remplacement des NaN et valeurs vides par None
        normalized = normalized.where(pd.notnull(normalized), None)
        
        # Nettoyage spécifique des chaînes vides et 'None' 
        for col in ['telephone', 'departement', 'poste']:
            if col in normalized.columns:
                normalized[col] = normalized[col].replace(['', 'None', 'none', 'NONE'], None)
        
        return normalized
    
    def export_to_excel(self, filename="export_employees.xlsx"):
        """
        Exporte toutes les données de la base SQLite vers un fichier Excel.
        Fonctionnalité 4 du hackathon : EXPORT vers Excel
        
        Args:
            filename (str): Nom du fichier Excel à créer
            
        Returns:
            dict: {
                "success": bool,
                "message": str,
                "filename": str ou None
            }
        """
        try:
            # Étape 1: Récupération de toutes les données depuis la base
            df = self.db.get_all_data()
            
            # Étape 2: Vérification qu'il y a des données à exporter
            if df.empty:
                return {
                    "success": False,
                    "message": "Aucune donnée à exporter",
                    "filename": None
                }
            
            # Étape 3: Export vers Excel avec pandas
            df.to_excel(filename, index=False, engine='openpyxl')
            
            # Succès
            return {
                "success": True,
                "message": f"{len(df)} employés exportés vers {filename}",
                "filename": filename
            }
            
        except PermissionError:
            return {
                "success": False,
                "message": f"Permission refusée : le fichier {filename} est peut-être ouvert",
                "filename": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur lors de l'export: {str(e)}",
                "filename": None
            }
    
    def get_statistics(self):
        """
        Calcule des statistiques sur les données pour le dashboard.
        Utilisé pour l'affichage structuré (Fonctionnalité 2).
        
        Returns:
            dict: Dictionnaire contenant les statistiques principales
        """
        # Récupération des données
        df = self.db.get_all_data()
        
        # Si pas de données, retourner des statistiques vides
        if df.empty:
            return {
                'total_employes': 0,
                'salaire_moyen': 0,
                'salaire_min': 0,
                'salaire_max': 0,
                'nombre_departements': 0,
                'nombre_postes': 0
            }
        
        # Calcul des statistiques avec gestion des erreurs
        try:
            stats = {
                'total_employes': len(df),
                'salaire_moyen': df['salaire'].mean() if 'salaire' in df.columns else 0,
                'salaire_min': df['salaire'].min() if 'salaire' in df.columns else 0,
                'salaire_max': df['salaire'].max() if 'salaire' in df.columns else 0,
                'nombre_departements': df['departement'].nunique() if 'departement' in df.columns else 0,
                'nombre_postes': df['poste'].nunique() if 'poste' in df.columns else 0
            }
            
            # Arrondir les valeurs monétaires
            for key in ['salaire_moyen', 'salaire_min', 'salaire_max']:
                if stats[key]:
                    stats[key] = round(stats[key], 2)
                    
            return stats
            
        except Exception as e:
            # En cas d'erreur, retourner des stats par défaut
            return {
                'total_employes': len(df),
                'salaire_moyen': 0,
                'salaire_min': 0, 
                'salaire_max': 0,
                'nombre_departements': 0,
                'nombre_postes': 0,
                'erreur': str(e)
            }
    
    def validate_excel_format(self, df):
        """
        Valide que le fichier Excel contient les colonnes minimales requises.
        
        Args:
            df (pandas.DataFrame): DataFrame à valider
            
        Returns:
            tuple: (valide: bool, format_detecte: str, erreurs: list)
        """
        # Colonnes obligatoires communes aux 2 formats
        required_columns = ['Nom', 'Email', 'Salaire']
        
        # Vérification des colonnes obligatoires
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, "Format inconnu", [f"Colonnes manquantes: {', '.join(missing_columns)}"]
        
        # Détection du format spécifique
        format_1_cols = ['Téléphone', 'Département']  # employees-1.xlsx
        format_2_cols = ['Phone', 'Poste']            # employees-2.xlsx
        
        if all(col in df.columns for col in format_1_cols):
            return True, "employees-1", []
        elif all(col in df.columns for col in format_2_cols):
            return True, "employees-2", []
        else:
            return True, "Format partiel", ["Certaines colonnes optionnelles manquent"]
    
    def get_data_preview(self, max_rows=5):
        """
        Retourne un aperçu des données actuelles (pour l'affichage).
        
        Args:
            max_rows (int): Nombre maximum de lignes à retourner
            
        Returns:
            pandas.DataFrame: Aperçu des données
        """
        df = self.db.get_all_data()
        return df.head(max_rows) if not df.empty else pd.DataFrame()