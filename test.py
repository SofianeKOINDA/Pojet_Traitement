import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import os
from io import StringIO

def try_read_xls(uploaded_file):
    try:
        # Essaye de lire comme un vrai Excel
        return pd.ExcelFile(uploaded_file), None, False
    except Exception:
        try:
            # Rewind le fichier pour relire
            uploaded_file.seek(0)
            # Essaye de lire comme un CSV tabulé (faux xls)
            content = uploaded_file.read()
            # Si bytes, décoder
            if isinstance(content, bytes):
                content = content.decode(errors='replace')
            # Essaye d'abord avec tabulation, puis espaces multiples si besoin
            try:
                df = pd.read_csv(StringIO(content), sep='\t', engine='python', header=None)
                if df.shape[1] < 3:  # Si toujours peu de colonnes, essaye avec espaces multiples
                    df = pd.read_csv(StringIO(content), sep='\s+', engine='python', header=None)
            except Exception:
                df = pd.read_csv(StringIO(content), sep='\s+', engine='python', header=None)
            return df, None, True  # On retourne le DataFrame directement, et un flag pour indiquer que c'est un DataFrame
        except Exception as e:
            return None, e, False

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
        # Conversion automatique si .xls
        file_name = uploaded_file.name.lower()
        if file_name.endswith('.xls'):
            xls, err, is_df = try_read_xls(uploaded_file)
            if xls is None:
                st.error(f"Erreur lors de la conversion du fichier {uploaded_file.name} : {err}")
                continue
        else:
            try:
                xls = pd.ExcelFile(uploaded_file)
                is_df = False
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier {uploaded_file.name} : {e}")
                continue
        if is_df:
            # On a un DataFrame déjà prêt (issu d'un faux xls)
            df = xls
            # Prend les 5 premières colonnes si elles existent
            df = df.iloc[:, :5]
            df.columns = ["date", "montant", "libelle", "reference", "client"][:df.shape[1]]
            # On ne garde que les 4 premières colonnes utiles pour le traitement
            df = df[["date", "montant", "libelle", "reference"]]
            if df.shape[1] < 4 or df.shape[0] == 0:
                continue
            df.columns = ["date", "montant", "libelle", "reference"]
            # Conversion de la colonne montant en numérique, remplace les erreurs par 0
            df["montant"] = df["montant"].astype(str).str.replace(",", ".").str.replace(" ", "")
            df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0)
            required_columns = [
                "date",
                "montant",
                "libelle",
                "reference",
            ]
            if not all(col in df.columns for col in required_columns):
                continue
            df = df[required_columns].copy()
            df["date_oper"] = datetime.datetime.today()
            df["date_transaction"] = pd.to_datetime(
                df["date"], errors="coerce"
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
            df['reference'] = '0' + df['reference'].astype(str)
            all_data.append(df)
        else:
            for sheet_name in xls.sheet_names:
                try:
                    df = xls.parse(sheet_name, header=None)
                    # Prend les 5 premières colonnes si elles existent
                    df = df.iloc[:, :5]
                    df.columns = ["date", "montant", "libelle", "reference", "client"][:df.shape[1]]
                    # On ne garde que les 4 premières colonnes utiles pour le traitement
                    df = df[["date", "montant", "libelle", "reference"]]
                    if df.shape[1] < 4 or df.shape[0] == 0:
                        continue
                    df.columns = ["date", "montant", "libelle", "reference"]
                    # Conversion de la colonne montant en numérique, remplace les erreurs par 0
                    df["montant"] = df["montant"].astype(str).str.replace(",", ".").str.replace(" ", "")
                    df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0)
                    required_columns = [
                        "date",
                        "montant",
                        "libelle",
                        "reference",
                    ]
                    if not all(col in df.columns for col in required_columns):
                        continue
                    df = df[required_columns].copy()
                    df["date_oper"] = datetime.datetime.today()
                    df["date_transaction"] = pd.to_datetime(
                        df["date"], errors="coerce"
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
                    df['reference'] = '0' + df['reference'].astype(str)
                    all_data.append(df)
                except Exception as e:
                    st.error(
                        f"Erreur lors de la lecture de la feuille '{sheet_name}' : {e}"
                    )
                #après traitement des données, le fichiercsv peut maintenant être téléchargé     
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        st.success(" Traitement terminé !")
        st.dataframe(final_df.head(20))
        output = BytesIO()
        final_df.to_csv(output, index=False, header=False)
        output.seek(0)
        st.download_button(
            label=" Télécharger le fichier CSV final",
            data=output,
            file_name="donnees_traitees.csv",
            mime="text/csv",
        )
    else:
        st.warning("Aucune donnée valide trouvée dans les fichiers téléchargés.")
