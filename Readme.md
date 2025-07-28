# Application de Traitement des Données Avant Intégration sur IGOR

Cette application permet de charger plusieurs fichiers Excel (ou CSV déguisés en .xls), d'extraire les données, de les nettoyer et de générer un fichier CSV propre prêt à être intégré dans le système de la banque, IGOR.

## Fonctionnalités principales
- Import de plusieurs fichiers Excel (.xls, .xlsx)
- Détection automatique des faux fichiers Excel (CSV renommés)
- Nettoyage et conversion des données (dates, montants, etc.)
- Génération d'un fichier CSV final 
- Téléchargement du fichier CSV prêt à l'emploi

## Utilisation

1. **Installation des dépendances**

Assurez-vous d'avoir Python 3.7+ installé.

Installez les dépendances nécessaires :
```bash
pip install streamlit pandas openpyxl
```

2. **Lancement de l'application**

Dans le dossier du projet, lancez :
```bash
streamlit run main.py
```

3. **Utilisation de l'interface**
- Chargez un ou plusieurs fichiers Excel (.xls ou .xlsx)
- L'application traite automatiquement les fichiers et affiche un aperçu
- Téléchargez le fichier CSV final généré

## Structure attendue des fichiers

Les fichiers doivent contenir au moins les colonnes suivantes (dans cet ordre) :
- date
- montant (avec virgule comme séparateur décimal)
- libellé
- référence

Une colonne supplémentaire (ex : client) peut être présente mais sera ignorée.

## Remarques
- Les montants au format français (ex : 1234,56) sont automatiquement convertis.
- Les lignes sans montant valide sont ignorées.
- Le fichier CSV généré ne contient que les colonnes nécessaires à l'intégration IGOR.

## Auteur
- Benewende Sofiane KOINDA Stagiaire en IT à BANK OF AFRICA