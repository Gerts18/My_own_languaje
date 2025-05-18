import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os

JAVA_MAIN_CLASS = "milenguaje.Main"
JAVA_PROJECT_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(JAVA_PROJECT_DIR, "src", "test", "resources")
TEMP_FILE = os.path.join(RESOURCES_DIR, "temp.pepsi")

# Colores y estilos
THEME = {
    "bg_main": "#f5f5f5",             # Color de fondo principal
    "bg_editor": "#ffffff",           # Color de fondo del editor
    "bg_linenumbers": "#e0e0e0",      # Color de fondo de los números de línea
    "fg_linenumbers": "#606060",      # Color del texto de los números de línea
    "bg_output": "#1e1e2e",           # Color de fondo para la salida (más oscuro pero elegante)
    "fg_output": "#50fa7b",           # Color del texto de salida (verde más suave)
    "accent": "#3498db",              # Color de acento para botones y elementos destacados
    "btn_hover": "#2980b9",           # Color de hover para botones
    "editor_font": ("Consolas", 12),  # Fuente del editor
    "output_font": ("Consolas", 11),  # Fuente de la salida
    "btn_font": ("Segoe UI", 10)      # Fuente de los botones
}

class LineNumbers(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=40, highlightthickness=0, bd=0, **kwargs)
        self.text_widget = text_widget
        self.config(bg=THEME["bg_linenumbers"])
        
        # Sincronizar scroll del editor con el canvas de líneas
        self.text_widget.bind("<Configure>", self.redraw)
        self.text_widget.bind("<KeyRelease>", self.redraw)
        self.text_widget.bind("<MouseWheel>", self.redraw)

    def redraw(self, event=None):
        # Limpiar canvas
        self.delete("all")
        
        # Obtener información visible del texto
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
                
            y = dline[1]  # Posición Y de la línea
            linenum = str(i).split(".")[0]
            self.create_text(
                20, 
                y + 2, 
                anchor="n", 
                text=linenum, 
                fill=THEME["fg_linenumbers"],
                font=THEME["editor_font"]
            )
            i = self.text_widget.index(f"{i}+1line")

class SyntaxHighlightingText(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configurar las etiquetas para resaltado básico
        self.tag_configure("keyword", foreground="#007acc")
        self.tag_configure("string", foreground="#ce9178")
        self.tag_configure("comment", foreground="#6a9955", font=(THEME["editor_font"][0], THEME["editor_font"][1], "italic"))
        self.tag_configure("number", foreground="#b5cea8")
        
        # Establecer vinculaciones para actualizar el resaltado
        self.bind("<KeyRelease>", self.highlight_syntax)
        
    def highlight_syntax(self, event=None):
        # Implementación básica - en un IDE real sería más compleja
        # Solo para efectos visuales en esta versión
        pass

class PepsiIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pepsi IDE")
        self.geometry("900x800")
        self.configure(bg=THEME["bg_main"])
        
        # Intentar cargar un icono si está disponible
        try:
            self.iconbitmap("pepsi.ico")
        except:
            pass
            
        # Configurar el estilo para ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Accent.TButton', 
                        background=THEME["accent"], 
                        foreground="white", 
                        font=THEME["btn_font"])
        style.map('Accent.TButton', 
                 background=[('active', THEME["btn_hover"])])
        
        # Frame principal con borde y sombra simulada
        main_frame = tk.Frame(self, bg=THEME["bg_main"], bd=1, relief=tk.RIDGE)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
        # Título con estilo
        title_frame = tk.Frame(main_frame, bg=THEME["accent"], height=30)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="Pepsi IDE", font=("Segoe UI", 12, "bold"), 
                 fg="white", bg=THEME["accent"], padx=10).pack(side="left")

        # Editor + líneas con mejor integración
        editor_frame = tk.Frame(main_frame, bg=THEME["bg_editor"])
        editor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Panel editor con scroll
        editor_container = tk.Frame(editor_frame, bg=THEME["bg_editor"])
        editor_container.pack(side="left", fill="both", expand=True)
        
        # Crear widget de editor de texto con resaltado básico
        self.editor = SyntaxHighlightingText(
            editor_container, 
            wrap="none", 
            font=THEME["editor_font"],
            bg=THEME["bg_editor"],
            insertbackground="black",
            selectbackground="#add8e6",
            selectforeground="black",
            undo=True,
            padx=5,
            pady=5
        )
        
        # Números de línea mejorados (canvas)
        self.lns = LineNumbers(editor_container, self.editor, bg=THEME["bg_linenumbers"])
        self.lns.pack(side="left", fill="y")
        
        # Crear scrollbars con estilo
        scrollbar_y = ttk.Scrollbar(editor_container, orient="vertical", command=self.editor.yview)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(editor_frame, orient="horizontal", command=self.editor.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        
        self.editor.config(
            yscrollcommand=self._on_editor_scroll_y,
            xscrollcommand=scrollbar_x.set
        )
        self.editor.pack(side="left", fill="both", expand=True)

        # Barra de botones con estilo mejorado
        buttons_frame = tk.Frame(main_frame, bg=THEME["bg_main"], pady=10)
        buttons_frame.pack(fill="x")
        
        btns = [
            ("Importar archivo", self.importar),
            ("Guardar código", self.guardar),
            ("Ejecutar", self.ejecutar),
            ("Exportar a Python", lambda: self.exportar("py")),
            ("Exportar a JavaScript", lambda: self.exportar("js")),
        ]
        
        for i, (text, command) in enumerate(btns):
            btn = ttk.Button(
                buttons_frame, 
                text=text, 
                command=command,
                style='Accent.TButton'
            )
            btn.pack(side="left", padx=5)

        # Panel de salida con estilo mejorado
        output_frame = tk.LabelFrame(
            main_frame, 
            text="Salida", 
            font=("Segoe UI", 10, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["accent"],
            pady=5
        )
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text widget para la salida con scrollbars
        self.salida = tk.Text(
            output_frame, 
            height=12, 
            wrap="none",
            font=THEME["output_font"], 
            bg=THEME["bg_output"], 
            fg=THEME["fg_output"],
            padx=10,
            pady=10,
            bd=0
        )
        
        # Scrollbars para salida
        output_scroll_y = ttk.Scrollbar(output_frame, orient="vertical", command=self.salida.yview)
        output_scroll_y.pack(side="right", fill="y")
        
        output_scroll_x = ttk.Scrollbar(output_frame, orient="horizontal", command=self.salida.xview)
        output_scroll_x.pack(side="bottom", fill="x")
        
        self.salida.config(
            yscrollcommand=output_scroll_y.set,
            xscrollcommand=output_scroll_x.set
        )
        self.salida.pack(side="left", fill="both", expand=True)
        
        # Barra de estado
        self.status_bar = tk.Label(
            main_frame, 
            text="Listo", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#f0f0f0",
            font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Enlazar eventos para actualizar la barra de estado
        self.editor.bind("<KeyRelease>", self._update_status)
        self.editor.bind("<Button-1>", self._update_status)

    def _on_editor_scroll_y(self, *args):
        # Sincronizar scrollbar con el texto y las líneas
        self.lns.yview_moveto(args[0])
        scrollbar_actual = self.editor.yview()
        self.lns.redraw()  # Redibujar las líneas al hacer scroll
        return args

    def _update_status(self, event=None):
        # Actualizar información de posición en la barra de estado
        position = self.editor.index(tk.INSERT).split('.')
        line, column = position[0], position[1]
        self.status_bar.config(text=f"Línea: {line} | Columna: {column}")

    def importar(self):
        fp = filedialog.askopenfilename(filetypes=[("Pepsi files","*.pepsi"),("All","*.*")])
        if not fp: return
        with open(fp,"r",encoding="utf-8") as f:
            txt = f.read()
        self.editor.delete("1.0",tk.END)
        self.editor.insert("1.0",txt)
        self.lns.redraw()
        self.status_bar.config(text=f"Archivo importado: {os.path.basename(fp)}")

    def guardar(self):
        code = self.editor.get("1.0",tk.END)
        fp = filedialog.asksaveasfilename(defaultextension=".pepsi",
                                          filetypes=[("Pepsi files","*.pepsi"),("All","*.*")])
        if not fp: return
        with open(fp,"w",encoding="utf-8") as f:
            f.write(code)
        self.status_bar.config(text=f"Archivo guardado: {os.path.basename(fp)}")

    def ejecutar(self):
        # 1) volcar a temp.pepsi
        code = self.editor.get("1.0",tk.END)
        os.makedirs(os.path.dirname(TEMP_FILE),exist_ok=True)
        with open(TEMP_FILE,"w",encoding="utf-8") as f:
            f.write(code)
        self.salida.delete("1.0",tk.END)
        self.status_bar.config(text="Ejecutando...")

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
            self.status_bar.config(text="Error en la ejecución")
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
            self.status_bar.config(text="Ejecución fallida: Error de sintaxis")
            return

        # 4) si todo ok, mostrar salida limpia
        clean = []
        for l in (p.stdout + p.stderr).splitlines():
            if l.startswith(("WARNING","[INFO]","[ERROR]","BUILD")):
                continue
            clean.append(l)
        self.salida.insert("1.0", "\n".join(clean))
        self.status_bar.config(text="Ejecución completada")

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
                self.status_bar.config(text=f"Archivo exportado a {lang.upper()}: {os.path.basename(fp)}")
        else:
            messagebox.showwarning("Exportar","No se generó el archivo traducido.")
            self.status_bar.config(text="Exportación fallida")

if __name__ == "__main__":
    app = PepsiIDE()
    app.mainloop()