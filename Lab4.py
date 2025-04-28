import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphMatrixCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор матриц графа")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f7f7f7')

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TNotebook", tabposition='n')

        # Ввод параметров
        input_frame = ttk.LabelFrame(self.root, text="Параметры графа", padding=10)
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Количество вершин:").pack(side="left", padx=5)
        self.vertices_var = tk.StringVar(value="4")
        ttk.Entry(input_frame, textvariable=self.vertices_var, width=10).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Создать матрицу", command=self.create_matrix).pack(side="left", padx=10)

        # Матрица смежности
        self.matrix_frame = ttk.LabelFrame(self.root, text="Матрица смежности", padding=10)
        self.matrix_frame.pack(fill="both", padx=20, pady=10, expand=True)

        self.matrix_canvas = tk.Canvas(self.matrix_frame, bg='white')
        self.matrix_canvas.pack(side="left", fill="both", expand=True)

        self.vscrollbar = ttk.Scrollbar(self.matrix_frame, orient="vertical", command=self.matrix_canvas.yview)
        self.vscrollbar.pack(side="right", fill="y")
        self.matrix_canvas.configure(yscrollcommand=self.vscrollbar.set)

        self.matrix_content_frame = ttk.Frame(self.matrix_canvas)
        self.matrix_window = self.matrix_canvas.create_window((0, 0), window=self.matrix_content_frame, anchor="nw")
        self.matrix_content_frame.bind("<Configure>", lambda e: self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all")))

        # Кнопки действий
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Рассчитать", command=self.calculate).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Очистить", command=self.clear).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Загрузить пример", command=self.load_example).pack(side="left", padx=10)

        # Результаты
        results_frame = ttk.LabelFrame(self.root, text="Результаты", padding=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill="both", expand=True)

        self.incidence_tab = ttk.Frame(self.notebook)
        self.paths_tab = ttk.Frame(self.notebook)
        self.graph_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.incidence_tab, text="Матрица инцидентности")
        self.notebook.add(self.paths_tab, text="Матрица кратчайших путей")
        self.notebook.add(self.graph_tab, text="Граф")

        self.setup_scrollable_tab(self.incidence_tab)
        self.setup_scrollable_tab(self.paths_tab)

        self.matrix_entries = []

    def setup_scrollable_tab(self, tab):
        canvas = tk.Canvas(tab)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        content = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tab.canvas = canvas
        tab.content = content

    def create_matrix(self):
        for widget in self.matrix_content_frame.winfo_children():
            widget.destroy()
        try:
            vertices = int(self.vertices_var.get())
            self.matrix_entries = []
            for i in range(vertices):
                row = []
                for j in range(vertices):
                    var = tk.StringVar(value="0")
                    entry = ttk.Entry(self.matrix_content_frame, textvariable=var, width=4)
                    entry.grid(row=i, column=j, padx=2, pady=2)
                    row.append(var)
                self.matrix_entries.append(row)
            self.matrix_content_frame.update_idletasks()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое число вершин.")

    def get_adjacency_matrix(self):
        try:
            vertices = int(self.vertices_var.get())
            A = np.zeros((vertices, vertices), dtype=int)
            for i in range(vertices):
                for j in range(vertices):
                    A[i, j] = int(self.matrix_entries[i][j].get())
            return A
        except Exception:
            messagebox.showerror("Ошибка", "Неверные данные в матрице!")
            return None

    def calculate(self):
        A = self.get_adjacency_matrix()
        if A is None:
            return
        try:
            U = self.all_pairs_shortest_paths(A)
            B = self.adjacency_to_incidence(A)

            self.display_matrix(B, self.incidence_tab.content, "e")
            self.display_matrix(U, self.paths_tab.content, "v", replace_minus=True)
            self.draw_graph(A)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def display_matrix(self, M, frame, prefix, replace_minus=False):
        for widget in frame.winfo_children():
            widget.destroy()
        rows, cols = M.shape
        for j in range(cols):
            ttk.Label(frame, text=f"{prefix}{j}").grid(row=0, column=j+1)
        for i in range(rows):
            ttk.Label(frame, text=f"{prefix}{i}").grid(row=i+1, column=0)
            for j in range(cols):
                val = M[i, j]
                if replace_minus and val == -1:
                    val = "∞"
                ttk.Label(frame, text=f"{val}", borderwidth=1, relief="solid", width=5).grid(row=i+1, column=j+1)

    def draw_graph(self, A):
        for widget in self.graph_tab.winfo_children():
            widget.destroy()
        fig, ax = plt.subplots(figsize=(6, 5))
        n = A.shape[0]
        pos = {i: (np.cos(2*np.pi*i/n), np.sin(2*np.pi*i/n)) for i in range(n)}

        for i in range(n):
            ax.plot(pos[i][0], pos[i][1], 'o', markersize=10, color='skyblue')
            ax.text(pos[i][0], pos[i][1], str(i), ha='center', va='center')

        for i in range(n):
            for j in range(n):
                if A[i, j] == 1:
                    ax.arrow(pos[i][0], pos[i][1], pos[j][0]-pos[i][0], pos[j][1]-pos[i][1],
                             head_width=0.05, head_length=0.1, fc='black', ec='black', length_includes_head=True)

        ax.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=self.graph_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def adjacency_to_incidence(self, A):
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

    def all_pairs_shortest_paths(self, A):
        n = A.shape[0]
        U = np.full((n, n), -1)
        for i in range(n):
            U[i] = self.bfs_shortest_paths(A, i)
        return U

    def bfs_shortest_paths(self, A, start):
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

    def clear(self):
        self.vertices_var.set("4")
        self.create_matrix()

    def load_example(self):
        self.vertices_var.set("4")
        self.create_matrix()
        example = [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]]
        for i in range(4):
            for j in range(4):
                self.matrix_entries[i][j].set(str(example[i][j]))

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphMatrixCalculator(root)
    root.mainloop()
