import tkinter as tk

# Dimensions de la grille
rows = 5
columns = 14  # 2 colonnes par module (5 modules * 2 colonnes)

# Modules répartis
modules = {
    0: "module 1", 1: "module 1",
    2: "module 2", 3: "module 2",
    4: "module 3", 5: "module 3",
    6: "module 4", 7: "module 4",
    8: "module 5", 9: "module 5"
}

# État des cellules ("none", "picked", "missing")
cell_states = [["none" for _ in range(rows)] for _ in range(columns)]

# Création de la fenêtre
root = tk.Tk()
root.title("Avancement du picking de la batterie")

# Titre
tk.Label(root, text="Avancement du picking de la batterie", font=("Arial", 16)).pack(pady=10)

# Cadre principal
frame = tk.Frame(root)
frame.pack()

# Couleurs associées
state_colors = {
    "none": "white",
    "picked": "lime green",
    "missing": "red"
}

border_colors = ["red", "blue"]  # alternance rouge/bleu par module

# Conteneur de cellules pour mise à jour dynamique
labels = []
polar=["+","-"]
indice_polar=0
indice_cell=0
for i in range(columns):
    row_labels = []
    if i % 2 == 0:
        for j in range(rows-1,-1,-1):
            color = state_colors[cell_states[i][j]]
            label = tk.Label(frame, text=polar[indice_polar] , width=4, height=2,
                             relief="solid", borderwidth=1, bg=color)
            label.grid(row=j, column=i, padx=1, pady=1)  # ligne inversée pour le même rendu
            row_labels.append(label)
            indice_cell=indice_cell+1
            indice_polar = (indice_cell // 7) % 2 
                
    else :
        for j in range(rows):
            color = state_colors[cell_states[i][j]]
            label = tk.Label(frame, text=polar[indice_polar] , width=4, height=2,
                             relief="solid", borderwidth=1, bg=color)
            label.grid(row=j, column=i, padx=1, pady=1)  # ligne inversée pour le même rendu
            row_labels.append(label)
            indice_cell=indice_cell+1
            indice_polar = (indice_cell // 7) % 2 
    labels.append(row_labels)

# Légende
legend = tk.Frame(root)
legend.pack(pady=10)

tk.Label(legend, text="⬜ cellule non pickée").grid(row=0, column=0, padx=5)
tk.Label(legend, text="🟩 cellule pickée", bg="lime green").grid(row=0, column=1, padx=5)
tk.Label(legend, text="🟥 cellule non trouvée", bg="red").grid(row=0, column=2, padx=5)

# Lancement
root.mainloop()
