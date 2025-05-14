import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shlex

JAVA_MAIN_CLASS = "milenguaje.Main"
JAVA_PROJECT_DIR = os.path.dirname(__file__)  
RESOURCES_DIR = os.path.join(JAVA_PROJECT_DIR, "src", "test", "resources")
TEMP_FILE = os.path.join(RESOURCES_DIR, "temp.pepsi")

class PepsiIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pepsi IDE")
        self.geometry("900x600")

        # Editor de código
        self.editor = tk.Text(self, wrap="none", font=("Consolas", 12))
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="Importar archivo", command=self.importar).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Ejecutar", command=self.ejecutar).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Exportar a Python", command=lambda: self.exportar("py")).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Exportar a JavaScript", command=lambda: self.exportar("js")).pack(side="left", padx=2)

        # Área de salida redimensionable con scrollbar
        salida_frame = tk.Frame(self)
        salida_frame.pack(fill="both", expand=True, padx=5, pady=2)
        tk.Label(salida_frame, text="Salida:").pack(anchor="w")
        self.salida = tk.Text(salida_frame, height=10, wrap="none", font=("Consolas", 11), bg="#222", fg="#0f0")
        self.salida.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(salida_frame, command=self.salida.yview)
        scrollbar.pack(side="right", fill="y")
        self.salida.config(yscrollcommand=scrollbar.set)

    def importar(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pepsi files", "*.pepsi"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert(tk.END, code)

    def ejecutar(self):
        code = self.editor.get("1.0", tk.END)
        os.makedirs(os.path.dirname(TEMP_FILE), exist_ok=True)
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        self.salida.delete("1.0", tk.END)
        try:
            # Ejecutar usando Maven para que resuelva el classpath
            cmd = [
                "mvn.cmd",
                "-Dexec.executable=java",
                '-Dexec.args=-classpath %classpath milenguaje.Main temp.pepsi',  # <-- Cambiado aquí
                "-Dexec.classpathScope=runtime",
                "-DskipTests=true",
                "--no-transfer-progress",
                "process-classes",
                "org.codehaus.mojo:exec-maven-plugin:3.1.0:exec"
            ]
            proc = subprocess.run(cmd, cwd=JAVA_PROJECT_DIR, capture_output=True, text=True, timeout=30)
            output = proc.stdout + "\n" + proc.stderr
        except Exception as e:
            output = f"Error al ejecutar: {e}"
        self.salida.insert(tk.END, output)

    def exportar(self, lang):
        code = self.editor.get("1.0", tk.END)
        os.makedirs(os.path.dirname(TEMP_FILE), exist_ok=True)
        with open(TEMP_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            cmd = [
                "mvn.cmd",
                "-Dexec.executable=java",
                '-Dexec.args=-classpath %classpath milenguaje.Main temp.pepsi',  # <-- Cambiado aquí
                "-Dexec.classpathScope=runtime",
                "-DskipTests=true",
                "--no-transfer-progress",
                "process-classes",
                "org.codehaus.mojo:exec-maven-plugin:3.1.0:exec"
            ]
            subprocess.run(cmd, cwd=JAVA_PROJECT_DIR, capture_output=True, text=True, timeout=30)
            ext = ".py" if lang == "py" else ".js"
            trad_file = os.path.join(RESOURCES_DIR, "temp" + ext)
            if os.path.exists(trad_file):
                with open(trad_file, "r", encoding="utf-8") as f:
                    trad_code = f.read()
                self.salida.delete("1.0", tk.END)
                self.salida.insert(tk.END, trad_code)
                save_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(f"{lang.upper()} files", f"*{ext}")])
                if save_path:
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(trad_code)
            else:
                self.salida.insert(tk.END, "No se generó el archivo traducido.")
        except Exception as e:
            self.salida.insert(tk.END, f"Error al exportar: {e}")

if __name__ == "__main__":
    app = PepsiIDE()
    app.mainloop()
