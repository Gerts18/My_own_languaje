import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

JAVA_MAIN_CLASS = "milenguaje.Main"
JAVA_PROJECT_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(JAVA_PROJECT_DIR, "src", "test", "resources")
TEMP_FILE = os.path.join(RESOURCES_DIR, "temp.pepsi")

class LineNumbers(tk.Text):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=4, padx=4, takefocus=0, **kwargs)
        self.text_widget = text_widget
        self.config(state='disabled', bg='#f0f0f0', fg='#888')
        text_widget.bind('<KeyRelease>', self.redraw)
        text_widget.bind('<MouseWheel>', self.redraw)
        text_widget.bind('<Return>', self.redraw)
        self.redraw()

    def redraw(self, event=None):
        self.config(state='normal')
        self.delete('1.0', tk.END)
        n = int(self.text_widget.index('end-1c').split('.')[0])
        for i in range(1, n+1):
            self.insert(tk.END, f"{i}\n")
        self.config(state='disabled')

class PepsiIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pepsi IDE")
        self.geometry("900x800")

        # Editor + líneas
        fr = tk.Frame(self); fr.pack(fill="both", expand=True, padx=5, pady=5)
        self.editor = tk.Text(fr, wrap="none", font=("Consolas", 12))
        self.lns = LineNumbers(fr, self.editor)
        self.lns.pack(side="left", fill="y")
        self.editor.pack(side="right", fill="both", expand=True)
        sy = tk.Scrollbar(fr, command=self._on_scroll); sy.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=sy.set)

        # Botones
        btns = [
          ("Importar archivo", self.importar),
          ("Guardar código",  self.guardar),
          ("Ejecutar",         self.ejecutar),
          ("Exportar a Python", lambda:self.exportar("py")),
          ("Exportar a JavaScript", lambda:self.exportar("js")),
        ]
        bf = tk.Frame(self); bf.pack(fill="x", padx=5, pady=2)
        for t,c in btns:
            tk.Button(bf, text=t, command=c).pack(side="left", padx=2)

        # Salida
        sf = tk.Frame(self); sf.pack(fill="both", expand=True, padx=5, pady=2)
        tk.Label(sf, text="Salida:").pack(anchor="w")
        self.salida = tk.Text(sf, height=20, wrap="none",
                              font=("Consolas",11), bg="#222", fg="#0f0")
        self.salida.pack(side="left", fill="both", expand=True)
        so = tk.Scrollbar(sf, command=self.salida.yview); so.pack(side="right", fill="y")
        self.salida.config(yscrollcommand=so.set)

    def _on_scroll(self, *args):
        self.editor.yview(*args)
        self.lns.yview(*args)

    def importar(self):
        fp = filedialog.askopenfilename(filetypes=[("Pepsi files","*.pepsi"),("All","*.*")])
        if not fp: return
        with open(fp,"r",encoding="utf-8") as f:
            txt = f.read()
        self.editor.delete("1.0",tk.END)
        self.editor.insert("1.0",txt)
        self.lns.redraw()

    def guardar(self):
        code = self.editor.get("1.0",tk.END)
        fp = filedialog.asksaveasfilename(defaultextension=".pepsi",
                                          filetypes=[("Pepsi files","*.pepsi"),("All","*.*")])
        if not fp: return
        with open(fp,"w",encoding="utf-8") as f:
            f.write(code)

    def ejecutar(self):
        # 1) volcar a temp.pepsi
        code = self.editor.get("1.0",tk.END)
        os.makedirs(os.path.dirname(TEMP_FILE),exist_ok=True)
        with open(TEMP_FILE,"w",encoding="utf-8") as f:
            f.write(code)
        self.salida.delete("1.0",tk.END)

        # 2) invocar Java via Maven
        cmd = [
            "mvn.cmd", "-Dexec.executable=java",
            f"-Dexec.args=-classpath %classpath {JAVA_MAIN_CLASS} temp.pepsi",
            "-Dexec.classpathScope=runtime","-DskipTests=true",
            "--no-transfer-progress","process-classes",
            "org.codehaus.mojo:exec-maven-plugin:3.1.0:exec"
        ]
        try:
            p = subprocess.run(cmd, cwd=JAVA_PROJECT_DIR,
                               capture_output=True, text=True, timeout=30)
        except Exception as e:
            messagebox.showerror("Error de ejecución", str(e))
            return

        # 3) filtrar SOLO errores de sintaxis de tu lenguaje
        if p.returncode != 0:
            errores = []
            combinado = (p.stderr + "\n" + p.stdout).splitlines()
            for l in combinado:
                l = l.strip()
                if l.startswith("Error en la línea"):
                    errores.append(l)
                elif "token recognition error" in l:
                    # ANTLR lexer error
                    errores.append("Error léxico NO FUE POSIBLE LA EJECUCION ")
            if not errores:
                # fallback muy simple
                errores = ["Error lexico, NO FUE POSIBLE LA EJECUCION"]
            messagebox.showerror("Error de sintaxis", "\n".join(errores))
            return

        # 4) si todo ok, mostrar salida limpia
        clean = []
        for l in (p.stdout + p.stderr).splitlines():
            if l.startswith(("WARNING","[INFO]","[ERROR]","BUILD")):
                continue
            clean.append(l)
        self.salida.insert("1.0", "\n".join(clean))

    def exportar(self, lang):
        # primero validar
        self.ejecutar()
        ext = ".py" if lang=="py" else ".js"
        f = os.path.join(RESOURCES_DIR, "temp"+ext)
        if os.path.exists(f):
            with open(f,"r",encoding="utf-8") as r:
                txt = r.read()
            self.salida.delete("1.0",tk.END)
            self.salida.insert("1.0",txt)
            fp = filedialog.asksaveasfilename(defaultextension=ext,
                filetypes=[(f"{lang.upper()} files",f"*{ext}")])
            if fp:
                with open(fp,"w",encoding="utf-8") as w:
                    w.write(txt)
        else:
            messagebox.showwarning("Exportar","No se generó el archivo traducido.")

if __name__ == "__main__":
    app = PepsiIDE()
    app.mainloop()
