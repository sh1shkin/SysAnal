import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

FONT = ("Arial", 12)
TITLE_FONT = ("Arial", 14, "bold")

class GraphAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ графов по инциденциям")
        self.root.geometry("900x700")

        self.size = 0
        self.entries = {}

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Введите количество вершин:", font=FONT).pack(side=tk.LEFT, padx=5)
        self.size_entry = tk.Entry(top_frame, width=10, font=FONT)
        self.size_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Подтвердить", font=FONT, bg="#2196F3", fg="white", command=self.create_input_fields).pack(side=tk.LEFT, padx=5)

        self.entries_frame = tk.Frame(self.root)
        self.entries_frame.pack(pady=10, fill='both', expand=True)

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)

        tk.Button(action_frame, text="Обработать", font=FONT, width=20, bg="#4CAF50", fg="white", command=self.process_input).pack(side=tk.LEFT, padx=10)
        self.save_button = tk.Button(action_frame, text="Сохранить", font=FONT, width=20, bg="#2196F3", fg="white", command=self.save_incidents, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=10)
        tk.Button(action_frame, text="Выход", font=FONT, width=20, bg="#f44336", fg="white", command=self.root.destroy).pack(side=tk.LEFT, padx=10)

        self.result_tabs = tk.Frame(self.root)
        self.result_tabs.pack(pady=10, fill='both', expand=True)

        self.text_area = scrolledtext.ScrolledText(self.result_tabs, width=100, height=25, font=FONT)
        self.text_area.pack(padx=10, pady=10, expand=True, fill='both')

    def create_input_fields(self):
        try:
            self.size = int(self.size_entry.get())
            if self.size <= 0:
                raise ValueError("Количество вершин должно быть положительным числом")

            for widget in self.entries_frame.winfo_children():
                widget.destroy()
            self.entries = {}

            for i in range(1, self.size+1):
                frame = tk.Frame(self.entries_frame)
                frame.pack(pady=3, anchor='w', padx=20)
                tk.Label(frame, text=f"G({i})-:", font=FONT, width=10, anchor='w').pack(side=tk.LEFT)
                entry = tk.Entry(frame, width=30, font=FONT)
                entry.pack(side=tk.LEFT)
                self.entries[i] = entry
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def process_input(self):
        try:
            left_incidents = {}
            G = nx.DiGraph()

            for node in self.entries:
                incidents_str = self.entries[node].get().strip()
                incidents = [int(x.strip()) for x in incidents_str.split(',') if x.strip()] if incidents_str else []
                left_incidents[node] = incidents
                for neighbor in incidents:
                    G.add_edge(neighbor, node)

            for node in range(1, self.size+1):
                if node not in G.nodes():
                    G.add_node(node)

            subsystems = self.find_strongly_connected_subsystems(G)
            new_G, _ = self.build_subsystem_graph(G, subsystems)

            self.display_results(G, new_G, subsystems, left_incidents)

            self.left_incidents = left_incidents
            self.save_button.config(state=tk.NORMAL)

            self.draw_graphs(G, new_G)
        except Exception as e:
            messagebox.showerror("Ошибка обработки", f"Произошла ошибка: {str(e)}")

    def display_results(self, G, new_G, subsystems, left_incidents):
        subsystems_text = "\n".join([f"Подсистема {idx+1}: {sorted(subgraph)}" for idx, subgraph in enumerate(subsystems)])
        left_incidents_text = "\n".join([f"G({k})- : {{ {', '.join(map(str, values))} }}" for k, values in left_incidents.items()])
        adj_matrix_text = self.adjacency_matrix_text(G)

        full_text = f"Разбиение на подсистемы:\n{subsystems_text}\n\n"
        full_text += f"Множество левых инциденций:\n{left_incidents_text}\n\n"
        full_text += f"Матрица смежности:\n{adj_matrix_text}"

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, full_text)
        self.text_area.config(state=tk.DISABLED)

    def draw_graphs(self, G, new_G):
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        pos1 = nx.spring_layout(G, seed=42)
        nx.draw(G, pos1, with_labels=True, node_color='lightblue', edge_color='gray',
                node_size=2000, font_size=12, arrows=True, ax=axes[0])
        axes[0].set_title("Исходный граф")

        pos2 = nx.spring_layout(new_G, seed=42)
        nx.draw(new_G, pos2, with_labels=True, node_color='lightcoral', edge_color='gray',
                node_size=2000, font_size=12, arrows=True, ax=axes[1])
        axes[1].set_title("Граф подсистем")

        plt.tight_layout()
        plt.show()

    def save_incidents(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Множества левых инциденций (G^-):\n")
                    for node, incidents in self.left_incidents.items():
                        f.write(f"G({node})- : {{ {', '.join(map(str, incidents))} }}\n")
                messagebox.showinfo("Сохранение", f"Данные сохранены в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {str(e)}")

    @staticmethod
    def find_strongly_connected_subsystems(G):
        subsystems = []
        remaining_nodes = set(G.nodes())
        excluded_nodes = set()
        while remaining_nodes:
            node = min(remaining_nodes)
            R = set(nx.descendants(G, node)) | {node}
            Q = (set(nx.ancestors(G, node)) | {node}) - excluded_nodes
            SCC = R & Q
            subsystems.append(SCC)
            remaining_nodes -= SCC
            excluded_nodes |= SCC
        return subsystems

    @staticmethod
    def build_subsystem_graph(G, subsystems):
        new_G = nx.DiGraph()
        subsystem_map = {frozenset(subsystem): idx + 1 for idx, subsystem in enumerate(subsystems)}
        for subsystem, label in subsystem_map.items():
            new_G.add_node(label)
        for subsystem_1 in subsystems:
            for subsystem_2 in subsystems:
                if subsystem_1 != subsystem_2:
                    for node in subsystem_1:
                        for neighbor in G.successors(node):
                            if neighbor in subsystem_2:
                                new_G.add_edge(subsystem_map[frozenset(subsystem_1)], subsystem_map[frozenset(subsystem_2)])
        return new_G, subsystem_map

    @staticmethod
    def adjacency_matrix_text(G):
        nodes = sorted(G.nodes())
        matrix = [[0]*len(nodes) for _ in range(len(nodes))]
        node_idx = {node: idx for idx, node in enumerate(nodes)}
        for u, v in G.edges():
            matrix[node_idx[u]][node_idx[v]] = 1
        header = "\t" + "\t".join(map(str, nodes))
        rows = [header]
        for idx, row in enumerate(matrix):
            rows.append(f"{nodes[idx]}\t" + "\t".join(map(str, row)))
        return "\n".join(rows)

def main():
    root = tk.Tk()
    app = GraphAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
