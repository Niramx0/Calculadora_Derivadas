import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import io
import base64

from sympy import symbols, diff, sympify, latex, Mul, Poly, Add
from sympy.parsing.latex import parse_latex
x = symbols('x')

def obtener_coeficientes(polinomio):
    poli = Poly(polinomio, x) #Poly se encarga de extraer el coeficiente de cada x en el polinomio
    coeficientes = poli.all_coeffs()  # .all_coeffs ordena la lista de coeficientes de mayor a menor grado
    exponentes = list(range(poli.degree(), -1,-1))  # ordenamos también los exponentes que obtiene de .degree() de mayor a menor
    return list(zip(coeficientes, exponentes)) #retornando como resultado una tupla que contenga el coeficiente que multiplica a x + su exponente ([1, 3] por ej es la tupla que indica que el exponente que se eleva a la 3 tiene un coeficiente de 1)

def regla_derivada(expresion_parseada):
  #primera condición: si tenemos un término multiplicando
    if isinstance(expresion_parseada, Mul):
        factores = expresion_parseada.args
        #print(factores) #visualiza la lista de factores por lo que va a multiplicar
        resultado = 0
        for i in range(len(factores)):
            derivada_i = regla_derivada(factores[i])
            #print(derivada_i) #para observar cada deriva que vaya sacando
            producto_restante = Mul(*[factores[j] if j != i else derivada_i for j in range(len(factores))]) #acá juega con el Mul de sympy (objeto que es como el que define una multiplicación por *, igual que el + en Add)
            resultado += producto_restante
        return resultado
  #segunda condición: si tenemos un termino sumando
    elif isinstance(expresion_parseada, Add):
      return Add(*[regla_derivada(arg) for arg in expresion_parseada.args])
  #ya por último si está solo el polinomio lo deriva normalmente
    else:
        resultado = obtener_coeficientes(expresion_parseada)
        #print(resultado) #para visualizar cada 'resultado' en forma de lista 
        resultado_derivado = 0
        for coef, exp in resultado:
            if exp == 0 or coef == 0:
                continue
            else:
                resultado_derivado += coef * exp * x**(exp - 1)
        #print(resultado_derivado) #visualiza el resultado que está tomando cada que le aplique la regla f'(x)=n*x^{n-1} en el polinomio enlistado
        return resultado_derivado
    
def derivar(expresion_latex):
    try:
        expr = parse_latex(expresion_latex)
        #print(expr) #para ver la expresión parseada de latex a sympy
        derivada = regla_derivada(expr)
        return {
            'success': True,
            'original': expr,
            'original_latex': latex(expr),
            'derivative': derivada,
            'derivative_latex': latex(derivada)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Por favor, revisa si tu función cumple con los parámetros indicados en el instructivo y si no revisa con calma este error: {e}"
        }

#expr_latex = r"(13-x^{3})*((x^{3}*(x+4))+3x)"
#resultado = derivar(expr_latex)

#resultado_simplificado_real_de_la_derivada = diff(expresion_parseada, x) #esta es la forma de derivar con una función de sympy (que no usaremos por propósito académico)

#print(resultado) #el resultado queda como un output de string en latex en forma de factor de polinomios

class CalculadoraDerivadas:
    def __init__(self, root):
        self.root = root
        self.root.title("🧮 Calculadora de Derivadas con LaTeX")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', 
                           font=('Arial', 20, 'bold'),
                           foreground='#2c3e50',
                           background='#f0f0f0')
        
        self.style.configure('Header.TLabel',
                           font=('Arial', 12, 'bold'),
                           foreground='#34495e',
                           background='#f0f0f0')
        
        self.style.configure('Custom.TButton',
                           font=('Arial', 10, 'bold'),
                           padding=10)
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        titulo = ttk.Label(main_frame, text="📊 Calculadora de Derivadas", style='Title.TLabel')
        titulo.pack(pady=(0, 10))
        
        subtitulo = ttk.Label(main_frame, text="Ingresa expresiones matemáticas en formato LaTeX", 
                             font=('Arial', 10), foreground='#7f8c8d', background='#f0f0f0')
        subtitulo.pack(pady=(0, 20))
        entrada_frame = ttk.LabelFrame(main_frame, text="📝 Entrada LaTeX", padding="15")
        entrada_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(entrada_frame, text="Expresión en LaTeX:", style='Header.TLabel').pack(anchor=tk.W)
        
        self.entrada_texto = scrolledtext.ScrolledText(entrada_frame, 
                                                      height=3, 
                                                      font=('Courier New', 11),
                                                      wrap=tk.WORD)
        self.entrada_texto.pack(fill=tk.X, pady=(5, 10))
        self.entrada_texto.insert('1.0', '(13-x^{3})*((x^{3}*(x+4))+3x)')
        botones_frame = ttk.Frame(entrada_frame)
        botones_frame.pack(fill=tk.X)
        
        ttk.Button(botones_frame, text="🧮 Calcular Derivada", 
                  command=self.calcular_derivada, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(botones_frame, text="🗑️ Limpiar", 
                  command=self.limpiar_campos, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(botones_frame, text="📊 Graficar", 
                  command=self.graficar_funciones, style='Custom.TButton').pack(side=tk.LEFT)
        self.resultado_frame = ttk.LabelFrame(main_frame, text="📈 Resultados", padding="15")
        self.resultado_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        ttk.Label(self.resultado_frame, text="Función original:", style='Header.TLabel').pack(anchor=tk.W)
        self.funcion_original = scrolledtext.ScrolledText(self.resultado_frame, 
                                                         height=3, 
                                                         font=('Courier New', 10),
                                                         state=tk.DISABLED,
                                                         bg='#ecf0f1')
        self.funcion_original.pack(fill=tk.X, pady=(5, 10))
        ttk.Label(self.resultado_frame, text="Derivada:", style='Header.TLabel').pack(anchor=tk.W)
        self.derivada_resultado = scrolledtext.ScrolledText(self.resultado_frame, 
                                                           height=3, 
                                                           font=('Courier New', 10),
                                                           state=tk.DISABLED,
                                                           bg='#e8f5e8')
        self.derivada_resultado.pack(fill=tk.X, pady=(5, 15))
        self.grafico_frame = ttk.Frame(self.resultado_frame)
        self.grafico_frame.pack(fill=tk.BOTH, expand=True)
        ejemplos_frame = ttk.LabelFrame(main_frame, text="💡 Ejemplos", padding="10")
        ejemplos_frame.pack(fill=tk.X, pady=(15, 0))
        
        ejemplos = [
            "(13-x^{3})*((x^{3}*(x+4))+3x)",
            "x^{5} + 3x^{2} - 7x + 2",
            "(x^{2} + 1)(x^{3} - 2x)",
            "x^{4} - 8x^{3} + 12x^{2} - 5"
        ]
        
        for i, ejemplo in enumerate(ejemplos):
            btn = ttk.Button(ejemplos_frame, text=ejemplo, 
                           command=lambda e=ejemplo: self.cargar_ejemplo(e),
                           width=30)
            btn.pack(side=tk.LEFT if i % 2 == 0 else tk.RIGHT, padx=5, pady=2)
        self.entrada_texto.bind('<Control-Return>', lambda e: self.calcular_derivada())
        
    def cargar_ejemplo(self, ejemplo):
        self.entrada_texto.delete('1.0', tk.END)
        self.entrada_texto.insert('1.0', ejemplo)
        
    def limpiar_campos(self):
        self.entrada_texto.delete('1.0', tk.END)
        self.funcion_original.config(state=tk.NORMAL)
        self.funcion_original.delete('1.0', tk.END)
        self.funcion_original.config(state=tk.DISABLED)
        self.derivada_resultado.config(state=tk.NORMAL)
        self.derivada_resultado.delete('1.0', tk.END)
        self.derivada_resultado.config(state=tk.DISABLED)
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()
    
    def calcular_derivada(self):
        expresion_latex = self.entrada_texto.get('1.0', tk.END).strip()
        
        if not expresion_latex:
            messagebox.showwarning("Advertencia", "Por favor ingresa una expresión LaTeX.")
            return
        
        try:
            resultado = derivar(expresion_latex)
            self.funcion_original.config(state=tk.NORMAL)
            self.derivada_resultado.config(state=tk.NORMAL)
            
            self.funcion_original.delete('1.0', tk.END)
            self.derivada_resultado.delete('1.0', tk.END)
            
            if resultado['success']:
                self.funcion_original.insert('1.0', f"LaTeX: {resultado['original_latex']}\n\n")
                self.funcion_original.insert(tk.END, f"Sympy: {resultado['original']}")                
                self.derivada_resultado.insert('1.0', f"LaTeX: {resultado['derivative_latex']}\n\n")
                self.derivada_resultado.insert(tk.END, f"Sympy: {resultado['derivative']}")
                self.funcion_original.config(bg='#e8f5e8')
                self.derivada_resultado.config(bg='#e8f5e8')
                self.funcion_actual = resultado['original']
                self.derivada_actual = resultado['derivative']
                
                messagebox.showinfo("Éxito", "¡Derivada calculada correctamente!")
                
            else:
                self.funcion_original.insert('1.0', "Error en la expresión de entrada")
                self.derivada_resultado.insert('1.0', resultado['error'])
                self.funcion_original.config(bg='#ffeaea')
                self.derivada_resultado.config(bg='#ffeaea')
                
                messagebox.showerror("Error", resultado['error'])
            
            self.funcion_original.config(state=tk.DISABLED)
            self.derivada_resultado.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def graficar_funciones(self):
        if not hasattr(self, 'funcion_actual') or not hasattr(self, 'derivada_actual'):
            messagebox.showwarning("Advertencia", "Primero calcula una derivada para poder graficar.")
            return
        
        try:
            for widget in self.grafico_frame.winfo_children():
                widget.destroy()
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            fig.patch.set_facecolor('#f0f0f0')
            x_vals = np.linspace(-5, 5, 1000)
            
            from sympy import lambdify
            f_func = lambdify(x, self.funcion_actual, 'numpy')
            df_func = lambdify(x, self.derivada_actual, 'numpy')
            
            try:
                y_vals = f_func(x_vals)
                dy_vals = df_func(x_vals)
                ax1.plot(x_vals, y_vals, 'b-', linewidth=2, label='f(x)')
                ax1.set_title('Función Original', fontsize=12, fontweight='bold')
                ax1.grid(True, alpha=0.3)
                ax1.set_xlabel('x')
                ax1.set_ylabel('f(x)')
                ax1.legend()
                ax2.plot(x_vals, dy_vals, 'r-', linewidth=2, label="f'(x)")
                ax2.set_title('Derivada', fontsize=12, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                ax2.set_xlabel('x')
                ax2.set_ylabel("f'(x)")
                ax2.legend()
                
                plt.tight_layout()
                
                # Integrar en tkinter
                canvas = FigureCanvasTkAgg(fig, self.grafico_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
            except Exception as e:
                messagebox.showwarning("Advertencia de Gráficos", 
                                     f"No se pudo graficar la función (posiblemente contiene valores complejos): {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error de Gráficos", f"Error al crear gráficos: {str(e)}")

def main():
    root = tk.Tk()
    app = CalculadoraDerivadas(root)
    root.mainloop()

if __name__ == "__main__":
    main()