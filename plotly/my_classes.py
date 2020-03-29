import tkinter as tk
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.text import Text
from matplotlib.lines import Line2D
import locale
locale.setlocale(locale.LC_ALL, '')

weights = ['normal','bold',]
styles = ['normal', 'italic']
families = ['serif', 'sans-serif','DejaVu Sans']
linestyles = ['-', '--', '-.', ':']
which = ['major','minor','both']
which_axis = ['both','y','x']

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
            # print(self.color)
            root.destroy()

        self.grid(row=0, column=0,sticky=tk.NSEW)

        for color in COLORS:

            button = tk.Button(self, text=color, bg=color,font=("Times", self.FONT_SIZE, "bold"))
            button.grid(row=r,column=c, sticky=tk.NSEW,padx=2,pady=2)
            button.config(command= lambda btn=button: choose_color(btn))
            r += 1

            if r > self.MAX_ROWS:
                r = 0
                c += 1

class NavigationToolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] in ('Pan', 'Zoom', 'Save')]

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground

class move_obj:
    def __init__(self,obj,figure,align,parent):
        self.obj=obj
        self.figure=figure
        self.pick=None
        self.align=align
        self.parent=parent
        self.ending=False

    def connect_obj(self):
        'connect to all the events we need'
        self.cidpress = self.figure.canvas.mpl_connect('pick_event', self.on_pick_obj)
        self.cidrelease = self.figure.canvas.mpl_connect('button_release_event', self.on_release_obj)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion_obj)
        self.ciddouble = self.figure.canvas.mpl_connect('button_press_event', self.onclik)

    def on_pick_obj(self, event):
        'on button pick we will see if the mouse is over us and store some data'
        if isinstance(event.artist, Text):
            if isinstance(self.obj,Text):

                transf = self.figure.axes[0].transData.inverted()
                bb = self.obj.get_window_extent(renderer = self.figure.canvas.renderer)
                bb_datacoords = bb.transformed(transf)

                x0 = event.mouseevent.xdata
                y0 = event.mouseevent.ydata

                if self.align=="Arrow":
                    if self.obj.xy[0]>self.obj.xyann[0]:
                        if (x0>bb_datacoords.xmin+(bb_datacoords.xmax-bb_datacoords.xmin)/2):
                            if (x0>bb_datacoords.xmax)|(y0>bb_datacoords.ymax*1.01)|(y0<bb_datacoords.ymin*0.99):
                                return
                            # print("Ending")
                            self.ending = True
                            self.pick = True
                        else:
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax*1.01)|(y0<bb_datacoords.ymin*0.99):
                                return
                            # print("Beginning")
                            self.pick = True
                    else:
                        if (x0<bb_datacoords.xmin+(bb_datacoords.xmax-bb_datacoords.xmin)/2):
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax*1.01)|(y0<bb_datacoords.ymin*0.99):
                                return
                            self.ending = True
                            self.pick = True
                        else:
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax*1.01)|(y0<bb_datacoords.ymin*0.99):
                                return
                            self.pick = True
                elif self.align==None:
                    if (x0>bb_datacoords.xmax)|(x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax*1.01)|(y0<bb_datacoords.ymin*0.99):
                        return
                    self.pick = True
        elif isinstance(event.artist, Line2D):
            if isinstance(self.obj,Line2D)&(self.align=="Vertical"):
                xlim_cur=self.figure.axes[0].get_xlim()[1]-self.figure.axes[0].get_xlim()[0]
                ylim_cur=self.figure.axes[0].get_ylim()[1]-self.figure.axes[0].get_ylim()[0]
                self.xl = self.obj.get_xdata()
                self.yl = self.obj.get_ydata()
                if abs(self.xl[0]-event.mouseevent.xdata)>(xlim_cur)*(500/86400):
                    return
                self.pick=True
            elif isinstance(self.obj,Line2D)&(self.align=="Horizontal"):
                xlim_cur=self.figure.axes[0].get_xlim()[1]-self.figure.axes[0].get_xlim()[0]
                ylim_cur=self.figure.axes[0].get_ylim()[1]-self.figure.axes[0].get_ylim()[0]
                self.xl = self.obj.get_xdata()
                self.yl = self.obj.get_ydata()
                if abs(self.yl[0]-event.mouseevent.ydata)>(ylim_cur/100):
                    return
                self.pick=True

    def on_motion_obj(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.pick is None:
            return
        if event.inaxes != self.figure.axes[0]:
            return
        if isinstance(self.obj,Text):
            if self.align==None:
                self.obj.set_position((event.xdata,event.ydata))
                try:
                    self.figure.canvas.draw()
                except:pass
            elif self.align=="Arrow":
                if not self.ending:
                    self.obj.set_position((event.xdata,event.ydata))
                    try:
                        self.figure.canvas.draw()
                    except:pass
                else:
                    self.obj.xy = (event.xdata,event.ydata)
                    try:
                        self.figure.canvas.draw()
                    except:pass
        elif isinstance(self.obj,Line2D):
            if self.align=="Vertical":
                self.obj.set_xdata((event.xdata,event.xdata))
                self.figure.canvas.draw()
            if self.align=="Horizontal":
                self.obj.set_ydata((event.ydata,event.ydata))
                self.figure.canvas.draw()

    def on_release_obj(self, event):
        'on release we reset the press data'
        self.pick = None
        self.ending=False
        try:
            self.figure.canvas.draw()
        except:pass

    def onclik(self,event):
        if self.pick is None:
            return
        if event.dblclick:
            if event.button == 1:
                if self.obj in self.figure.axes[0].texts:
                    if self.align==None:
                        def apply_text():
                            self.obj.set_text(e_text.get())
                            try:
                                self.obj.set_rotation(float(text_rot.get()))
                            except:
                                self.obj.set_rotation(0)
                            try:
                                self.obj.set_fontsize(float(text_size.get()))
                            except:
                                self.obj.set_fontsize(12)
                            try:
                                self.obj.get_bbox_patch().set_linewidth(text_frame.get())
                            except:
                                self.obj.get_bbox_patch().set_linewidth(1)
                            try:
                                self.obj.get_bbox_patch().set_alpha(float(text_alpha.get()))
                            except:
                                self.obj.get_bbox_patch().set_alpha(1)

                            self.obj.set_fontweight(var_weight.get())
                            self.obj.set_fontstyle(var_style.get())
                            self.figure.canvas.draw()
                            change_text.destroy()

                        def delete_text():
                            self.obj.remove()
                            self.figure.canvas.draw()
                            change_text.destroy()

                        def text_t_color():
                            c_ch = tk.Toplevel(change_text)
                            c_ch.resizable(width=False, height=False)
                            c_ch.withdraw()
                            c_ch.protocol("WM_DELETE_WINDOW")
                            app = ColorChart(c_ch)
                            c_ch.deiconify()
                            c_ch.grab_set()
                            c_ch.wait_window(c_ch)
                            color=app.color
                            if color != None:
                                self.obj.set_color(color)
                                text_c_button.config(background=color)
                                text_c_button.config(activebackground=text_c_button.cget('background'))

                        def text_bg_color():
                            c_ch = tk.Toplevel(change_text)
                            c_ch.resizable(width=False, height=False)
                            c_ch.withdraw()
                            c_ch.protocol("WM_DELETE_WINDOW")
                            app = ColorChart(c_ch)
                            c_ch.deiconify()
                            c_ch.grab_set()
                            c_ch.wait_window(c_ch)
                            color=app.color
                            if color != None:
                                self.obj.get_bbox_patch().set_facecolor(color)
                                text_bc_button.config(background=color)
                                text_bc_button.config(activebackground=text_bc_button.cget('background'))

                        def text_eg_color():
                            c_ch = tk.Toplevel(change_text)
                            c_ch.resizable(width=False, height=False)
                            c_ch.withdraw()
                            c_ch.protocol("WM_DELETE_WINDOW")
                            app = ColorChart(c_ch)
                            c_ch.deiconify()
                            c_ch.grab_set()
                            c_ch.wait_window(c_ch)
                            color=app.color
                            if color != (None,None):
                                self.obj.get_bbox_patch().set_edgecolor(color)
                                text_ec_button.config(background=color)
                                text_ec_button.config(activebackground=text_ec_button.cget('background'))

                        try:
                            if 'normal' == change_text.state():
                                change_text.lift()
                        except:
                            change_text=tk.Toplevel(self.parent)
                            change_text.resizable(height=False,width=False)
                            change_text.title("Text")

                            label_text = tk.Label(change_text, text="Insert Text").grid(row=0)
                            e_text = tk.Entry(change_text,bd=5,width=40)
                            e_text.insert(0,self.obj.get_text())
                            e_text.grid(row=0,column=1)

                            text_rot_label = tk.Label(change_text,text="Rotation").grid(row=1)
                            var_rot=tk.StringVar(change_text)
                            var_rot.set(self.obj.get_rotation())
                            text_rot = tk.Spinbox(change_text,from_=0,to=360,bd=5,width=5,textvariable=var_rot,increment=5)
                            text_rot.grid(row=1,column=1,sticky=tk.W)

                            text_size_label = tk.Label(change_text,text="Size").grid(row=2)
                            var_size=tk.StringVar(change_text)
                            var_size.set(self.obj.get_fontsize())
                            text_size=tk.Spinbox(change_text,from_=2,to=30,bd=5,width=5,textvariable=var_size,increment=0.5)
                            text_size.grid(row=2,column=1,sticky=tk.W)

                            text_weight_label = tk.Label(change_text, text="FontWeight").grid(row=3)
                            var_weight = tk.StringVar(change_text)
                            var_weight.set(self.obj.get_fontweight())
                            text_weight = tk.OptionMenu(change_text, var_weight, *weights)
                            text_weight.grid(row=3,column=1,sticky=tk.W)

                            text_style_label = tk.Label(change_text, text="FontStyle").grid(row=4)
                            var_style = tk.StringVar(change_text)
                            var_style.set(self.obj.get_fontstyle())
                            text_style = tk.OptionMenu(change_text, var_style, *styles)
                            text_style.grid(row=4,column=1,sticky=tk.W)

                            text_frame_label = tk.Label(change_text,text="FrameWidth").grid(row=5)
                            var_frame=tk.StringVar(change_text)
                            var_frame.set(self.obj.get_bbox_patch().get_linewidth())
                            text_frame=tk.Spinbox(change_text,from_=0,to=10,bd=5,width=5,textvariable=var_frame,increment=0.5)
                            text_frame.grid(row=5,column=1,sticky=tk.W)

                            t_color = self.obj.get_color()
                            te_color_rgb= self.obj.get_bbox_patch().get_edgecolor()
                            te_color='#%02x%02x%02x' %  (int(te_color_rgb[0]*255),int(te_color_rgb[1]*255),int(te_color_rgb[2]*255))
                            tb_color_rgb= self.obj.get_bbox_patch().get_facecolor()
                            tb_color='#%02x%02x%02x' %  (int(tb_color_rgb[0]*255),int(tb_color_rgb[1]*255),int(tb_color_rgb[2]*255))

                            text_c_label= tk.Label(change_text,text="Text Color").grid(row=6)
                            text_c_button= tk.Button(change_text,background =t_color,command=text_t_color)
                            text_c_button.config(activebackground=text_c_button.cget('background'))
                            text_c_button.grid(row=6,column=1,sticky=tk.W)

                            text_bc_label= tk.Label(change_text,text="Background Color").grid(row=7)
                            text_bc_button= tk.Button(change_text,text="          ",background =tb_color,command=text_bg_color)
                            text_bc_button.config(activebackground=text_bc_button.cget('background'))
                            text_bc_button.grid(row=7,column=1,sticky=tk.W)

                            text_ec_label= tk.Label(change_text,text="Edge Color").grid(row=8)
                            text_ec_button= tk.Button(change_text,text="          ",background =te_color,command=text_eg_color)
                            text_ec_button.config(activebackground=text_ec_button.cget('background'))
                            text_ec_button.grid(row=8,column=1,sticky=tk.W)

                            text_alpha_label= tk.Label(change_text,text="Opacity").grid(row=9)
                            var_alpha=tk.StringVar(change_text)
                            var_alpha.set(self.obj.get_bbox_patch().get_alpha())
                            text_alpha = tk.Spinbox(change_text,from_=0, to=1,bd=5,width=5,textvariable=var_alpha,increment=0.05)
                            text_alpha.grid(row=9,column=1,sticky=tk.W)

                            quit_text=tk.Button(change_text, text='Delete',command=delete_text).grid(row=10, column=0, sticky=tk.W, pady=4)
                            apply_text = tk.Button(change_text,text='Apply',command=apply_text).grid(row=10,column=1,sticky=tk.W, pady=4)
                    else:

                        def ar_color():
                            c_ch = tk.Toplevel(change_arrows)
                            c_ch.resizable(width=False, height=False)
                            c_ch.withdraw()
                            c_ch.protocol("WM_DELETE_WINDOW")
                            app = ColorChart(c_ch)
                            c_ch.deiconify()
                            c_ch.grab_set()
                            c_ch.wait_window(c_ch)
                            color=app.color
                            if  color != None:
                                self.obj.arrow_patch.set_edgecolor(color)
                                arrow_color_button.config(background=color)
                                arrow_color_button.config(activebackground=arrow_color_button.cget('background'))

                        def delete_arrows():
                            self.obj.remove()
                            self.figure.canvas.draw_idle()
                            change_arrows.destroy()

                        def edit_arrows():
                            try:
                                self.obj.arrow_patch.set_linewidth(float(e_arrow_width.get()))
                            except:
                                self.obj.arrowprops['lw']=2
                            try:
                                self.obj.arrow_patch.set_alpha(float(e_arrow_alpha.get()))
                            except:
                                self.obj.arrowprops['alpha']= 1

                            self.obj.arrow_patch.set_linestyle(arrow_linestyle_val.get())

                            self.figure.canvas.draw_idle()
                            change_arrows.destroy()

                        try:
                          if 'normal' == change_arrows.state():
                              change_arrows.lift()
                        except:
                          change_arrows=tk.Toplevel(self.parent)
                          change_arrows.resizable(width=False,height=False)
                          change_arrows.title("arrows")

                          arrow_title= tk.Label(change_arrows,text=self.align+" arrow").grid(row=0,columnspan=2)

                          arrow_width= tk.Label(change_arrows,text="Width").grid(row=1)
                          arrow_width_val=tk.StringVar(change_arrows)
                          arrow_width_val.set(self.obj.arrow_patch.get_linewidth())
                          e_arrow_width = tk.Spinbox(change_arrows,from_=1, to=30,bd=5,width=5,textvariable=arrow_width_val,increment=0.5)
                          e_arrow_width.grid(row=1,column=1)

                          arrow_alpha= tk.Label(change_arrows,text="Opacity").grid(row=2)
                          arrow_alpha_val=tk.StringVar(change_arrows)
                          arrow_alpha_val.set(self.obj.arrow_patch.get_alpha())
                          e_arrow_alpha = tk.Spinbox(change_arrows,from_=0, to=1,bd=5,width=5,textvariable=arrow_alpha_val,increment=0.05)
                          e_arrow_alpha.grid(row=2,column=1)

                          arrow_linestyle= tk.Label(change_arrows,text="Style").grid(row=3)
                          arrow_linestyle_val=tk.StringVar(change_arrows)
                          arrow_linestyle_val.set(self.obj.arrow_patch.get_linestyle())
                          e_arrow_linestyle = tk.OptionMenu(change_arrows, arrow_linestyle_val, *linestyles)
                          e_arrow_linestyle.grid(row=3,column=1)

                          arrow_color_rgb = self.obj.arrow_patch.get_edgecolor()
                          arrow_color = '#%02x%02x%02x' %  (int(arrow_color_rgb[0]*255),int(arrow_color_rgb[1]*255),int(arrow_color_rgb[2]*255))

                          arrow_color_label= tk.Label(change_arrows,text="Color").grid(row=4)
                          arrow_color_button= tk.Button(change_arrows,text="          ",background =arrow_color)
                          arrow_color_button.config(activebackground=arrow_color_button.cget('background'))
                          arrow_color_button.config(command=ar_color)
                          arrow_color_button.grid(row=4,column=1,sticky=tk.W)

                        quit_arrows=tk.Button(change_arrows, text='Delete',command=delete_arrows).grid(row=5, column=0, sticky=tk.W, pady=4)
                        apply_arrows = tk.Button(change_arrows,text='Apply', command=edit_arrows).grid(row=5,column=1,sticky=tk.W, pady=4)

                elif self.obj in self.figure.axes[0].lines:

                    def l_color():
                        c_ch = tk.Toplevel(change_lines)
                        c_ch.resizable(width=False, height=False)
                        c_ch.withdraw()
                        c_ch.protocol("WM_DELETE_WINDOW")
                        app = ColorChart(c_ch)
                        c_ch.deiconify()
                        c_ch.grab_set()
                        c_ch.wait_window(c_ch)
                        color=app.color
                        if  color != None:
                            self.obj.set_color(color)
                            line_color_button.config(background=color)
                            line_color_button.config(activebackground=line_color_button.cget('background'))

                    def delete_lines():
                        self.obj.remove()
                        self.figure.canvas.draw_idle()
                        change_lines.destroy()

                    def edit_lines():
                        try:
                            self.obj.set_linewidth(float(e_line_width.get()))
                        except:
                            self.obj.set_linewidth(2)
                        try:
                            self.obj.set_alpha(float(e_line_alpha.get()))
                        except:
                            self.obj.set_alpha(1)

                        self.obj.set_linestyle(line_style_val.get())

                        self.figure.canvas.draw_idle()
                        change_lines.destroy()

                    try:
                        if 'normal' == change_lines.state():
                            change_lines.lift()
                    except:

                        change_lines=tk.Toplevel(self.parent)
                        change_lines.resizable(width=False,height=False)
                        change_lines.title("Lines")

                        line_title= tk.Label(change_lines,text=self.align+" Line").grid(row=0,columnspan=2)

                        line_width= tk.Label(change_lines,text="Width").grid(row=1)
                        line_width_val=tk.StringVar(change_lines)
                        line_width_val.set(self.obj.get_linewidth())
                        e_line_width = tk.Spinbox(change_lines,from_=1, to=30,bd=5,width=5,textvariable=line_width_val,increment=0.5)
                        e_line_width.grid(row=1,column=1)

                        line_alpha= tk.Label(change_lines,text="Opacity").grid(row=2)
                        line_alpha_val=tk.StringVar(change_lines)
                        line_alpha_val.set(self.obj.get_alpha())
                        e_line_alpha = tk.Spinbox(change_lines,from_=0, to=1,bd=5,width=5,textvariable=line_alpha_val,increment=0.05)
                        e_line_alpha.grid(row=2,column=1)

                        line_style= tk.Label(change_lines,text="Style").grid(row=3)
                        line_style_val=tk.StringVar(change_lines)
                        line_style_val.set(self.obj.get_linestyle())
                        e_line_style = tk.OptionMenu(change_lines, line_style_val, *linestyles)
                        e_line_style.grid(row=3,column=1)

                        line_color = self.obj.get_color()

                        line_color_label= tk.Label(change_lines,text="Color").grid(row=4)
                        line_color_button= tk.Button(change_lines,text="          ",background =line_color)
                        line_color_button.config(activebackground=line_color_button.cget('background'))
                        line_color_button.config(command=l_color)
                        line_color_button.grid(row=4,column=1,sticky=tk.W)

                    quit_lines=tk.Button(change_lines, text='Delete',command=delete_lines).grid(row=5, column=0, sticky=tk.W, pady=4)
                    apply_lines = tk.Button(change_lines,text='Apply', command=edit_lines).grid(row=5,column=1,sticky=tk.W, pady=4)


    def disconnect_obj(self):
        'disconnect all the stored connection ids'
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
