import pandas as pd
import datetime
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

def generate_comprehensive_facture_excel(data: list[dict], client_full_name: str):
    safe_client_name = "".join(c for c in client_full_name if c.isalnum() or c in (' ', '-', '_')).replace(' ',
                                                                                                           '_').rstrip(
        '_')
    #file_name = f"Rapport_Factures_{safe_client_name}_{report_period.replace(' ', '_')}.xlsx"
    file_name = f"Rapport_Factures_{safe_client_name}.xlsx"

    wb = Workbook()
    ws = wb.active
    #ws.title = f"Factures {client_full_name} {report_period}"
    ws.title = f"Factures ce {client_full_name} "

    # Styles
    bold_font = Font(bold=True)
    header_font = Font(bold=True, size=14)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                         bottom=Side(style='thin'))

    # Définition des couleurs de remplissage
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Vert clair
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Rouge clair

    current_row = 1

    # Informations du client (en-tête)
    if data:
        client_info = data[0]  # Prendre les infos du premier enregistrement pour le client
        client_display_name = f"{client_info['client_nom']} {client_info['client_prenom']}"
        if client_info['client_categorie'] != 'Particulier':
            client_display_name = f"{client_info['client_nom']} (Responsable: {client_info['client_prenom'] if client_info['client_prenom'] else 'N/A'})"

        ws.cell(row=current_row, column=1, value="Client :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_display_name)
        current_row += 1

        ws.cell(row=current_row, column=1, value="Adresse :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_adresse'])
        current_row += 1

        ws.cell(row=current_row, column=1, value="Téléphone :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_telephone'])
        current_row += 1

        ws.cell(row=current_row, column=1, value="Catégorie Client :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_categorie'])
        current_row += 1

    current_row += 1  # Ligne vide

    # Ligne de titre du rapport
    ws.cell(row=current_row, column=1,
            value=f"Rapport de Facturation pour la période : 2025").font = header_font
    # Fusionner les cellules pour le titre, en fonction du nombre maximum de colonnes du tableau
    max_cols_for_merge = 13  # This should match the number of columns in table_headers
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=max_cols_for_merge)
    ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center')
    current_row += 2  # Deux lignes vides après pour la séparation avec le tableau

    # Tableau des détails de la facture
    table_headers = [
        'ID Contrat', 'Date Contrat', 'Début Contrat', 'Fin Contrat', 'Statut Contrat', 'Durée Contrat',
        'Type de Traitement', 'Redondance (Mois)', 'Date de Planification', 'Etat du Planning',
        'Date de Facturation', 'Etat de Paiement', 'Montant Facturé'
    ]

    # Écrire les en-têtes du tableau
    for col_idx, header in enumerate(table_headers, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=header)
        cell.font = bold_font
        cell.border = thin_border
    current_row += 1

    if not data:
        ws.cell(row=current_row, column=1,
                value=f"Aucune facture trouvée pour le client '{client_full_name}' pour la période sélectionnée.").border = thin_border
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=len(table_headers))
        current_row += 1
    else:
        # Préparer les données pour le tableau
        df_invoice_data = pd.DataFrame(data)

        # S'assurer que les dates sont au format 'YYYY-MM-DD' pour l'affichage
        # Appliquer une fonction de formatage pour les dates/datetimes
        def format_date_if_datetime(val):
            if isinstance(val, (datetime.date, datetime.datetime)):
                return val.strftime('%Y-%m-%d')
            return val

        # Appliquer le formatage aux colonnes de date spécifiques
        date_cols = ['Date Contrat', 'Début Contrat', 'Fin Contrat', 'Date de Planification', 'Date de Facturation']
        for col in date_cols:
            # Vérifier si la colonne existe dans le DataFrame avant d'essayer de la formater
            if col in df_invoice_data.columns:
                df_invoice_data[col] = df_invoice_data[col].apply(format_date_if_datetime)

        # Réordonner les colonnes pour l'affichage selon table_headers
        # Utiliser .reindex pour s'assurer que l'ordre est correct et que les colonnes manquantes sont gérées (bien que non attendu ici)
        df_display = df_invoice_data.reindex(columns=table_headers)

        # Écrire les données du tableau et appliquer la couleur
        for r_idx, row_data in enumerate(df_display.values.tolist(), start=current_row):
            # Déterminer la couleur de remplissage basée sur l'état de paiement
            # 'Etat de Paiement' est la 12ème colonne dans table_headers (index 11)
            payment_status = row_data[11]
            fill_to_apply = None
            if payment_status == 'Payé':
                fill_to_apply = green_fill
            elif payment_status == 'Non payé':
                fill_to_apply = red_fill

            for c_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.border = thin_border
                if fill_to_apply:
                    cell.fill = fill_to_apply
            current_row += 1

    current_row += 1  # Ligne vide avant les totaux

    # Calcul et affichage des totaux
    if data:
        df_calc = pd.DataFrame(data)  # Utilise le DataFrame complet

        # Total général
        grand_total = df_calc['Montant Facturé'].sum()
        ws.cell(row=current_row, column=1, value="Montant Total Facturé sur la période :").font = bold_font
        ws.cell(row=current_row, column=len(table_headers), value=grand_total).font = bold_font
        current_row += 1

        # Total payé
        total_paid = df_calc[df_calc['Etat de Paiement'] == 'Payé']['Montant Facturé'].sum()
        ws.cell(row=current_row, column=1, value="Montant Total Payé sur la période :").font = bold_font
        ws.cell(row=current_row, column=len(table_headers), value=total_paid).font = bold_font
        ws.cell(row=current_row, column=len(table_headers)).fill = green_fill
        current_row += 1

        # Total impayé
        total_unpaid = df_calc[df_calc['Etat de Paiement'] == 'Non payé']['Montant Facturé'].sum()
        ws.cell(row=current_row, column=1, value="Montant Total Impayé sur la période :").font = bold_font
        ws.cell(row=current_row, column=len(table_headers), value=total_unpaid).font = bold_font
        ws.cell(row=current_row, column=len(table_headers)).fill = red_fill
        current_row += 1

        current_row += 1  # Ligne vide

        # Totaux par type de traitement (tous statuts)
        ws.cell(row=current_row, column=1, value="Synthèse par Type de Traitement :").font = bold_font
        current_row += 1

        # S'assurer que 'Type de Traitement' est une colonne pour le groupby
        if 'Type de Traitement' in df_calc.columns:
            total_by_type = df_calc.groupby('Type de Traitement')['Montant Facturé'].sum().reset_index()
            for _, row in total_by_type.iterrows():
                ws.cell(row=current_row, column=2, value=row['Type de Traitement']).font = bold_font
                ws.cell(row=current_row, column=3, value=row['Montant Facturé']).font = bold_font
                current_row += 1
        else:
            ws.cell(row=current_row, column=1,
                    value="Impossible de synthétiser par type de traitement (colonne manquante).")
            current_row += 1

    # Ajuster la largeur des colonnes
    for i in range(1, len(table_headers) + 1):
        column_letter = get_column_letter(i)
        length = 0
        for row_idx in range(1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=i)
            if cell.value is not None:
                # Gérer les dates et autres types pour la longueur
                if isinstance(cell.value, (datetime.date, datetime.datetime)):
                    cell_length = len(cell.value.strftime('%Y-%m-%d'))  # Format standard de date
                else:
                    cell_length = len(str(cell.value))
                length = max(length, cell_length)
        ws.column_dimensions[column_letter].width = length + 2

    try:
        output = BytesIO()
        wb.save(output)
        with open(file_name, 'wb') as f:
            f.write(output.getvalue())

        print(f"Fichier '{file_name}' généré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la génération du fichier Excel de la facture : {e}")

def generate_facture_excel(data: list[dict], client_full_name: str, year: int, month: int):
    month_name_fr = datetime.date(year, month, 1).strftime('%B').capitalize()

    safe_client_name = "".join(c for c in client_full_name if c.isalnum() or c in (' ', '-', '_')).replace(' ',
                                                                                                           '_').rstrip(
        '_')
    file_name = f"{safe_client_name}-{month_name_fr}-{year}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = f"Facture {client_full_name} {month_name_fr}"

    # Styles
    bold_font = Font(bold=True)
    header_font = Font(bold=True, size=14)
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    current_row = 1

    # Informations du client (en-tête)
    if data:
        client_info = data[0]
        client_display_name = f"{client_info['client_nom']} {client_info['client_prenom']}"
        if client_info['client_categorie'] != 'Particulier':
            client_display_name = f"{client_info['client_nom']} (Responsable: {client_info['client_prenom']})"

        ws.cell(row=current_row, column=1, value="Client :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_display_name)
        current_row += 1

        ws.cell(row=current_row, column=1, value="Adresse :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_adresse'])
        current_row += 1

        ws.cell(row=current_row, column=1, value="Téléphone :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_telephone'])
        current_row += 1

        ws.cell(row=current_row, column=1, value="Catégorie Client :").font = bold_font
        ws.cell(row=current_row, column=2, value=client_info['client_categorie'])
        current_row += 1

    current_row += 1  # Ligne vide

    # Ligne "Facture du mois de:"
    # Adjusted num_table_cols to account for the 'Montant' column being added to the display
    num_table_cols = 5
    ws.cell(row=current_row, column=1, value=f"Facture du mois de : {month_name_fr} {year}").font = header_font
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=num_table_cols)
    ws.cell(row=current_row, column=1).alignment = Alignment(horizontal='center')
    current_row += 2  # Deux lignes vides après pour la séparation avec le tableau

    # Tableau des traitements - Ajout de la colonne 'Montant'
    table_headers = ['Date de traitement', 'Traitement (Type)', 'Etat traitement', 'Etat paiement (Payée ou non)', 'Montant']

    # Écrire les en-têtes du tableau
    for col_idx, header in enumerate(table_headers, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=header)
        cell.font = bold_font
        cell.border = thin_border
    current_row += 1

    if not data:
        ws.cell(row=current_row, column=1,
                value=f"Aucune facture trouvée pour le client '{client_full_name}' pour ce mois.").border = thin_border
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=len(table_headers))
        current_row += 1
    else:
        df_invoice_data = pd.DataFrame(data)
        # Sélectionner et réordonner les colonnes pour l'affichage du tableau
        df_display = df_invoice_data[
            ['Date de traitement', 'Traitement (Type)', 'Etat traitement', 'Etat paiement (Payée ou non)', 'montant_facture']]
        df_display.rename(columns={'montant_facture': 'Montant'}, inplace=True) # Renommer pour l'affichage

        # Écrire les données du tableau
        for r_idx, row_data in enumerate(df_display.values.tolist(), start=current_row):
            for c_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.border = thin_border
            current_row += 1

    current_row += 1  # Ligne vide avant les totaux

    # Calcul et affichage des totaux
    if data:
        df_calc = pd.DataFrame(data)  # Utilise le DataFrame complet avec montant_facture

        # Total par type de traitement (seulement payé)
        total_by_type_paid = df_calc[df_calc['Etat paiement (Payée ou non)'] == 'Payé'].groupby('Traitement (Type)')[
            'montant_facture'].sum()

        if not total_by_type_paid.empty:
            ws.cell(row=current_row, column=1, value="Facture total pour :").font = bold_font
            current_row += 1
            for service_type, total_amount in total_by_type_paid.items():
                ws.cell(row=current_row, column=2, value=f"{service_type} (Payé)").font = bold_font
                ws.cell(row=current_row, column=3, value=total_amount).font = bold_font
                current_row += 1
        else:
            ws.cell(row=current_row, column=1,
                    value="Aucun montant payé pour les types de traitement ce mois.").font = bold_font
            current_row += 1

        current_row += 1  # Ligne vide

        # Montant total pour tous les traitements effectués (même non payés)
        grand_total = df_calc['montant_facture'].sum()
        ws.cell(row=current_row, column=1, value="Montant total des traitements effectués ce mois :").font = bold_font
        ws.cell(row=current_row, column=3, value=grand_total).font = bold_font
        current_row += 1

    # Ajuster la largeur des colonnes
    max_col_for_width = max(num_table_cols, 3)

    for i in range(1, max_col_for_width + 1):
        column_letter = get_column_letter(i)
        length = 0
        for row_idx in range(1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=i)
            if cell.value is not None:
                length = max(length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = length + 2

    try:
        output = BytesIO()
        wb.save(output)
        with open(file_name, 'wb') as f:
            f.write(output.getvalue())

        print(f"Fichier '{file_name}' généré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la génération du fichier Excel de la facture : {e}")

def generate_traitements_excel(data: list[dict], year: int, month: int):
    month_name_fr = datetime.date(year, month, 1).strftime('%B').capitalize()
    file_name = f"traitements-{month_name_fr}-{year}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = f"Traitements {month_name_fr} {year}"

    # Styles
    bold_font = Font(bold=True)
    header_font = Font(bold=True, size=14)
    center_align = Alignment(horizontal='center', vertical='center')

    # Définition des couleurs de remplissage
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Rouge clair
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # Vert clair

    # Titre du rapport
    ws.cell(row=1, column=1, value=f"Rapport des Traitements du mois de {month_name_fr} {year}").font = header_font
    ws.cell(row=1, column=1).alignment = center_align
    num_data_cols = 7
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_data_cols)

    # Nombre total de traitements
    total_traitements = len(data)
    ws.cell(row=3, column=1, value=f"Nombre total de traitements ce mois-ci : {total_traitements}").font = bold_font

    # Ligne vide pour la séparation
    ws.cell(row=4, column=1, value="")

    df = pd.DataFrame(data)

    if df.empty:
        ws.cell(row=5, column=1, value="Aucun traitement trouvé pour ce mois.")
    else:
        headers = df.columns.tolist()
        # Trouvez l'index de la colonne 'Etat traitement'
        status_col_idx = -1
        try:
            status_col_idx = headers.index('Etat traitement')
        except ValueError:
            print("AVERTISSEMENT: La colonne 'Etat traitement' n'a pas été trouvée dans les données. Les couleurs ne seront pas appliquées.")


        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=5, column=col_idx, value=header)
            cell.font = bold_font

        # Itérer sur les données et appliquer la couleur
        for r_idx, row_dict in enumerate(data, start=6): # Utiliser les dictionnaires directement pour accéder au statut
            # Utiliser les valeurs du dictionnaire pour écrire les cellules
            for c_idx, (col_name, value) in enumerate(row_dict.items(), 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)

                # Appliquer la couleur si c'est la colonne 'Etat traitement'
                if col_name == 'Etat traitement':
                    if value == 'Effectué':
                        cell.fill = red_fill
                    elif value == 'À venir': # Assurez-vous que cette valeur correspond à votre ENUM
                        cell.fill = green_fill

    max_col_for_width = len(df.columns) if not df.empty else num_data_cols

    for i in range(1, max_col_for_width + 1):
        column_letter = get_column_letter(i)
        length = 0
        for row_idx in range(1, ws.max_row + 1):
            cell = ws.cell(row=row_idx, column=i)
            if cell.value is not None:
                length = max(length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = length + 2

    try:
        output = BytesIO()
        wb.save(output)
        with open(file_name, 'wb') as f:
            f.write(output.getvalue())

        print(f"Fichier '{file_name}' généré avec succès.")
    except Exception as e:
        print(f"Erreur lors de la génération du fichier Excel des traitements : {e}")
