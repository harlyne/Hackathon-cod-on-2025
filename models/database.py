import sqlite3
import pandas as pd

class EmployeeDatabase:
    """
    Classe de gestion de la base de données SQLite pour les employés.
    Implémente les opérations CRUD (Create, Read, Update, Delete).
    """
    
    def __init__(self, db_path="employees.db"):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path (str): Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """
        Crée la table employees si elle n'existe pas.
        Structure: id, nom, email, telephone, departement, poste, salaire
        """
        # Connexion à la base SQLite
        conn = sqlite3.connect(self.db_path)
        
        # Création de la table avec tous les champs nécessaires
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT,
                telephone TEXT,
                departement TEXT,
                poste TEXT,
                salaire REAL
            )
        """)
        
        # Validation des changements
        conn.commit()
        conn.close()
        print("Base de données initialisée avec succès")
    
    def insert_from_dataframe(self, df):
        """
        Insère les données d'un DataFrame pandas dans la table employees.
        
        Args:
            df (pandas.DataFrame): DataFrame contenant les données à insérer
            
        Returns:
            int: Nombre de lignes insérées
        """
        # Connexion à la base
        conn = sqlite3.connect(self.db_path)
        
        # Insertion en masse via pandas (append = ajouter aux données existantes)
        df.to_sql('employees', conn, if_exists='append', index=False)
        
        # Validation et fermeture
        conn.commit()
        conn.close()
        
        return len(df)
    
    def get_all_data(self):
        """
        Récupère toutes les données de la table employees.
        
        Returns:
            pandas.DataFrame: DataFrame contenant tous les employés
        """
        # Connexion et requête SELECT
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        
        return df
    
    def update_employee(self, employee_id, field, new_value):
        """
        Met à jour un champ spécifique d'un employé.
        
        Args:
            employee_id (int): ID de l'employé à modifier
            field (str): Nom du champ à modifier (nom, email, telephone, etc.)
            new_value: Nouvelle valeur à assigner
        """
        # Connexion à la base
        conn = sqlite3.connect(self.db_path)
        
        # Requête UPDATE sécurisée avec paramètres (évite l'injection SQL)
        conn.execute(f"UPDATE employees SET {field} = ? WHERE id = ?", (new_value, employee_id))
        
        # Validation et fermeture
        conn.commit()
        conn.close()
    
    def delete_employee(self, employee_id):
        """
        Supprime un employé de la base de données.
        
        Args:
            employee_id (int): ID de l'employé à supprimer
        """
        # Connexion à la base
        conn = sqlite3.connect(self.db_path)
        
        # Requête DELETE sécurisée
        conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        # Validation et fermeture
        conn.commit()
        conn.close()
    
    def clear_all_data(self):
        """
        Supprime toutes les données de la table (utile pour les tests).
        ATTENTION: Cette opération est irréversible.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM employees")
        conn.commit()
        conn.close()
    
    def get_employee_count(self):
        """
        Retourne le nombre total d'employés dans la base.
        
        Returns:
            int: Nombre d'employés
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        conn.close()
        
        return count