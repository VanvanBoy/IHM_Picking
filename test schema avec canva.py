import tkinter as tk

# Dimensions de la grille
rows = 5
columns = 14  # 2 colonnes par module (5 modules * 2 colonnes)

# Modules répartis
modules = {
    0: "module 1", 1: "module 2",
    2: "module 3", 3: "module 4",
    4: "module 5", 5: "module 6",
    6: "module 7", 7: "module 8",
    8: "module 9", 9: "module 10"
}

# État des cellules ("none", "picked", "missing")
cell_states = [["none" for _ in range(rows)] for _ in range(columns)]

border_colors = ["#E25B5B", "#519AE4"]  # alternance rouge/bleu par module

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


cell_size = 40  # Taille des cellules
# Conteneur de cellules pour mise à jour dynamique
canvases = []
polar=["+","-"]
indice_polar=0
indice_cell=0
for i in range(columns):
    row_canvas = []
    if i % 2 == 0:
        for j in range(rows-1,-1,-1):
            color = state_colors[cell_states[i][j]]
            border_color = border_colors[indice_polar]
            canvas = tk.Canvas(frame,width=cell_size, height=cell_size,highlightthickness=0)
            canvas.grid(row=j+1, column=i, padx=1, pady=1) 
            rect = canvas.create_rectangle(2, 2, cell_size - 2, cell_size - 2, fill=color, outline=border_color, width=2)
            text = canvas.create_text(cell_size // 2, cell_size // 2, text=polar[indice_polar], font=("Arial", 12))

            row_canvas.append(canvas)
            indice_cell=indice_cell+1
            indice_polar = (indice_cell // 7) % 2 
                
    else :
        for j in range(rows):
            color = state_colors[cell_states[i][j]]
            border_color = border_colors[indice_polar]
            canvas = tk.Canvas(frame,width=cell_size, height=cell_size,highlightthickness=0)
            canvas.grid(row=j+1, column=i, padx=1, pady=1) 
            rect = canvas.create_rectangle(2, 2, cell_size - 2, cell_size - 2, fill=color, outline=border_color, width=2)
            text = canvas.create_text(cell_size // 2, cell_size // 2, text=polar[indice_polar], font=("Arial", 12))

            row_canvas.append(canvas)
            indice_cell=indice_cell+1
            indice_polar = (indice_cell // 7) % 2 
            
    canvases.append(row_canvas)


tk.Label(frame, text=modules[0], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=0, columnspan=2)
tk.Label(frame, text=modules[1], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=1, columnspan=2)
tk.Label(frame, text=modules[2], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=2, columnspan=2)
tk.Label(frame, text=modules[3], font=("Arial", 12), bg=border_colors[1]).grid(row=0, column=4, columnspan=2)
tk.Label(frame, text=modules[4], font=("Arial", 12), bg=border_colors[0]).grid(row=6, column=5, columnspan=2)
tk.Label(frame, text=modules[5], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=7, columnspan=2)
tk.Label(frame, text=modules[6], font=("Arial", 12), bg=border_colors[0]).grid(row=0, column=8, columnspan=2)
tk.Label(frame, text=modules[7], font=("Arial", 12), bg=border_colors[1]).grid(row=6, column=9, columnspan=2)
tk.Label(frame, text=modules[8], font=("Arial", 12), bg=border_colors[0]).grid(row=6, column=11, columnspan=2)
tk.Label(frame, text=modules[9], font=("Arial", 12), bg=border_colors[1]).grid(row=0, column=12, columnspan=2)
# Légende
legend = tk.Frame(root)
legend.pack(pady=10)

tk.Label(legend, text="⬜ cellule non pickée").grid(row=0, column=0, padx=5)
tk.Label(legend, text="🟩 cellule pickée", bg="lime green").grid(row=0, column=1, padx=5)
tk.Label(legend, text="🟥 cellule non trouvée", bg="red").grid(row=0, column=2, padx=5)

# Lancement
root.mainloop()

