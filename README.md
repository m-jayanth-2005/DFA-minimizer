# DFA Minimizer Pro 🤖

A graphical desktop application for visualizing the minimization of Deterministic Finite Automata (DFAs) using the Table-Filling algorithm.

This tool provides a clear "before and after" comparison, making it an excellent resource for students, educators, and anyone working with formal language theory.

![Screenshot of the DFA Minimizer application](https://i.imgur.com/L1L1f5i.png)

---

## ## Features

* **Interactive GUI**: An intuitive and modern user interface built with Tkinter.
* **DFA Visualization**: Automatically generates and displays state transition diagrams for both the original and minimized DFAs.
* **Core Minimization Logic**: Implements the classic **Table-Filling Algorithm** to find and merge indistinguishable states.
* **Unreachable State Removal**: Automatically prunes any states that are not reachable from the start state before minimization.
* **File Operations**: Save your DFA definitions to a JSON file and load them back in later.
* **Responsive Layout**: The application window and its internal panels are resizable.

---

## ## Tech Stack & Libraries

This project relies on the following core technologies:

* **Python 3**: The primary programming language.
* **Tkinter** & **TtkThemes**: For creating the graphical user interface. `Tkinter` is Python's standard GUI library, and `TtkThemes` is used for modern styling.
* **Graphviz**: The powerful open-source software used for rendering the state transition diagrams. The Python library acts as a wrapper for the system tool.
* **Pillow**: The Python Imaging Library (PIL) fork, used to process the raw image data from Graphviz, resize it, and display it in the Tkinter window.

---

## ## Setup and Installation

To get the application running on your local machine, please follow these steps.

### ### Prerequisites

1.  **Python 3**: You must have Python 3.6 or newer installed.
2.  **Graphviz System Tool**: This is the most important prerequisite. The Python library needs the actual Graphviz software to be installed on your system.
    * **Windows**: Download and run the installer from the [official Graphviz website](https://graphviz.org/download/). **Crucially, make sure to check the box "Add Graphviz to the system PATH" during installation.**
    * **macOS (using Homebrew)**: `brew install graphviz`
    * **Linux (Debian/Ubuntu)**: `sudo apt-get install graphviz`

### ### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Install Python dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install the required packages
    pip install pillow graphviz ttkthemes
    ```

3.  **Run the application:**
    ```bash
    python main_app.py
    ```

---

## ## How to Use

1.  **Define the DFA**: Fill in the input fields on the left panel:
    * **States**: A comma-separated list of all state names (e.g., `q0, q1, q2`).
    * **Alphabet**: A comma-separated list of input symbols (e.g., `0, 1`).
    * **Start State**: The name of the single start state.
    * **Final States**: A comma-separated list of accepting states.
    * **Transitions**: Define the transition function, with one state's transitions per line (e.g., `q0:0=q1,1=q2`).
2.  **Minimize**: Click the **"Minimize DFA"** button.
3.  **View Results**: The right-hand panel will update to show:
    * The state diagram of your original DFA (with unreachable states removed).
    * The state diagram of the new, minimized DFA.
    * The formal 5-tuple definitions for both automata in the text box below.
4.  **Load/Save**: Use the **File** menu to save your minimized DFA to a `.json` file or to load a previously saved DFA definition.

---

## ## Code Structure

The project is organized into two main files to separate the core logic from the user interface:

* `dfa_logic.py`: The "brain" of the application. It contains the `DFA` and `DFAMinimizer` classes and handles all the theoretical computations without any knowledge of the GUI.
* `main_app.py`: The "face" of the application. It contains the `DFA_GUI` class and is responsible for creating the window, handling user input, and visualizing the results returned by `dfa_logic.py`.

---

## ## Contributing

Contributions are welcome! If you'd like to improve the application or add a new feature, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourAmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some YourAmazingFeature'`).
4.  Push to the branch (`git push origin feature/YourAmazingFeature`).
5.  Open a new Pull Request.

---

## ## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
