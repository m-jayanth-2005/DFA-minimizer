# File: main_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
from collections import defaultdict
from PIL import Image, ImageTk
import os
import io
import graphviz
import json

from dfa_logic import DFA, DFAMinimizer # Import logic from the other file

class DFA_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DFA Minimizer Pro")
        self.root.geometry("1100x800")

        self.style = ttk.Style()
        self.style.configure("TLabel", padding=5)
        self.style.configure("TButton", padding=5)
        self.style.configure("TEntry", padding=5)

        self._create_menu()
        self._create_widgets()
        self.load_example_dfa()

    def _create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load DFA from JSON...", command=self._load_dfa)
        file_menu.add_command(label="Save Minimized DFA as JSON...", command=self._save_dfa)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_widgets(self):
        # Main container with a paned window for resizable sections
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(main_pane, text="DFA Definition", padding=10)
        main_pane.add(input_frame, weight=1)

        ttk.Label(input_frame, text="States (comma-separated):").grid(row=0, column=0, sticky='w')
        self.states_entry = ttk.Entry(input_frame, width=50)
        self.states_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Alphabet (comma-separated):").grid(row=1, column=0, sticky='w')
        self.alphabet_entry = ttk.Entry(input_frame, width=50)
        self.alphabet_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Start State:").grid(row=2, column=0, sticky='w')
        self.start_state_entry = ttk.Entry(input_frame, width=50)
        self.start_state_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Final States (comma-separated):").grid(row=3, column=0, sticky='w')
        self.final_states_entry = ttk.Entry(input_frame, width=50)
        self.final_states_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Transitions (one per line, e.g., A:0=B,1=C):").grid(row=4, column=0, sticky='nw')
        self.transitions_text = tk.Text(input_frame, height=10, width=40, relief=tk.SOLID, borderwidth=1)
        self.transitions_text.grid(row=4, column=1, padx=5, pady=5, sticky='nsew')
        
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_rowconfigure(4, weight=1)
        
        # --- Control Buttons ---
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Minimize DFA", command=self.run_minimization).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Clear & Reset", command=self.clear_fields).pack(side=tk.LEFT, padx=10)
        
        # --- Output Frame ---
        output_container = ttk.Frame(main_pane)
        main_pane.add(output_container, weight=2)
        
        output_pane = ttk.PanedWindow(output_container, orient=tk.VERTICAL)
        output_pane.pack(fill=tk.BOTH, expand=True)
        
        # --- Graph Frame ---
        graph_frame = ttk.LabelFrame(output_pane, text="State Diagrams", padding=10)
        output_pane.add(graph_frame, weight=2)
        
        graph_frame.grid_columnconfigure((0,1), weight=1)
        graph_frame.grid_rowconfigure(1, weight=1)
        
        ttk.Label(graph_frame, text="Original DFA").grid(row=0, column=0)
        self.original_canvas = tk.Canvas(graph_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        self.original_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(graph_frame, text="Minimized DFA").grid(row=0, column=1)
        self.minimized_canvas = tk.Canvas(graph_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        self.minimized_canvas.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # --- Text Output Frame ---
        text_output_frame = ttk.LabelFrame(output_pane, text="Formal Definition", padding=10)
        output_pane.add(text_output_frame, weight=1)

        self.output_text = tk.Text(text_output_frame, height=12, width=80, relief=tk.SOLID, borderwidth=1)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_example_dfa(self):
        """Loads a sample DFA into the input fields."""
        self.clear_fields()
        self.states_entry.insert(0, "A, B, C, D, E, F, G, H")
        self.alphabet_entry.insert(0, "0, 1")
        self.start_state_entry.insert(0, "A")
        self.final_states_entry.insert(0, "C")
        self.transitions_text.insert(tk.END,
            "A:0=B,1=F\n"
            "B:0=G,1=C\n"
            "C:0=A,1=C\n"
            "D:0=C,1=G\n"
            "E:0=H,1=F\n"
            "F:0=C,1=G\n"
            "G:0=G,1=E\n"
            "H:0=G,1=C"
        )
        self.status_var.set("Example DFA loaded. Press 'Minimize DFA' to start.")

    def run_minimization(self):
        """Parses input, minimizes DFA, and displays results."""
        try:
            states = {s.strip() for s in self.states_entry.get().split(',') if s.strip()}
            alphabet = {s.strip() for s in self.alphabet_entry.get().split(',') if s.strip()}
            start_state = self.start_state_entry.get().strip()
            final_states = {s.strip() for s in self.final_states_entry.get().split(',') if s.strip()}
            
            transitions = defaultdict(dict)
            lines = self.transitions_text.get("1.0", tk.END).strip().split('\n')
            for line in lines:
                if not line.strip() or ':' not in line: continue
                state, trans_str = line.split(':', 1)
                state = state.strip()
                pairs = trans_str.split(',')
                for pair in pairs:
                    if '=' not in pair: continue
                    symbol, next_state = pair.split('=')
                    transitions[state][symbol.strip()] = next_state.strip()

            self.original_dfa = DFA(states, alphabet, transitions, start_state, final_states)
            
            is_valid, msg = self.original_dfa.is_valid()
            if not is_valid:
                messagebox.showerror("Invalid DFA", msg)
                self.status_var.set(f"Error: {msg}")
                return
            
            minimizer = DFAMinimizer(self.original_dfa)
            self.minimized_dfa = minimizer.minimize()
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "--- Original DFA ---\n")
            self.output_text.insert(tk.END, str(self.original_dfa) + "\n\n")
            self.output_text.insert(tk.END, "--- Minimized DFA ---\n")
            self.output_text.insert(tk.END, str(self.minimized_dfa))

            self.display_graph(self.original_dfa.remove_unreachable_states(), self.original_canvas)
            self.display_graph(self.minimized_dfa, self.minimized_canvas)
            self.status_var.set("DFA minimized successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.status_var.set(f"Error: {e}")

    def display_graph(self, dfa, canvas):
        """Generates and displays a state transition diagram, resizing it to fit the canvas."""
        canvas.delete("all")
        # Force canvas to update its size information
        canvas.update_idletasks()

        try:
            dot = graphviz.Digraph(graph_attr={'rankdir': 'LR'})
            dot.node('start', shape='none', label='')
            
            # Ensure a consistent node order for deterministic layouts
            sorted_states = sorted(list(dfa.states))

            for state in sorted_states:
                shape = 'doublecircle' if state in dfa.final_states else 'circle'
                dot.node(state, shape=shape)

            dot.edge('start', dfa.start_state)
            
            # Add edges based on a sorted transition order for consistency
            for state in sorted(dfa.transitions.keys()):
                trans = dfa.transitions[state]
                for symbol in sorted(trans.keys()):
                    next_state = trans[symbol]
                    dot.edge(state, next_state, label=symbol)
            
            png_data = dot.pipe(format='png')
            
            # Open image with Pillow
            image = Image.open(io.BytesIO(png_data))

            # --- RESIZING LOGIC ---
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # Add a small padding
            padding = 20 
            canvas_width -= padding
            canvas_height -= padding

            img_width, img_height = image.size

            # Calculate aspect ratios
            img_ratio = img_width / img_height
            canvas_ratio = canvas_width / canvas_height

            # Determine new size to fit inside canvas while maintaining aspect ratio
            if canvas_ratio > img_ratio:
                # Canvas is wider than the image, so height is the limiting factor
                new_height = canvas_height
                new_width = int(new_height * img_ratio)
            else:
                # Canvas is taller than the image, so width is the limiting factor
                new_width = canvas_width
                new_height = int(new_width / img_ratio)

            # Resize the image using a high-quality filter
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            canvas.image = ImageTk.PhotoImage(resized_image) # Keep a reference
            canvas.create_image(canvas.winfo_width() / 2, canvas.winfo_height() / 2, image=canvas.image)

        except (graphviz.backend.execute.ExecutableNotFound, FileNotFoundError):
            canvas.create_text(
                canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                text="Graphviz not found.\nPlease install it and add it to your system's PATH.",
                fill="red", font=("Arial", 10), justify='center'
            )
        except Exception as e:
            canvas.create_text(
                canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                text=f"Failed to render graph:\n{e}",
                fill="red", font=("Arial", 10), justify='center'
            )

    def clear_fields(self):
        """Clears all input fields and output canvases."""
        self.states_entry.delete(0, tk.END)
        self.alphabet_entry.delete(0, tk.END)
        self.start_state_entry.delete(0, tk.END)
        self.final_states_entry.delete(0, tk.END)
        self.transitions_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.original_canvas.delete("all")
        self.minimized_canvas.delete("all")
        self.minimized_dfa = None
        self.original_dfa = None
        self.status_var.set("Fields cleared. Ready.")
    
    def _load_dfa(self):
        filepath = filedialog.askopenfilename(
            title="Load DFA from JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            dfa = DFA.from_dict(data)
            
            # Populate UI from loaded DFA
            self.clear_fields()
            self.states_entry.insert(0, ", ".join(dfa.states))
            self.alphabet_entry.insert(0, ", ".join(dfa.alphabet))
            self.start_state_entry.insert(0, dfa.start_state)
            self.final_states_entry.insert(0, ", ".join(dfa.final_states))
            
            trans_text = []
            for state, trans in dfa.transitions.items():
                pairs = [f"{sym}={next_s}" for sym, next_s in trans.items()]
                trans_text.append(f"{state}:{','.join(pairs)}")
            self.transitions_text.insert("1.0", "\n".join(trans_text))
            self.status_var.set(f"Successfully loaded DFA from {os.path.basename(filepath)}.")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load or parse file: {e}")
            self.status_var.set("Error loading file.")

    def _save_dfa(self):
        if not hasattr(self, 'minimized_dfa') or self.minimized_dfa is None:
            messagebox.showwarning("Save Error", "No minimized DFA to save. Please run the minimization first.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Minimized DFA as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'w') as f:
                json.dump(self.minimized_dfa.to_dict(), f, indent=4)
            self.status_var.set(f"Minimized DFA saved to {os.path.basename(filepath)}.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")
            self.status_var.set("Error saving file.")
            
    def _show_about(self):
        messagebox.showinfo(
            "About DFA Minimizer Pro",
            "DFA Minimizer Pro\n\n"
            "An application to visualize the minimization of Deterministic Finite Automata "
            "using the Table-Filling algorithm.\n\n"
            "Features:\n"
            "- Unreachable state removal\n"
            "- Table-Filling minimization\n"
            "- Graphviz visualization\n"
            "- JSON import/export"
        )


if __name__ == '__main__':
    # Use ThemedTk for a modern look
    root = ThemedTk(theme="arc")
    app = DFA_GUI(root)
    root.mainloop()