import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def process_files(file_paths):
    # Préparer une liste pour stocker les données traitées
    processed_data = []

    for file_path in file_paths:
        # Lire chaque feuille d'Excel
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Traiter les colonnes requises
            for _, row in df.iterrows():
                reference_compte = row["Référence du compte"]
                date_operation = row["Date de l’opération"]
                montant_operation = row["Montant de l’opération"]
                libelle_operation = row["Libellé de l’opération"]
                
                # Vérifier si la date est différente d'aujourd'hui
                if date_operation.date() != datetime.today().date():
                    date_operation = datetime(1900, 1, 1)
                
                # Déterminer si c'est un crédit ou un débit
                if montant_operation > 0:
                    montant_crediter = montant_operation
                    montant_debiter = 0
                else:
                    montant_crediter = 0
                    montant_debiter = abs(montant_operation)

                # Ajouter les données traitées à la liste
                processed_data.append({
                    "Référence du compte": reference_compte,
                    "Date de l'opération": date_operation,
                    "Montant créditer": montant_crediter,
                    "Montant débiter": montant_debiter,
                    "Libellé de l’opération": libelle_operation,
                    "Devise": "EUR"  # Exemple de devise
                })
    
    # Convertir en DataFrame et supprimer les lignes vides
    final_df = pd.DataFrame(processed_data)
    final_df = final_df[(final_df["Montant créditer"] != 0) | (final_df["Montant débiter"] != 0)]
    
    # Enregistrer dans un nouveau fichier CSV
    final_df.to_csv("donnees_traitees.csv", index=False)

def upload_files():
    file_paths = filedialog.askopenfilenames(title="Choisir les fichiers Excel", filetypes=[("Excel files", ".xlsx;.xls")])
    if file_paths:
        process_files(file_paths)
        print("Traitement terminé ! Le fichier 'donnees_traitees.csv' a été créé.")

# Interface graphique
root = tk.Tk()
root.title("Outil de traitement de données bancaires")
upload_button = tk.Button(root, text="Charger les fichiers Excel", command=upload_files)
upload_button.pack(pady=20)

root.mainloop()