import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.title(" Application de Traitement des Données Avant Intégration sur IGOR")

st.markdown(
    """
Cette application permet de charger plusieurs fichiers Excel, extraire les données, les nettoyer et générer un fichier CSV propre prêt à être intégré dans le système de la banque.
"""
)

uploaded_files = st.file_uploader(
    " Charger les fichiers Excel", type=["xls", "xlsx"], accept_multiple_files=True
)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        xls = pd.ExcelFile(uploaded_file)
        for sheet_name in xls.sheet_names:
            try:
                df = xls.parse(sheet_name)
                df = df.rename(columns=lambda x: x.strip().lower())
                columns_mapping = {
                    "date de l’opération": "date_operation",
                    "date de l'operation": "date_operation",
                    "montant de l’opération": "montant",
                    "montant de l'operation": "montant",
                    "libellé de l’opération": "libelle",
                    "libelle de l'operation": "libelle",
                    "référence du compte": "reference",
                    "reference du compte": "reference",
                }
                df = df.rename(columns=columns_mapping)
                required_columns = [
                    "date_operation",
                    "montant",
                    "libelle",
                    "reference",
                ]
                if not all(col in df.columns for col in required_columns):
                    continue
                df = df[required_columns].copy()
                df["date_oper"] = pd.to_datetime("1900-01-01")
                df["date_transaction"] = pd.to_datetime(
                    df["date_operation"], errors="coerce"
                )
                df["date_transaction"] = df["date_transaction"].fillna(
                    datetime.datetime.today()
                )
                df["montant_crediter"] = df["montant"].apply(lambda x: x if x > 0 else 0)
                df["montant_debiter"] = df["montant"].apply(lambda x: abs(x) if x < 0 else 0)
                df["devise"] = "XOF"
                df = df[
                    [
                        "reference",
                        "date_oper",
                        "date_transaction",
                        "montant_crediter",
                        "montant_debiter",
                        "libelle",
                        "devise",
                    ]
                ]
                df = df[
                    (df["montant_crediter"] != 0) | (df["montant_debiter"] != 0)
                ]
                df['reference']= '0' + df['reference].astype(str)
                all_data.append(df)
            except Exception as e:
                st.error(
                    f"Erreur lors de la lecture de la feuille '{sheet_name}' : {e}"
                )
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        st.success(" Traitement terminé !")
        st.dataframe(final_df.head(20))
        output = BytesIO()
        final_df.to_csv(output, index=False)
        output.seek(0)
        st.download_button(
            label=" Télécharger le fichier CSV final",
            data=output,
            file_name="donnees_traitees.csv",
            mime="text/csv",
        )
    else:
        st.warning("Aucune donnée valide trouvée dans les fichiers téléchargés.")
