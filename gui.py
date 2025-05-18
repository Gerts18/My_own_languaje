import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os

JAVA_MAIN_CLASS = "milenguaje.Main"
JAVA_PROJECT_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(JAVA_PROJECT_DIR, "src", "test", "resources")
TEMP_FILE = os.path.join(RESOURCES_DIR, "temp.pepsi")

# Colores y estilos - Tema oscuro
THEME = {
    "bg_main": "#2e3440",           # Fondo principal oscuro (Nord theme)
    "bg_editor": "#3b4252",         # Fondo del editor más oscuro
    "bg_linenumbers": "#2e3440",    # Fondo de números de línea
    "fg_linenumbers": "#d8dee9",    # Color del texto de números (gris claro)
    "bg_output": "#1e1e2e",         # Color de fondo para la salida (aún más oscuro)
    "fg_output": "#50fa7b",         # Color del texto de salida (verde)
    "accent": "#5e81ac",            # Color de acento para elementos destacados (azul)
    "btn_hover": "#81a1c1",         # Color de hover para botones
    "editor_font": ("Consolas", 12), # Fuente del editor
    "output_font": ("Consolas", 11), # Fuente de la salida
    "btn_font": ("Segoe UI", 10),   # Fuente de los botones
    "text_color": "#eceff4",        # Color de texto principal (claro)
    "border_color": "#4c566a",      # Color para bordes
    "title_bg": "#5e81ac",          # Color de la barra de título
    "scrollbar_bg": "#4c566a",      # Color de fondo de scrollbar
    "scrollbar_fg": "#81a1c1",      # Color de scrollbar
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
        self.tag_configure("keyword", foreground="#88c0d0")    # Palabras clave en azul claro
        self.tag_configure("string", foreground="#a3be8c")     # Strings en verde
        self.tag_configure("comment", foreground="#b48ead", font=(THEME["editor_font"][0], THEME["editor_font"][1], "italic"))  # Comentarios en morado
        self.tag_configure("number", foreground="#ebcb8b")     # Números en amarillo claro
        self.tag_configure("operator", foreground="#d08770")   # Operadores en naranja
        self.tag_configure("brackets", foreground="#88c0d0")   # Corchetes en azul
        
        # Establecer vinculaciones para actualizar el resaltado
        self.bind("<KeyRelease>", self.highlight_syntax)
        
    def highlight_syntax(self, event=None):
        # Implementación básica de resaltado de sintaxis para Pepsi
        self.tag_remove("keyword", "1.0", tk.END)
        self.tag_remove("string", "1.0", tk.END)
        self.tag_remove("comment", "1.0", tk.END)
        self.tag_remove("number", "1.0", tk.END)
        self.tag_remove("operator", "1.0", tk.END)
        self.tag_remove("brackets", "1.0", tk.END)
        
        # Palabras clave de Pepsi (detectadas en el ejemplo)
        keywords = ["ent", "Imprime", "SoloSi", "SoloSiTamb", "SiNo", "Recorre"]
        
        # Buscar y resaltar palabras clave
        for keyword in keywords:
            start_pos = "1.0"
            while True:
                start_pos = self.search(keyword, start_pos, tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                self.tag_add("keyword", start_pos, end_pos)
                start_pos = end_pos
                
        # Operadores
        operators = ["->", "+", "-", "*", "/", "[", "]", "(", ")", "{", "}", "<", ">", "="]
        for op in operators:
            start_pos = "1.0"
            while True:
                start_pos = self.search(op, start_pos, tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(op)}c"
                if op in "[](){}":
                    self.tag_add("brackets", start_pos, end_pos)
                else:
                    self.tag_add("operator", start_pos, end_pos)
                start_pos = end_pos
                
        # Números
        start_pos = "1.0"
        while True:
            # Buscar cualquier secuencia de dígitos
            start_pos = self.search(r'\d+', start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            # Encontrar el final del número
            end_pos = f"{start_pos}+1c"
            while self.get(end_pos) in "0123456789.":
                end_pos = f"{end_pos}+1c"
            self.tag_add("number", start_pos, end_pos)
            start_pos = end_pos

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
        
        # Configurar el estilo de scrollbars
        style.configure("Horizontal.TScrollbar", 
                      background=THEME["scrollbar_bg"],
                      troughcolor=THEME["bg_main"], 
                      bordercolor=THEME["border_color"],
                      arrowcolor=THEME["text_color"])
                      
        style.configure("Vertical.TScrollbar", 
                      background=THEME["scrollbar_bg"],
                      troughcolor=THEME["bg_main"], 
                      bordercolor=THEME["border_color"],
                      arrowcolor=THEME["text_color"])
        
        # Map para los estados de scrollbar
        style.map("Horizontal.TScrollbar",
                background=[("active", THEME["scrollbar_fg"]), 
                           ("!disabled", THEME["scrollbar_bg"])])
        style.map("Vertical.TScrollbar",
                background=[("active", THEME["scrollbar_fg"]), 
                           ("!disabled", THEME["scrollbar_bg"])])
        
        # Estilos de botones con colores diferentes
        button_styles = {
            'Import.TButton': {"bg": "#4CAF50", "hover": "#388E3C"},  # Verde - Importar
            'Save.TButton': {"bg": "#2196F3", "hover": "#1565C0"},    # Azul - Guardar
            'Run.TButton': {"bg": "#FF5722", "hover": "#E64A19"},     # Naranja - Ejecutar
            'Python.TButton': {"bg": "#3776AB", "hover": "#2E5D8A"},  # Azul Python
            'JS.TButton': {"bg": "#F7DF1E", "hover": "#D4BE0B", "fg": "black"}  # Amarillo JS
        }
        
        # Crear cada estilo
        for style_name, colors in button_styles.items():
            style.configure(style_name, 
                        background=colors["bg"], 
                        foreground=colors.get("fg", "white"), 
                        font=THEME["btn_font"])
            style.map(style_name, 
                     background=[('active', colors["hover"])])
        
        # Frame principal con borde y sombra simulada
        main_frame = tk.Frame(self, bg=THEME["bg_main"], bd=1, relief=tk.RIDGE, 
                             borderwidth=1, highlightbackground=THEME["border_color"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
        # Título con estilo
        title_frame = tk.Frame(main_frame, bg=THEME["title_bg"], height=30)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="Pepsi IDE", font=("Segoe UI", 12, "bold"), 
                 fg="white", bg=THEME["title_bg"], padx=10).pack(side="left")

        # Editor + líneas con mejor integración
        editor_frame = tk.Frame(main_frame, bg=THEME["bg_editor"])
        editor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Panel editor con scroll
        editor_container = tk.Frame(editor_frame, bg=THEME["bg_editor"])
        editor_container.pack(fill="both", expand=True)
        
        # Crear widget de editor de texto con resaltado básico
        self.editor = SyntaxHighlightingText(
            editor_container, 
            wrap="none", 
            font=THEME["editor_font"],
            bg=THEME["bg_editor"],
            fg=THEME["text_color"],
            insertbackground=THEME["text_color"],
            selectbackground="#5e81ac",
            selectforeground="white",
            undo=True,
            padx=5,
            pady=5
        )
        
        # Números de línea mejorados (canvas)
        self.lns = LineNumbers(editor_container, self.editor, bg=THEME["bg_linenumbers"])
        self.lns.pack(side="left", fill="y")
        
        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(editor_container, orient="vertical", 
                                  command=self.editor.yview, 
                                  style="Vertical.TScrollbar")
        scrollbar_y.pack(side="right", fill="y")
        
        # Empacar el editor - CORREGIDO: debe estar antes del scrollbar horizontal 
        self.editor.pack(side="top", fill="both", expand=True)
        
        # Scrollbar horizontal - CORREGIDO: ahora dentro de editor_container
        scrollbar_x = ttk.Scrollbar(editor_container, orient="horizontal", 
                                  command=self.editor.xview,
                                  style="Horizontal.TScrollbar")
        scrollbar_x.pack(side="bottom", fill="x")
        
        self.editor.config(
            yscrollcommand=self._on_editor_scroll_y,
            xscrollcommand=scrollbar_x.set
        )

        # Barra de botones con estilo mejorado
        buttons_frame = tk.Frame(main_frame, bg=THEME["bg_main"], pady=10)
        buttons_frame.pack(fill="x")
        
        # Botones con iconos (opcionales)
        btns = [
            ("Importar archivo", self.importar, 'Import.TButton', "📂"),  # Icono de carpeta
            ("Guardar código", self.guardar, 'Save.TButton', "💾"),       # Icono de disco
            ("Ejecutar", self.ejecutar, 'Run.TButton', "▶️"),             # Icono de play
            ("Exportar a Python", lambda: self.exportar("py"), 'Python.TButton', "🐍"),  # Icono de serpiente
            ("Exportar a JavaScript", lambda: self.exportar("js"), 'JS.TButton', "☕"),   # Icono de taza
        ]
        
        for i, (text, command, style_name, icon) in enumerate(btns):
            btn = ttk.Button(
                buttons_frame, 
                text=f"{icon} {text}", 
                command=command,
                style=style_name
            )
            btn.pack(side="left", padx=5)

        # ==================== SALIDA/TERMINAL MEJORADA ======================
        # Panel de salida con estilo mejorado
        output_frame = tk.LabelFrame(
            main_frame, 
            text="Salida", 
            font=("Segoe UI", 10, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["text_color"],
            pady=5
        )
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Container para la salida para mantener consistencia con el diseño del editor
        output_container = tk.Frame(output_frame, bg=THEME["bg_output"])
        output_container.pack(fill="both", expand=True)
        
        # Text widget para la salida con scrollbars - ESTRUCTURA CORREGIDA
        self.salida = tk.Text(
            output_container, 
            height=12, 
            wrap="none",
            font=THEME["output_font"], 
            bg=THEME["bg_output"], 
            fg=THEME["fg_output"],
            padx=10,
            pady=10,
            bd=0
        )
        
        # Scrollbars para salida - CORREGIDO para seguir estructura del editor
        output_scroll_y = ttk.Scrollbar(output_container, orient="vertical", 
                                      command=self.salida.yview,
                                      style="Vertical.TScrollbar")
        output_scroll_y.pack(side="right", fill="y")
        
        # Empacar la salida antes del scrollbar horizontal
        self.salida.pack(side="top", fill="both", expand=True)
        
        # Scrollbar horizontal para la salida - CORREGIDO
        output_scroll_x = ttk.Scrollbar(output_container, orient="horizontal", 
                                      command=self.salida.xview,
                                      style="Horizontal.TScrollbar")
        output_scroll_x.pack(side="bottom", fill="x")
        
        self.salida.config(
            yscrollcommand=output_scroll_y.set,
            xscrollcommand=output_scroll_x.set
        )
        
        # Barra de estado
        self.status_bar = tk.Label(
            main_frame, 
            text="Listo", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg=THEME["bg_editor"],
            fg=THEME["text_color"],
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