import tkinter as tk
from tkinter import messagebox
import numpy as np

def convert_to_right_incidence_matrix(edges, num_vertices):
    matrix = np.zeros((num_vertices, len(edges)), dtype=int)
    for col, (_, end) in enumerate(edges):
        matrix[end][col] = 1
    return matrix

def build_graph_from_edges(edges, num_vertices):
    graph = [[] for _ in range(num_vertices)]
    for start, end in edges:
        graph[start].append(end)
    return graph

def topological_sort(graph):
    num_vertices = len(graph)
    in_degree = [0] * num_vertices
    for i in range(num_vertices):
        for j in graph[i]:
            in_degree[j] += 1

    queue = [i for i in range(num_vertices) if in_degree[i] == 0]
    order = []
    while queue:
        current = queue.pop(0)
        order.append(current)
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != num_vertices:
        raise ValueError("Граф содержит цикл!")
    return order

def calculate():
    try:
        edges_input = edges_entry.get()
        num_vertices = int(vertices_entry.get())

        # Преобразуем номера вершин в 0-based индексы
        edges = []
        for edge in edges_input.split(';'):
            if edge.strip():
                start, end = map(int, edge.strip().split(','))
                if start > num_vertices or end > num_vertices or start < 1 or end < 1:
                    raise ValueError(f"Номер вершины должен быть от 1 до {num_vertices}")
                edges.append((start-1, end-1))  # преобразуем в 0-based

        matrix = convert_to_right_incidence_matrix(edges, num_vertices)
        graph = build_graph_from_edges(edges, num_vertices)
        order = topological_sort(graph)

        result = "🔹 Матрица правых инцидентностей (G+):\n"
        for row in matrix:
            result += ' '.join(map(str, row)) + '\n'

        result += "\n🔸 Новая нумерация вершин (по топологическому порядку):\n"
        for i in range(num_vertices):
            result += f"Старая вершина {i+1} → Новая вершина {order.index(i)}\n"

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, result)
        result_text.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# ---------- Графический интерфейс ---------- #
root = tk.Tk()
root.title("Преобразование графа в G+ (правые инцидентности)")
root.geometry("750x600")
root.configure(bg="#f2f2f2")

title_label = tk.Label(root, text="Преобразование графа в множество правых инцидентностей (G+)", 
                       font=("Arial", 16, "bold"), bg="#f2f2f2")
title_label.pack(pady=10)

desc_label = tk.Label(root, text="Введите количество вершин и список дуг в формате '1,2;1,7;2,3;...' (вершины нумеруются с 1).",
                      font=("Arial", 10), bg="#f2f2f2")
desc_label.pack(pady=(0, 15))

# Ввод данных в рамке
input_frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE, padx=10, pady=10)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Количество вершин:", font=("Arial", 11), bg="#ffffff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
vertices_entry = tk.Entry(input_frame, width=10, font=("Arial", 11))
vertices_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Список дуг:", font=("Arial", 11), bg="#ffffff").grid(row=1, column=0, sticky='e', padx=5, pady=5)
edges_entry = tk.Entry(input_frame, width=40, font=("Arial", 11))
edges_entry.grid(row=1, column=1, padx=5, pady=5)

calculate_button = tk.Button(input_frame, text="Рассчитать", command=calculate, font=("Arial", 11), bg="#4CAF50", fg="white")
calculate_button.grid(row=2, column=0, columnspan=2, pady=10)

# Результаты
tk.Label(root, text="Результаты:", font=("Arial", 12, "bold"), bg="#f2f2f2").pack(pady=(20, 5))

result_text = tk.Text(root, height=20, width=90, font=("Courier New", 10), wrap=tk.WORD, bg="#f9f9f9")
result_text.pack(pady=(0, 20))
result_text.config(state=tk.DISABLED)

root.mainloop()