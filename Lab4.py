import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def bfs_shortest_paths(A, start):
    n = A.shape[0]
    distances = np.full(n, -1)
    distances[start] = 0
    queue = [start]

    while queue:
        current = queue.pop(0)
        for neighbor in range(n):
            if A[current, neighbor] == 1 and distances[neighbor] == -1:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances

def all_pairs_shortest_paths(A):
    n = A.shape[0]
    U = np.zeros((n, n), dtype=int)
    for i in range(n):
        U[i] = bfs_shortest_paths(A, i)
    return U

def adjacency_to_incidence(A):
    n = A.shape[0]
    edges = np.sum(A)
    B = np.zeros((n, edges), dtype=int)
    e = 0
    for i in range(n):
        for j in range(n):
            if A[i, j] == 1:
                B[i, e] = -1
                B[j, e] = 1
                e += 1
    return B

class GraphMatrixCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор матриц графа (смежности)")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Параметры матрицы смежности")
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="Количество вершин:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.vertices_var = tk.StringVar(value="4")
        ttk.Entry(input_frame, textvariable=self.vertices_var, width=10).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Создать матрицу", command=self.create_matrix).grid(row=0, column=2, padx=5, pady=5)

        self.matrix_frame = ttk.LabelFrame(self.root, text="Матрица смежности", height=300)
        self.matrix_frame.pack(fill="x", padx=10, pady=10)
        self.matrix_frame.pack_propagate(False)

        self.matrix_canvas = tk.Canvas(self.matrix_frame)
        self.matrix_canvas.pack(side="left", fill="both", expand=True)

        self.matrix_vscrollbar = ttk.Scrollbar(self.matrix_frame, orient="vertical", command=self.matrix_canvas.yview)
        self.matrix_vscrollbar.pack(side="right", fill="y")
        self.matrix_canvas.configure(yscrollcommand=self.matrix_vscrollbar.set)

        self.matrix_hscrollbar = ttk.Scrollbar(self.matrix_frame, orient="horizontal", command=self.matrix_canvas.xview)
        self.matrix_hscrollbar.pack(side="bottom", fill="x")
        self.matrix_canvas.configure(xscrollcommand=self.matrix_hscrollbar.set)

        self.matrix_content_frame = ttk.Frame(self.matrix_canvas)
        self.matrix_canvas_window = self.matrix_canvas.create_window((0, 0), window=self.matrix_content_frame, anchor="nw")

        self.matrix_content_frame.bind("<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")))

        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить пример", command=self.load_example).pack(side="left", padx=5)

        self.results_frame = ttk.LabelFrame(self.root, text="Результаты")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.incidence_tab = ttk.Frame(self.notebook)
        self.paths_tab = ttk.Frame(self.notebook)
        self.graph_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.incidence_tab, text="Матрица инцидентности")
        self.notebook.add(self.paths_tab, text="Матрица кратчайших путей")
        self.notebook.add(self.graph_tab, text="Визуализация графа")

        self.setup_scrollable_frame(self.incidence_tab)
        self.setup_scrollable_frame(self.paths_tab)

        self.matrix_entries = []

    def setup_scrollable_frame(self, parent_frame):
        canvas = tk.Canvas(parent_frame)
        canvas.pack(side="left", fill="both", expand=True)

        vscrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        vscrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=vscrollbar.set)

        hscrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=canvas.xview)
        hscrollbar.pack(side="bottom", fill="x")
        canvas.configure(xscrollcommand=hscrollbar.set)

        content_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        parent_frame.canvas = canvas
        parent_frame.content_frame = content_frame

    def create_matrix(self):
        for widget in self.matrix_content_frame.winfo_children():
            widget.destroy()

        try:
            vertices = int(self.vertices_var.get())
            if vertices <= 0:
                messagebox.showerror("Ошибка", "Количество вершин должно быть положительным числом")
                return

            self.matrix_entries = []
            for i in range(vertices):
                row_entries = []
                for j in range(vertices):
                    var = tk.StringVar(value="0")
                    entry = ttk.Entry(self.matrix_content_frame, textvariable=var, width=5)
                    entry.grid(row=i, column=j, padx=2, pady=2)
                    row_entries.append(var)
                self.matrix_entries.append(row_entries)

            self.matrix_content_frame.update_idletasks()
            self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число вершин")

    def get_adjacency_matrix(self):
        try:
            vertices = int(self.vertices_var.get())
            A = np.zeros((vertices, vertices), dtype=int)

            for i in range(vertices):
                for j in range(vertices):
                    A[i, j] = int(self.matrix_entries[i][j].get())

            return A
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Проверьте значения матрицы")
            return None

    def calculate(self):
        A = self.get_adjacency_matrix()
        if A is None:
            return

        try:
            U = all_pairs_shortest_paths(A)
            B = adjacency_to_incidence(A)

            # Очищаем старое содержимое
            for tab in [self.incidence_tab, self.paths_tab]:
                for widget in tab.content_frame.winfo_children():
                    widget.destroy()
                tab.canvas.configure(scrollregion=tab.canvas.bbox("all"))

            for widget in self.graph_tab.winfo_children():
                widget.destroy()

            # Вывод матрицы инцидентности с заголовками
            ttk.Label(self.incidence_tab.content_frame, text="Матрица инцидентности:").grid(row=0, column=0, columnspan=B.shape[1]+1, pady=5)

            for j in range(B.shape[1]):
                ttk.Label(self.incidence_tab.content_frame, text=f"e{j}", width=5).grid(row=1, column=j+1)

            for i in range(B.shape[0]):
                ttk.Label(self.incidence_tab.content_frame, text=f"v{i}", width=5).grid(row=i+2, column=0)
                for j in range(B.shape[1]):
                    ttk.Label(self.incidence_tab.content_frame, text=f"{B[i, j]}", width=5, borderwidth=1, relief="solid").grid(row=i+2, column=j+1)

            # Вывод матрицы кратчайших путей с заголовками
            vertices = A.shape[0]

            ttk.Label(self.paths_tab.content_frame, text="Матрица кратчайших путей:").grid(row=0, column=0, columnspan=vertices+1, pady=5)

            for j in range(vertices):
                ttk.Label(self.paths_tab.content_frame, text=f"{j}", width=5).grid(row=1, column=j+1)

            for i in range(vertices):
                ttk.Label(self.paths_tab.content_frame, text=f"{i}", width=5).grid(row=i+2, column=0)
                for j in range(vertices):
                    value = U[i, j]
                    display_value = str(value) if value != -1 else "∞"
                    ttk.Label(self.paths_tab.content_frame, text=display_value, width=5, borderwidth=1, relief="solid").grid(row=i+2, column=j+1)

            self.visualize_graph(A)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def visualize_graph(self, A):
        fig, ax = plt.subplots(figsize=(6, 5))
        n = A.shape[0]
        pos = {}
        for i in range(n):
            angle = 2 * np.pi * i / n
            pos[i] = (np.cos(angle), np.sin(angle))

        for i in range(n):
            ax.plot(pos[i][0], pos[i][1], 'o', markersize=15, color='skyblue')
            ax.text(pos[i][0], pos[i][1], str(i), horizontalalignment='center', verticalalignment='center')

        for i in range(n):
            for j in range(n):
                if A[i, j] == 1:
                    dx = pos[j][0] - pos[i][0]
                    dy = pos[j][1] - pos[i][1]
                    length = np.sqrt(dx**2 + dy**2)
                    node_radius = 0.15
                    start_x = pos[i][0] + node_radius * dx / length
                    start_y = pos[i][1] + node_radius * dy / length
                    end_x = pos[j][0] - node_radius * dx / length
                    end_y = pos[j][1] - node_radius * dy / length

                    ax.arrow(start_x, start_y, end_x - start_x, end_y - start_y, 
                             head_width=0.05, head_length=0.1, fc='black', ec='black')

        ax.set_title("Визуализация графа")
        ax.axis('equal')
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear(self):
        self.vertices_var.set("4")
        self.create_matrix()

    def load_example(self):
        self.vertices_var.set("4")
        self.create_matrix()
        example = [
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0]
        ]
        for i in range(4):
            for j in range(4):
                self.matrix_entries[i][j].set(str(example[i][j]))

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphMatrixCalculator(root)
    root.mainloop()
