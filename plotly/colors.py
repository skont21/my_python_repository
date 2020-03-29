import tkinter as tk

COLORS = ['#000000',
'#ffffff',
'#ff0000',
'#00ff00',
'#0000ff',
'#ffff00',
'#ff00ff',
'#00ffff',
'#800000',
'#008000',
'#000080',
'#808000',
'#800080',
'#008080',
'#c0c0c0',
'#808080',
'#9999ff',
'#993366',
'#ffffcc',
'#ccffff',
'#660066',
'#ff8080',
'#0066cc',
'#ccccff',
'#000080',
'#ff00ff',
'#ffff00',
'#00ffff',
'#800080',
'#800000',
'#008080',
'#0000ff',
'#00ccff',
'#ccffff',
'#ccffcc',
'#ffff99',
'#99ccff',
'#ff99cc',
'#cc99ff',
'#ffcc99',
'#3366ff',
'#33cccc',
'#99cc00',
'#ffcc00',
'#ff9900',
'#ff6600',
'#666699',
'#969696',
'#003366',
'#339966',
'#003300',
'#333300',
'#993300',
'#993366',
'#333399',
'#333333'
]


class ColorChart(tk.Frame):

    MAX_ROWS = 7
    FONT_SIZE = 12

    def __init__(self, root):
        tk.Frame.__init__(self, root)
        r = 0
        c = 0
        self.color=None

        def choose_color(b):
            self.color=b['text']
            print(self.color)
            # root.destroy()

        self.grid(row=0, column=0,sticky=tk.NSEW)

        for color in COLORS:

            button = tk.Button(self, text=color, bg=color,font=("Times", self.FONT_SIZE, "bold"))
            button.grid(row=r,column=c, sticky=tk.NSEW,padx=2,pady=2)
            button.config(command= lambda btn=button: choose_color(btn))
            r += 1

            if r > self.MAX_ROWS:
                r = 0
                c += 1




root = tk.Tk()
root.resizable(height=False,width=False)
root.title("Pick Color")
app = ColorChart(root)
root.mainloop()
