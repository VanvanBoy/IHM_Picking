import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import mysql.connector
import pandas as pd

class DBManager:
    def __init__(self):
        self.config = {
            'user': 'Vanvan',
            'password': 'VoltR99!', 
            'host': '34.77.226.40', 
            'database': 'cellules_batteries_cloud',
            'auth_plugin': 'mysql_native_password'
        }
    
    def connect(self):
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur DB", f"Erreur lors de la connexion : {err}")
            return None

class StockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de Stock Usine - Plateaux & Emplacements")
        self.geometry("1500x1000")  
        self.db_manager = DBManager()
        
        self.picking_file_path = None
        
        self.create_widgets()

        # Intercepte la fermeture par la croix
        self.protocol("WM_DELETE_WINDOW", self.disable_close)


    def disable_close(self):
        messagebox.showwarning("Action interdite", "Veuillez utiliser le bouton 'Fermer l'application' pour quitter.")

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # Onglet Mise en Plateaux
        tab_mise = ttk.Frame(notebook)
        notebook.add(tab_mise, text="Mise en Plateaux")
        self.setup_mise_en_plateaux(tab_mise)

        # Onglet Picking
        tab_picking = ttk.Frame(notebook)
        notebook.add(tab_picking, text="Picking Plateaux")
        self.setup_picking(tab_picking)

        # Onglet Visualisation
        tab_visu = ttk.Frame(notebook)
        notebook.add(tab_visu, text="Visualisation Plateaux")
        self.setup_visualisation(tab_visu)
        
        # Bouton pour fermer l'application
        close_button = tk.Button(self, text="Fermer l'application", command=self.close_app, bg="#DD5049", fg="White")
        close_button.pack(side='bottom', pady=5)

    # -------------------------------
    # Onglet Mise en Plateaux
    # -------------------------------
    def setup_mise_en_plateaux(self, frame):
        label_info = tk.Label(frame, text="Attribuer une cellule à un emplacement d'un plateau")
        label_info.pack(pady=5)

        # --- Frame principale en deux lignes : top (entrées), bottom (Treeview) ---
        top_frame = tk.Frame(frame)
        top_frame.pack(fill='x', padx=10, pady=5)

        bottom_frame = tk.Frame(frame)
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Partie gauche : cellules a mettre en plateau ---
        left_inputs = tk.Frame(top_frame)
        left_inputs.pack(side="left", fill='y', expand=True)

        tk.Label(left_inputs, text="Numéro de série de la première cellule :").pack(pady=5)
        self.entry_numero = tk.Entry(left_inputs)
        self.entry_numero.pack(pady=5)

        tk.Label(left_inputs, text="Nom du plateau :").pack(pady=5)
        self.entry_plateau = tk.Entry(left_inputs)
        self.entry_plateau.pack(pady=5)

        self.t_plateau=tk.Label(left_inputs, text="type plateau:")
        self.t_plateau.pack(pady=5)

        tk.Label(left_inputs, text="Nombre de cellules de la batterie à mettre en plateaux :").pack(pady=5)
        self.entry_emplacement = tk.Entry(left_inputs)
        self.entry_emplacement.pack(pady=5)

        btn_submit = tk.Button(left_inputs, text="Placer les cellules", command=self.put_in_plateau, bg="#60CF60", fg="black")
        btn_submit.pack(pady=10)

        # --- Partie droite : recherche/changement de place ---
        right_inputs = tk.Frame(top_frame)
        right_inputs.pack(side="right", fill='y', expand=True)

        tk.Label(right_inputs, text="Numero serie cellule :").pack(pady=5)
        self.entry_add1 = tk.Entry(right_inputs)
        self.entry_add1.pack(pady=5)

        btn_recherche = tk.Button(right_inputs, text="Rechercher emplacement", command=self.on_plateau, bg="#C760F7", fg="black")
        btn_recherche.pack(pady=10)

        btn_retire = tk.Button(right_inputs, text="Retirer du plateau", command=self.off_plateau, bg="#566DF1", fg="black")
        btn_retire.pack(pady=10)

        tk.Label(right_inputs, text="Nouvel emplacement").pack(pady=5)
        self.entry_add2 = tk.Entry(right_inputs)
        self.entry_add2.pack(pady=5)

        btn_switch = tk.Button(right_inputs, text="Changer emplacement", command=self.switch_plateau, bg="#60CF60", fg="black")
        btn_switch.pack(pady=10)

        # --- Treeview en bas ---
        self.tree = ttk.Treeview(bottom_frame, columns=("Colonne1", "Colonne2"), show='headings')
        self.tree.heading("Colonne1", text="numero serie")
        self.tree.heading("Colonne2", text="emplacement")
        self.tree.column("Colonne1", width=100, anchor="center")
        self.tree.column("Colonne2", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def on_plateau(self):
        numero = self.entry_add1.get().strip()
        if not numero:
            messagebox.showwarning("Champ manquant", "Veuillez entrer un numéro de série.")
            return

        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT code_emplacement, plateau_id 
                    FROM emplacement
                    WHERE numero_serie = %s
                """
                cursor.execute(query, (numero,))
                result = cursor.fetchone()
                
                if result:
                    emplacement, plateau_id = result
                    query_plateau = "SELECT id_plateau FROM plateau WHERE id = %s"
                    cursor.execute(query_plateau, (plateau_id,))
                    plateau_name = cursor.fetchone()[0]
                    
                    messagebox.showinfo("Emplacement trouvé", f"Cellule {numero} est à l'emplacement {emplacement} sur le plateau {plateau_name}.")
                else:
                    messagebox.showwarning("Non trouvé", f"Aucun emplacement trouvé pour la cellule {numero}.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la requête : {err}")
            finally:
                cursor.close()
                conn.close()
    
    def off_plateau(self):
        numero = self.entry_add1.get().strip()
        if not numero:
            messagebox.showwarning("Champ manquant", "Veuillez entrer un numéro de série.")
            return

        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    UPDATE emplacement
                    SET est_occupe = FALSE, numero_serie = NULL, date_attribution = NOW() 
                    WHERE numero_serie = %s
                """
                cursor.execute(query, (numero,))
                conn.commit()
                
                messagebox.showinfo("Succès", f"La cellule {numero} a été retirée du plateau.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la mise à jour : {err}")
            finally:
                cursor.close()
                conn.close()
    
    def switch_plateau(self):
        numero = self.entry_add1.get().strip()
        nouvel_emplacement = self.entry_add2.get().strip()
        
        if not numero or not nouvel_emplacement:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Vérifier si la cellule existe
                query_check = "SELECT code_emplacement FROM emplacement WHERE numero_serie = %s"
                cursor.execute(query_check, (numero,))
                result = cursor.fetchone()
                
                if not result:
                    messagebox.showwarning("Non trouvé", f"Aucune cellule trouvée avec le numéro {numero}.")
                    return
                
                # Vérifier si le nouvel emplacement est libre
                query_check_new = "SELECT est_occupe FROM emplacement WHERE code_emplacement = %s"
                cursor.execute(query_check_new, (nouvel_emplacement,))
                is_occupied = cursor.fetchone()[0]
                
                if is_occupied:
                    messagebox.showwarning("Emplacement occupé", f"L'emplacement {nouvel_emplacement} est déjà occupé.")
                    return
                
                # Mettre à jour l'emplacement de la cellule
                query_delete = """
                    UPDATE emplacement
                    SET est_occupe = FALSE, numero_serie = NULL, date_attribution = NOW()
                    WHERE numero_serie = %s
                """

                cursor.execute(query_delete, (numero,))

                query_update = """
                    UPDATE emplacement
                    SET numero_serie = %s, est_occupe = TRUE, date_attribution = NOW() 
                    WHERE code_emplacement = %s
                """
                cursor.execute(query_update, (numero, nouvel_emplacement))
                conn.commit()
                
                messagebox.showinfo("Succès", f"La cellule {numero} a été déplacée vers l'emplacement {nouvel_emplacement}.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la mise à jour : {err}")
            finally:
                cursor.close()
                conn.close()

    def put_in_plateau(self):
        df = pd.DataFrame(columns=["num_serie","emplacement"])
        list_cell=[]
        numero = self.entry_numero.get().strip()
        nom_plateau = self.entry_plateau.get().strip()
        try:
            nb_cells = int(self.entry_emplacement.get().strip())
        except ValueError:
            messagebox.showwarning("Erreur", "Le nombre de cellules doit être un entier.")
            return

        if not numero or not nom_plateau or not nb_cells:
            messagebox.showwarning("Champs manquants", "Veuillez remplir tous les champs.")
            return

        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                num_batt=numero[:9]
                first_id=numero[9:]
                for i in range(nb_cells):
                    num_serie_cell = num_batt + str(int(first_id)+i).zfill(3)
                    list_cell.append(num_serie_cell)
                #Récuperer le type de plateau 
                query_type_plateau = "SELECT type_plateau FROM plateau WHERE id_plateau = %s"
                cursor.execute(query_type_plateau, (nom_plateau,))
                type_plateau = cursor.fetchall()
                if not type_plateau:
                    messagebox.showerror("Erreur", "Le plateau spécifié n'existe pas.")
                    return
                type_plateau = type_plateau[0][0]
                self.t_plateau.config(text=f"type plateau: {type_plateau}")

                # Récupérer l'état de la cellule
                query_cellule = "SELECT etape_processus FROM cellule WHERE numero_serie_cellule = %s"
                cursor.execute(query_cellule, (numero,))
                etat_cellule = cursor.fetchone()[0]
                if etat_cellule !='Testee':
                    messagebox.showerror("Erreur", "La cellule n'est pas dans l'état 'testée'.")
                    return

                # Récupérer l'ID du plateau
                query_plateau = "SELECT id FROM plateau WHERE id_plateau = %s"
                cursor.execute(query_plateau, (nom_plateau,))
                plateau = cursor.fetchall()
                if not plateau:
                    messagebox.showerror("Erreur", "Le plateau spécifié n'existe pas.")
                    return
                plateau_id = plateau[0][0]

                #Récuperer les numeros_cellules deja en plateaux 

                query_num_cell="""
                    SELECT numero_serie FROM emplacement
                """
                cursor.execute(query_num_cell)
                existing_cells = cursor.fetchall()
                if numero in [x[0] for x in existing_cells]:
                    query_place="""
                        SELECT code_emplacement FROM emplacement
                        WHERE numero_serie = %s 
                    """
                    cursor.execute(query_place, (numero,))
                    emplacement = cursor.fetchone()
                    messagebox.showerror("Erreur", "La cellule est deja rangée à l'emplacement "+ str(emplacement[0]) +".")
                    return

                
                # Récupérer l'ID du plateau sélectionné
                query_plateau = "SELECT id FROM plateau WHERE id_plateau = %s"
                cursor.execute(query_plateau, (nom_plateau,))
                plateau_row = cursor.fetchone()
                if not plateau_row:
                    messagebox.showerror("Erreur", "Le plateau spécifié n'existe pas.")
                    return
                plateau_id = plateau_row[0]

                # Récupérer tous les plateaux avec ID >= plateau sélectionné, triés par ID
                query_all_plateaux = """
                    SELECT id FROM plateau
                    WHERE id >= %s
                    ORDER BY id
                """
                cursor.execute(query_all_plateaux, (plateau_id,))
                plateaux_ordered = [x[0] for x in cursor.fetchall()]

                # Parcourir les plateaux jusqu’à trouver assez d’emplacements
                list_emplacement = []
                for pid in plateaux_ordered:
                    query_emplacement = """
                        SELECT code_emplacement FROM emplacement
                        WHERE plateau_id = %s AND est_occupe = 0
                        ORDER BY id
                    """
                    cursor.execute(query_emplacement, (pid,))
                    emplacements = [x[0] for x in cursor.fetchall()]
                    list_emplacement.extend(emplacements)
                    if len(list_emplacement) >= len(list_cell):
                        break

                if len(list_emplacement) < len(list_cell):
                    messagebox.showerror("Erreur", "Pas assez d'emplacement disponibles pour toutes les cellules.")
                    return

                # Créer le DataFrame d'affectation
                df = pd.DataFrame({
                    "num_serie": list_cell,
                    "emplacement": list_emplacement[:len(list_cell)]
                })

                # Mise à jour BDD
                for idx in range(len(df)):
                    query_update = """
                        UPDATE emplacement
                        SET est_occupe = TRUE, numero_serie = %s, date_attribution = NOW()
                        WHERE code_emplacement = %s
                    """
                    cursor.execute(query_update, (df.loc[idx, "num_serie"], df.loc[idx, "emplacement"]))
                    conn.commit()

                messagebox.showinfo(
                    "Succès", 
                    f"Cellules attribuées jusqu'au numéro série {df.loc[len(df)-1,'num_serie']}"
                )
                
                # Ajout dans TreeView
                for index, row in df.iterrows():
                    self.tree.insert("", "end", values=list(row))

            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de l'opération : {err}")
            finally:
                cursor.close()
                conn.close()

    # -------------------------------
    # Onglet Picking plateaux
    # -------------------------------
    def refresh_battery_grid_from_picking(self):
        
        if not hasattr(self, 'picking_data') or self.current_index >= len(self.picking_data):
            return

        # Récupérer l'identifiant de la batterie courante
        produit_courant = self.picking_data[self.current_index].get("num_produit_bdd", "")

        index_local = 0  # index pour la grille zigzag locale
        for idx, row in enumerate(self.picking_data):
            produit = row.get("num_produit_bdd", "")
            if produit != produit_courant:
                continue

            i, j = self.get_battery_grid_coords(index_local)
            canvas, rect = self.battery_canvases.get((i, j), (None, None))
            if canvas:
                etat = row.get("etat_picking", 0)
                if etat == 1:
                    color = "lime green"
                    self.battery_cell_states[(i, j)] = "picked"
                else:
                    color = "white"
                    self.battery_cell_states[(i, j)] = "none"
                canvas.itemconfig(rect, fill=color)

            index_local += 1



    def setup_picking(self, main_frame):

        # Configuration pour 2 colonnes égales (50/50)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=2)
        main_frame.grid_columnconfigure(1, weight=1)

        # Frame gauche : Infos picking
        left_frame = tk.Frame(main_frame, bg="lightgray")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Frame droite : Listes & treeviews
        right_frame = tk.Frame(main_frame, bg="white")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # ----- SOUS-FRAMES POUR LEFT -----
        # Top (cellule courante, emplacement)
        top_frame = tk.Frame(left_frame, bg="lightgray")
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.grid_columnconfigure(0, weight=1)

        # Bottom (infos module, scan, boutons, etc.)
        bottom_frame = tk.Frame(left_frame, bg="lightgray")
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        left_frame.grid_rowconfigure(0, weight=1)   # 20%
        left_frame.grid_rowconfigure(1, weight=4)   # 80%

        # ----- TOP INFOS -----
        self.large_font = ("Arial", 25, "bold")
        self.label_info_cellule = tk.Label(top_frame, text="Cellule :", font=self.large_font, bg="lightgray")
        self.label_info_cellule.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.label_info_emplacement = tk.Label(top_frame, text="Emplacement :", font=self.large_font, bg="lightgray")
        self.label_info_emplacement.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # ----- BOTTOM INFOS -----
        self.label_info_module = tk.Label(bottom_frame, text="Module :", font=("Arial", 12), bg="lightgray")
        self.label_info_module.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.label_info_nb_cell = tk.Label(bottom_frame, text="Cellule :", font=("Arial", 12), bg="lightgray")
        self.label_info_nb_cell.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.label_status = tk.Label(bottom_frame, text="Status LED", font=("Arial", 12, "bold"), bg="lightgray")
        self.label_status.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        tk.Label(bottom_frame, text="Scanner la cellule :", font=("Arial", 12), bg="lightgray").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_scan = tk.Entry(bottom_frame, font=("Arial", 12))
        self.entry_scan.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entry_scan.bind("<KeyRelease>", self.check_entry_length)

        self.btn_skip = tk.Button(bottom_frame, text="Passer la cellule", command=self.skip_cellule,
                                  bg="#6688E7", fg="black", font=("Arial", 12))
        self.btn_skip.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.button_retour = tk.Button(bottom_frame, text="Retour à la derniere cellule passée", command=self.return_last_cell,
                                       bg="#CD5FE9", fg="black", font=("Arial", 12))
        self.button_retour.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.option_retour = ttk.Combobox(bottom_frame, values=["Batterie", "Cellule", "Picking"], state="readonly")
        self.option_retour.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(bottom_frame, text="Choisir un mode de retour :", font=("Arial", 12), bg="lightgray").grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.label_info_1 = tk.Label(bottom_frame, text="Modèle batterie:", font=("Arial", 12), bg="lightgray")
        self.label_info_1.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.label_info_2 = tk.Label(bottom_frame, text="Architecture:", font=("Arial", 12), bg="lightgray")
        self.label_info_2.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        battery_wrapper = tk.Frame(bottom_frame, bg="lightgray")
        battery_wrapper.grid(row=8, column=0, sticky="nsew")

        self.battery_grid_frame = tk.Frame(battery_wrapper, bg="lightgray")
        self.battery_grid_frame.pack(side="left", anchor="n", padx=5, pady=5)


        # ----- RIGHT FRAME -----
        # Label titre
        self.label_tree1 = tk.Label(right_frame, text="Picking général", font=("Arial", 12), bg="white")
        self.label_tree1.grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")

        # Treeview 1 + Scrollbar
        self.tree_picking_import = ttk.Treeview(
            right_frame,
            columns=("numero_serie", "module", "produit", "etat_picking"),
            show='headings', height=10
        )
        for col in ("numero_serie", "module", "produit", "etat_picking"):
            self.tree_picking_import.heading(col, text=col.replace("_", " ").capitalize())
            self.tree_picking_import.column(col, width=80, anchor="center")
        self.tree_picking_import.grid(row=1, column=0, padx=5, pady=2, sticky="nsew")
        self.tree_picking_import.tag_configure("found", background="lightgreen")
        self.tree_picking_import.tag_configure("not_found", background="lightcoral")

        # Scrollbar pour Treeview 1
        scrollbar1 = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree_picking_import.yview)
        self.tree_picking_import.configure(yscrollcommand=scrollbar1.set)
        scrollbar1.grid(row=1, column=1, sticky="ns")

        # Boutons Import & Launch
        btn_import = tk.Button(right_frame, text="Importer fichier de picking", command=self.import_picking,
                               bg="#6688E7", fg="black")
        btn_import.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        btn_launch = tk.Button(right_frame, text="Lancer le picking", command=self.start_picking,
                               bg="#CD5FE9", fg="black")
        btn_launch.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        # Label pour Treeview 2
        self.label_tree2 = tk.Label(right_frame, text="Picking batterie : ", font=("Arial", 12), bg="white")
        self.label_tree2.grid(row=4, column=0, padx=5, pady=(10,0), sticky="w")

        # Treeview 2 + Scrollbar
        self.tree_picking_module = ttk.Treeview(
            right_frame,
            columns=("numero_serie", "module", "produit", "etat picking", "emplacement"),
            show='headings', height=10
        )
        for col in ("numero_serie", "module", "produit", "etat picking", "emplacement"):
            self.tree_picking_module.heading(col, text=col.replace("_", " ").capitalize())
            self.tree_picking_module.column(col, width=80, anchor="center")
        self.tree_picking_module.grid(row=5, column=0, padx=5, pady=2, sticky="nsew")
        self.tree_picking_module.tag_configure("found", background="lightgreen")
        self.tree_picking_module.tag_configure("not_found", background="lightcoral")
        scrollbar2 = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree_picking_module.yview)
        self.tree_picking_module.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.grid(row=5, column=1, sticky="ns")

        # Configurer le redimensionnement pour que les 2 treeviews occupent bien l'espace
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(5, weight=1)

        # Dictionnaires de mapping (remplis plus tard dans ton vrai code)
        self.t1_item_map = {}
        self.t2_item_map = {}

    def get_battery_grid_coords(self, index):
        nb_batt=index // 70
        rows = 5
        col = (index-nb_batt*70) // rows
        row_in_col = index % rows

        # Colonne paire → de bas en haut
        if col % 2 == 0:
            row = rows - 1 - row_in_col
        else:  # Colonne impaire → de haut en bas
            row = row_in_col

        return col, row

    def create_battery_grid(self):
        rows = 5
        columns = 14
        cell_size = 40
        border_colors = ["#E25B5B", "#519AE4"]
        state_colors = {
            "none": "white",
            "picked": "lime green",
            "missing": "red"
        }
        polar = ["+", "-"]
        cell_states = [["none" for _ in range(rows)] for _ in range(columns)]

        canvases = []
        indice_polar = 0
        indice_cell = 0
        self.battery_cell_states = {}    # (col, row): état ("none", "picked", "missing")
        self.battery_canvases = {}   # (col, row): canvas

        for i in range(columns):
            row_canvas = []
            if i % 2 == 0:
                for j in range(rows-1, -1, -1):
                    color = state_colors[cell_states[i][j]]
                    border_color = border_colors[indice_polar]
                    canvas = tk.Canvas(self.battery_grid_frame, width=cell_size, height=cell_size, highlightthickness=0)
                    canvas.grid(row=j+1, column=i, padx=1, pady=1)
                    rect=canvas.create_rectangle(2, 2, cell_size-2, cell_size-2, fill=color, outline=border_color, width=2)
                    canvas.create_text(cell_size//2, cell_size//2, text=polar[indice_polar], font=("Arial", 12))
                    row_canvas.append(canvas)

                    self.battery_cell_states[(i, j)] = "none"
                    self.battery_canvases[(i, j)] = (canvas, rect)

                    indice_cell += 1
                    indice_polar = (indice_cell // 7) % 2
            else:
                for j in range(rows):
                    color = state_colors[cell_states[i][j]]
                    border_color = border_colors[indice_polar]
                    canvas = tk.Canvas(self.battery_grid_frame, width=cell_size, height=cell_size, highlightthickness=0)
                    canvas.grid(row=j+1, column=i, padx=1, pady=1)
                    rect=canvas.create_rectangle(2, 2, cell_size-2, cell_size-2, fill=color, outline=border_color, width=2)
                    canvas.create_text(cell_size//2, cell_size//2, text=polar[indice_polar], font=("Arial", 12))
                    row_canvas.append(canvas)

                    self.battery_cell_states[(i, j)] = "none"
                    self.battery_canvases[(i, j)] = (canvas, rect)

                    indice_cell += 1
                    indice_polar = (indice_cell // 7) % 2

            canvases.append(row_canvas)

        # Titres modules
        modules = {
            0: "module 1", 1: "module 2", 2: "module 3", 3: "module 4", 4: "module 5",
            5: "module 6", 6: "module 7", 7: "module 8", 8: "module 9", 9: "module 10"
        }

        tk.Label(self.battery_grid_frame, text=modules[0], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=0, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[1], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=1, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[2], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=2, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[3], font=("Arial", 12), bg=border_colors[1]).grid(row=0, column=4, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[4], font=("Arial", 12), bg=border_colors[0]).grid(row=6, column=5, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[5], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=7, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[6], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=8, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[7], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=9, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[8], font=("Arial", 12), bg=border_colors[0]).grid(row=6, column=11, columnspan=2)
        tk.Label(self.battery_grid_frame, text=modules[9], font=("Arial", 12), bg=border_colors[1]).grid(row=0, column=12, columnspan=2)

        tk.Label(self.battery_grid_frame, text="",bg="lightgrey").grid(row=8, column=3, columnspan=2)
        tk.Label(self.battery_grid_frame, text="",bg="lightgrey").grid(row=8, column=6, columnspan=2)
        tk.Label(self.battery_grid_frame, text="",bg="lightgrey").grid(row=8, column=9, columnspan=2)

        tk.Label(self.battery_grid_frame, text="⬜ cellule non pickée").grid(row=9, column=3, columnspan=3)
        tk.Label(self.battery_grid_frame, text="🟩 cellule pickée", bg="lime green").grid(row=9, column=6, columnspan=3)
        tk.Label(self.battery_grid_frame, text="🟥 cellule non trouvée", bg="red").grid(row=9, column=9, columnspan=3)


    def compter_etat_par_batterie(self,batterie_cible):
        tree=self.tree_picking_module
        total = 0
        etat_1 = 0

        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            num_serie, module, produit, etat,empla = values

            if produit == batterie_cible:
                total += 1
                if etat == '1':  # ou `if int(etat) == 1` selon le type
                    etat_1 += 1

        return total, etat_1

    def compter_etat_par_module(self,module_cible):
        tree=self.tree_picking_module
        total = 0
        etat_1 = 0

        for item_id in tree.get_children():
            values = tree.item(item_id, 'values')
            num_serie, module, produit, etat,empla = values

            if int(module) == module_cible:
                total += 1
                if etat == '1':  # ou `if int(etat) == 1` selon le type
                    etat_1 += 1

        return total, etat_1
    
    def return_last_cell(self):
        mode= self.option_retour.get()
        if mode:
            try:
                if mode == "Picking":
                    self.start_picking()
                elif mode == "Cellule":
                    if self.current_index > 0:
                        self.current_index -= 1
                        current_row = self.picking_data[self.current_index]
                        etat_picking = current_row.get("etat_picking", 0)
                        while etat_picking !=0 :
                            self.current_index -= 1
                            current_row = self.picking_data[self.current_index]
                            etat_picking = current_row.get("etat_picking", 0)  
                        self.missed_cells.pop()
                        self.refresh_battery_grid_from_picking()
                        self.load_current_cell()
                    else:
                        messagebox.showwarning("Avertissement", "Vous êtes déjà à la première cellule.")
                elif mode =='Batterie':
                    if self.current_index > 0:
                        start_row = self.picking_data[self.current_index]
                        produit_ref = start_row.get("num_produit_bdd", "")
                        etat_picking = start_row.get("etat_picking", 0)
                        current_row = start_row
                        produit=produit_ref
                        while produit == produit_ref :
                            self.current_index -= 1
                            current_row = self.picking_data[self.current_index]
                            produit = current_row.get("num_produit_bdd", "")
                            etat_picking = current_row.get("etat_picking", 0)
                            if etat_picking == 0:
                                self.missed_cells.pop()
                           
                        self.current_index+=1
                        self.refresh_battery_grid_from_picking()
                        self.load_current_cell()

                    else:
                        messagebox.showwarning("Avertissement", "Vous êtes déjà à la première cellule.")
                        
                   
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du retour à une passée : {e}")
        else :
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un mode de retour.")
            return  

    def import_picking(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier de picking", 
            filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        
        self.picking_file_path = file_path
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            self.picking_data = df.to_dict(orient='records')

            for item in self.tree_picking_import.get_children():
                self.tree_picking_import.delete(item)

            # Insertion dans tree_picking_import
            for row in self.picking_data:
                numero_serie = row.get("Numero_serie_cellule", "")
                module = row.get("module", "")
                produit = row.get("num_produit_bdd", "")
                etat_picking = row.get("etat_picking", 0) 

                item_id = self.tree_picking_import.insert(
                    "", "end", 
                    values=(numero_serie, module, produit, etat_picking)
                )
                self.t1_item_map[numero_serie] = item_id
                
                if etat_picking == 1:
                    self.tree_picking_import.item(item_id, tags=("found",))

            # on récupère le module/produit de la première ligne
            row_one = self.picking_data[0]
            module_one = row_one.get("module", "")
            produit_one = row_one.get("num_produit_bdd", "")
            list_one = [
                r.get("Numero_serie_cellule", "")
                for r in self.picking_data
                if r.get("module", "") == module_one and r.get("num_produit_bdd", "") == produit_one
            ]
            self.nb_cells_module = len(list_one)   

            query_info_produit = """
                SELECT reference_batterie_voltr, architecture
                FROM ref_batterie_voltr
                as rb 
                JOIN produit_voltr as pv 
                ON rb.reference_batterie_voltr = pv.reference_produit_voltr
                WHERE pv.numero_serie_produit= %s
            """
            conn = self.db_manager.connect()
            if conn:
                try:
                    cursor = conn.cursor()

                    cursor.execute(query_info_produit, (produit_one,))
                    result = cursor.fetchall()
                    if result:
                        architecture = result[0][1]
                        reference_batterie = result[0][0]
                        self.label_info_1.config(text=f"Modèle batterie: {reference_batterie}")
                        self.label_info_2.config(text=f"Architecture: {architecture}")
                        if reference_batterie == "EMBR036AA":
                            self.create_battery_grid()
                finally:
                    cursor.close()
                    conn.close()
            messagebox.showinfo("Import", "Fichier importé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'importation du fichier : {e}")

    def start_picking(self):
        if not hasattr(self, 'picking_data'):
            messagebox.showwarning("Aucun fichier", "Veuillez d'abord importer un fichier de picking.")
            return
        
        self.current_index = 0
        self.missed_cells = []

        # On affiche (pack) la picking_frame dans le left_frame
        #self.picking_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.refresh_battery_grid_from_picking()
        self.load_current_cell()

    def load_current_cell(self):
        while self.current_index < len(self.picking_data):
            current_row = self.picking_data[self.current_index]
            numero_serie = current_row.get("Numero_serie_cellule", "")
            module = current_row.get("module", "")
            produit = current_row.get("num_produit_bdd", "")
            etat_picking = current_row.get("etat_picking", 0)

            if etat_picking == 1:
                self.current_index += 1
                continue  # on passe à la prochaine ligne
            else:
                break   # on sort du while pour traiter la ligne trouvée

        else:
            self.finish_picking()
            return
        
        self.tree_picking_import.see(self.tree_picking_import.get_children()[self.current_index])

        emplacement = self.get_emplacement_from_db(numero_serie)
        if emplacement:
            #Rendre l'emplacement plus lisible 
            parties = emplacement.split('-')
            if len(parties) > 1:
                emplacement = f"{parties[0]} - {parties[1]}"

        self.label_info_cellule.config(text=f"Cellule : {numero_serie}")
        self.label_info_emplacement.config(text=f"Emplacement : {emplacement if emplacement else '-introuvable-'}")
        self.label_info_module.config(text=f"Module : {module}")


        self.entry_scan.delete(0, tk.END)
        self.set_status("Attente scan", "black")

        self.refresh_module_tree(module, produit)

        div,num=self.compter_etat_par_module(module)
        self.label_info_nb_cell.config(text=f"Cellules pickée dans le module : {num}/{div}")

        tot_cell_batterie, tot_cell_picked = self.compter_etat_par_batterie(produit)
        self.label_tree2.config(text=f"Picking batterie : {produit} ({tot_cell_picked}/{tot_cell_batterie})")

        item_id = self.t2_item_map[numero_serie] if numero_serie in self.t2_item_map else None
        if item_id:
            self.tree_picking_module.see(item_id)
            #self.tree_picking_module.selection_set(item_id)
        else:
            messagebox.showwarning("Avertissement", f"Numéro de série {numero_serie} non trouvé dans le module.")

    def refresh_module_tree(self, module, produit):
        ancien_emplacements = {}
        for item_id in self.tree_picking_module.get_children():
            num = self.tree_picking_module.set(item_id, "numero_serie")
            emp = self.tree_picking_module.set(item_id, "emplacement")
            ancien_emplacements[num] = emp


        for item in self.tree_picking_module.get_children():
            self.tree_picking_module.delete(item)
        self.t2_item_map.clear()

        for row in self.picking_data:
            m = row.get("module", "")
            p = row.get("num_produit_bdd", "")
            etat = row.get("etat_picking", 0)
            if p == produit : #and etat == 0: #m == module and
                num = row.get("Numero_serie_cellule", "")

                old_emplacement = ancien_emplacements.get(num, "")

                item_id = self.tree_picking_module.insert(
                    "", "end", 
                    values=(num, m, p, etat,old_emplacement)
                )
                self.t2_item_map[num] = item_id
                if etat == 1:
                    self.tree_picking_module.item(item_id, tags=("found",))

    def get_emplacement_from_db(self, numero_serie):
        conn = self.db_manager.connect()
        emplacement = None
        if conn:
            try:
                cursor = conn.cursor()
                sql = """SELECT code_emplacement 
                         FROM emplacement
                         WHERE numero_serie = %s"""
                cursor.execute(sql, (numero_serie,))
                result = cursor.fetchone()
                if result:
                    emplacement = result[0]
                    while cursor.nextset():
                        pass
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la requête emplacement : {err}")
            finally:
                try:
                    _ = cursor.fetchall()
                except:
                    pass
                cursor.close()
                conn.close()
        return emplacement
    
    def end_battery(self):
        battery_act=self.picking_data[self.current_index].get("num_produit_bdd", "")
        battery_last=self.picking_data[self.current_index-1].get("num_produit_bdd", "")
        if battery_act != battery_last:
            messagebox.showinfo("Fin de picking batterie", f"Fin de picking pour la batterie {battery_last}.")
            self.create_battery_grid()
            self.refresh_battery_grid_from_picking()

    def check_entry_length(self, event):
        print("Key released:", event.keysym)
        if event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R","Shift","Enter"]:
            return

        content = self.entry_scan.get().strip()
        if len(content) == 12:
            self.validate_cell_scan(content)

    def validate_cell_scan(self, scanned_number):
        current_row = self.picking_data[self.current_index]
        expected_num_serie = current_row.get("Numero_serie_cellule", "")

        if scanned_number == expected_num_serie:
            
            self.set_status("OK!", "green")

            # Colorer la ligne dans le 2e TreeView
            if scanned_number in self.t2_item_map:
                item_id = self.t2_item_map[scanned_number]
                self.tree_picking_module.item(item_id, tags=("found",))

            # Mettre à jour etat_picking = 1
            self.picking_data[self.current_index]["etat_picking"] = 1

            #Mettre a jour l'emplacement de la cellule

            conn = self.db_manager.connect()
            if conn:
                try:
                    cursor = conn.cursor()
                    query_emp = """
                        SELECT code_emplacement
                        FROM emplacement   
                        WHERE numero_serie = %s
                    """
                    cursor.execute(query_emp, (scanned_number,))
                    emplacement_scan = cursor.fetchone()
                    if emplacement_scan:
                        emplacement_scan = emplacement_scan[0]

                except mysql.connector.Error as err:
                    messagebox.showerror("Erreur DB", f"Erreur lors de la mise à jour : {err}")
                finally:
                    cursor.close()
                    conn.close()

            self.release_emplacement_in_db(scanned_number)
            self.tree_picking_module.set(item_id, column="emplacement", value=f"{emplacement_scan}")

            # Colorer la ligne dans le 1er TreeView
            if scanned_number in self.t1_item_map:
                item_t1 = self.t1_item_map[scanned_number]
                old_values = self.tree_picking_import.item(item_t1, "values")
                new_values = (old_values[0], old_values[1], old_values[2], 1)
                self.tree_picking_import.item(item_t1, values=new_values, tags=("found",))

            i, j = self.get_battery_grid_coords(self.current_index)
            #self.battery_cell_states[(i, j)] = "picked"
            canvas, rect = self.battery_canvases[(i, j)]
            canvas.itemconfig(rect, fill="lime green")

            self.current_index += 1
            self.end_battery()
            self.after(1000, self.load_current_cell)
        else:
            self.set_status("KO!", "red")
            self.entry_scan.delete(0, tk.END)
            query_wrong_cell = """
                SELECT code_emplacement
                FROM emplacement
                WHERE numero_serie = %s
            """
            conn = self.db_manager.connect()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query_wrong_cell, (scanned_number,))
                    result = cursor.fetchone()
                    if result:
                        emplacement = result[0]
                        messagebox.showerror("Erreur", f"Numéro de série incorrect. Emplacement : {emplacement}")
                    else:
                        messagebox.showerror("Erreur", "Numéro de série incorrect et non trouvé dans la base de données.")
                except mysql.connector.Error as err:
                    messagebox.showerror("Erreur DB", f"Erreur lors de la requête : {err}")
                finally:
                    cursor.close()
                    conn.close()

    def release_emplacement_in_db(self, numero):
        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    UPDATE emplacement
                    SET est_occupe = FALSE, numero_serie = NULL, date_attribution = NOW()
                    WHERE numero_serie = %s
                """
                cursor.execute(query, (numero,))
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la libération : {err}")
            finally:
                cursor.close()
                conn.close()

    def skip_cellule(self):
        current_row = self.picking_data[self.current_index]
        numero_serie = current_row.get("Numero_serie_cellule", "")
        self.missed_cells.append(current_row)

        if numero_serie in self.t2_item_map:
            item_id = self.t2_item_map[numero_serie]
            self.tree_picking_module.item(item_id, tags=("not_found",))
            
        i, j = self.get_battery_grid_coords(self.current_index)
        self.battery_cell_states[(i, j)] = "missing"
        canvas, rect = self.battery_canvases[(i, j)]
        canvas.itemconfig(rect, fill="red")

        self.current_index += 1
        self.end_battery()
        self.load_current_cell()

    def finish_picking(self):
        if self.missed_cells:
            txt = "Cellules non trouvées / passées :\n"
            for row in self.missed_cells:
                txt += (f"- {row.get('Numero_serie_cellule','')} "
                        f"(module={row.get('module','')}, "
                        f"produit={row.get('num_produit_bdd','')})\n")
            messagebox.showinfo("Picking terminé", txt)
        else:
            messagebox.showinfo("Picking terminé", "Toutes les cellules ont été pickées avec succès !")
        
        self.picking_frame.pack_forget()

    def set_status(self, text, color):
        self.label_status.config(text=text, fg=color)

    # -------------------------------
    # Onglet Visualisation
    # -------------------------------
    def setup_visualisation(self, frame):
        tk.Label(frame, text="Visualisation des emplacements").pack(pady=5)
        self.visu_text = tk.Text(frame, height=25)
        self.visu_text.pack(padx=10, pady=10, fill="both", expand=True)
        btn_refresh = tk.Button(frame, text="Rafraîchir", command=self.refresh_visualisation, bg="#B19CD9", fg="white")
        btn_refresh.pack(pady=5)

    def refresh_visualisation(self):
        conn = self.db_manager.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT p.nom_plateau, e.code_emplacement, e.est_occupe, e.numero_serie 
                    FROM emplacement e 
                    JOIN plateau p ON e.plateau_id = p.id
                    ORDER BY p.nom_plateau, e.code_emplacement
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                self.visu_text.delete("1.0", tk.END)
                for row in rows:
                    statut = "Occupé" if row[2] else "Libre"
                    num = row[3] if row[3] is not None else "-"
                    self.visu_text.insert(
                        tk.END, 
                        f"Plateau: {row[0]}, Emplacement: {row[1]}, Statut: {statut}, Cellule: {num}\n"
                    )
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur DB", f"Erreur lors de la récupération des données : {err}")
            finally:
                cursor.close()
                conn.close()

    def close_app(self):
        if hasattr(self, 'picking_data') and self.picking_file_path:
            try:
                df = pd.DataFrame(self.picking_data)
                df.to_excel(self.picking_file_path, index=False)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de mettre à jour le fichier Excel : {e}")
        
        self.destroy()


if __name__ == "__main__":
        app = StockApp()
        app.mainloop()