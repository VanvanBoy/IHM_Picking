import tkinter as tk

# Configurations
rows = 5
modules = [
    "module 1", "module 2", "module 3", "module 4", "module 5",
    "module 6", "module 7", "module 8", "module 9", "module 10"
]
polarities = ["+", "-"]  # chaque module a 2 polarités

# Couleurs
state_colors = {
    "none": "white",
    "picked": "lime green",
    "missing": "red"
}
border_colors = ["red", "blue"]  # alternance rouge/bleu par module

# États initiaux
cell_states = [["none" for _ in range(len(modules) * 2)] for _ in range(rows)]
canvases = []

# Taille des cases
cell_size = 40

# Fenêtre principale
root = tk.Tk()
root.title("Avancement du picking de la batterie")

# Titre
tk.Label(root, text="Avancement du picking de la batterie", font=("Arial", 18)).pack(pady=10)

# Cadre principal
main_frame = tk.Frame(root)
main_frame.pack()

# Affichage des noms de modules
for mod_idx, mod in enumerate(modules):
    color = border_colors[mod_idx % 2]
    tk.Label(main_frame, text=mod, fg=color, font=("Arial", 9, "bold")).grid(row=0, column=mod_idx * 2, columnspan=2)

# Création des cellules en Canvas
for i in range(rows):
    row_canvas = []
    for j in range(len(modules) * 2):
        mod_idx = j // 2
        border_color = border_colors[mod_idx % 2]
        polarity = "+" if j % 2 == 0 else "-"
        state = cell_states[i][j]
        fill_color = state_colors[state]

        canvas = tk.Canvas(main_frame, width=cell_size, height=cell_size, highlightthickness=0)
        canvas.grid(row=rows - i + 1, column=j, padx=1, pady=1)

        rect = canvas.create_rectangle(2, 2, cell_size - 2, cell_size - 2, fill=fill_color, outline=border_color, width=2)
        text = canvas.create_text(cell_size // 2, cell_size // 2, text=polarity, font=("Arial", 12))

        row_canvas.append((canvas, rect))
    canvases.append(row_canvas)

# Légende
legend = tk.Frame(root)
legend.pack(pady=10)

tk.Label(legend, text="⬜ cellule non pickée", bg="white").grid(row=0, column=0, padx=10)
tk.Label(legend, text="🟩 cellule pickée", bg="lime green").grid(row=0, column=1, padx=10)
tk.Label(legend, text="🟥 cellule non trouvée", bg="red").grid(row=0, column=2, padx=10)

# Fonction pour mettre à jour une cellule dynamiquement
def update_cell(i, j, new_state):
    cell_states[i][j] = new_state
    mod_idx = j // 2
    border_color = border_colors[mod_idx % 2]
    canvas, rect_id = canvases[i][j]
    canvas.itemconfig(rect_id, fill=state_colors[new_state], outline=border_color)

# Exemples de mise à jour
update_cell(0, 0, "picked")
update_cell(1, 1, "missing")
update_cell(4, 19, "picked")

root.mainloop()
