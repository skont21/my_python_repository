# %matplotlib notebook
from plot_maplot_v1 import *
from recourses import *
import base64
import io
import tkinter as tk
from tkinter import colorchooser,filedialog,simpledialog,messagebox,ttk,PhotoImage
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.lines import Line2D
from matplotlib.text import Text
import matplotlib as mpl
import sys
import re
import numpy as np
import matplotlib.dates as mdates
mpl.use('TkAgg')
num_tr=0
sel_traces=[]
grid_color=((11,11,11),'#b0b0b0')
dead_flag = 0
line_deads=[]
line_deads_val=[]
time_xaxis=True
strace=1

weights = ['normal','bold',]
styles = ['normal', 'italic']
families = ['serif', 'sans-serif','DejaVu Sans']
linestyles = ['-', '--', '-.', ':']
which = ['major','minor','both']
which_axis = ['both','y','x']


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
                            if (x0>bb_datacoords.xmax)|(y0>bb_datacoords.ymax)|(y0<bb_datacoords.ymin):
                                return
                            self.ending = True
                            self.pick = True
                        else:
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax)|(y0<bb_datacoords.ymin):
                                return
                            self.pick = True
                    else:
                        if (x0<bb_datacoords.xmin+(bb_datacoords.xmax-bb_datacoords.xmin)/2):
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax)|(y0<bb_datacoords.ymin):
                                return
                            self.ending = True
                            self.pick = True
                        else:
                            if (x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax)|(y0<bb_datacoords.ymin):
                                return
                            self.pick = True
                elif self.align==None:
                    if (x0>bb_datacoords.xmax)|(x0<bb_datacoords.xmin)|(y0>bb_datacoords.ymax)|(y0<bb_datacoords.ymin):
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
                            color=colorchooser.askcolor(title="Pick Color")
                            if color != (None,None):
                                self.obj.set_color(color[1])
                                text_c_button.config(background=color[1])
                                text_c_button.config(activebackground=text_c_button.cget('background'))

                        def text_bg_color():
                            color=colorchooser.askcolor(title="Pick Color")
                            if color != (None,None):
                                self.obj.get_bbox_patch().set_facecolor(color[1])
                                text_bc_button.config(background=color[1])
                                text_bc_button.config(activebackground=text_bc_button.cget('background'))

                        def text_eg_color():
                            color=colorchooser.askcolor(title="Pick Color")
                            if color != (None,None):
                                self.obj.get_bbox_patch().set_edgecolor(color[1])
                                text_ec_button.config(background=color[1])
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
                            color=colorchooser.askcolor(title="Pick Color")
                            if  color != (None,None):
                                self.obj.arrow_patch.set_edgecolor(color[1])
                                arrow_color_button.config(background=color[1])
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
                        color=colorchooser.askcolor(title="Pick Color")
                        if  color != (None,None):
                            self.obj.set_color(color[1])
                            line_color_button.config(background=color[1])
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

csv=''
# while not csv:
input_csv = tk.Tk()
input_csv.withdraw()
csv = filedialog.askopenfilename(initialdir = "/home",title = "Select csv file",filetypes = (("csv files","*.csv"),),parent=input_csv)
if not csv:
    sys.exit()

data = get_data_from_csv(csv)

(time,m,s,en)=get_traces(data)

plots=dict()
i=1
for k in en.keys():
    if int(en[k].sum())!=0:
        plots[str(i)]=k
        i=i+1
if ('P' in en.keys())&('Q' in en.keys()):
    plots[str(i)]='Q Capability'
    i=i+1
plots[str(i)]="All Measurements"
plots[str(i+1)]="Custom Plot"
def destroyer():
    choose_plot.quit()
    choose_plot.destroy()

choose_plot = tk.Tk()
choose_plot.protocol("WM_DELETE_WINDOW",destroyer)
choose_plot.title("Available Plots")
choose_plot.resizable(width=False, height=False)
choose_plot.geometry("")
choose_plot.config(background='#000000')
choose_plot.grid_columnconfigure(0, weight=1)
choose_plot.grid_rowconfigure(0, weight=1)

style = ttk.Style()
style.map('TCombobox', fieldbackground=[('readonly','lightgrey')])
style.map('TCombobox', selectbackground=[('readonly', 'lightgrey')])
style.map('TCombobox', selectforeground=[('readonly', 'black')])

def plot_choise(button):
    global strace
    global line_deads_val

    def ask_trace(title,sets):

        def get_strace():
            global strace
            trace=select_trace_val.get()
            strace = traces.index(trace) +1
            input_trace.destroy()

        input_trace=tk.Toplevel(choose_plot)
        input_trace.geometry("+{}+{}".format(choose_plot.winfo_x(),choose_plot.winfo_y()))
        input_trace.resizable(width=False, height=False)
        input_trace.withdraw()
        input_trace.protocol("WM_DELETE_WINDOW")
        input_trace.title(title)

        tk.Label(input_trace,text="Please select trace for "+title).grid(row=0,column=0,columnspan=2)

        traces = list(sets.columns)

        select_trace_val = tk.StringVar(input_trace)
        select_trace_val.set(traces[0])
        e_select_trace = tk.OptionMenu(input_trace, select_trace_val, *traces)
        e_select_trace.grid(row=1,column=0,columnspan=2,sticky=tk.NSEW)

        quit_trace = tk.Button(input_trace,text='Apply',command=get_strace)
        quit_trace.grid(row=2,columnspan=2)
        input_trace.deiconify()
        input_trace.grab_set()
        input_trace.wait_window(input_trace)

    button_text = button.cget("text")

    def ask_xtrace(data,title):
        global sel_x

        def apply_trace():
            global sel_x
            sel_x = w_x.get()
            custom_trace.destroy()

        custom_trace=tk.Toplevel(choose_plot)
        custom_trace.resizable(width=False, height=False)
        # custom_trace.geometry("200x70")
        custom_trace.grid_columnconfigure(0, weight=1)
        custom_trace.grid_rowconfigure(0, weight=1)
        custom_trace.withdraw()
        custom_trace.protocol("WM_DELETE_WINDOW")
        custom_trace.title(title)

        choices = list(data.columns)

        x_ch =tk.Frame(custom_trace)
        x_ch.grid(row=0,column=0,sticky=tk.NSEW)
        x_ch.grid_columnconfigure(0,weight=1)

        w_x = ttk.Combobox(x_ch, values=choices,state="readonly",justify='center')
        w_x.current(0)
        w_x.grid(row=0,columnspan=2,sticky=tk.NSEW)

        buts =tk.Frame(custom_trace)
        buts.grid(row=1,column=0,sticky=tk.NSEW)
        buts.grid_columnconfigure(0,weight=1)
        custom_apply = tk.Button(buts,text="Apply",command=apply_trace)
        custom_apply.grid(row=1,column=0,columnspan=2,pady=5,sticky=tk.NSEW)

        custom_trace.deiconify()
        custom_trace.grab_set()
        custom_trace.wait_window(custom_trace)
        try:
            return(sel_x)
        except:
            return None

    def ask_ytrace(data,title):
        global sel_traces
        sel_traces=[]
        y1_traces=[]
        y1_vars=[]
        choices = list(data.columns)

        def apply_trace():
            global sel_traces
            for var in y1_vars:
                sel_traces.append(var.get())
            custom_trace.destroy()

        def add_trace():
            global num_tr
            num_tr+=1
            custom_trace.grid_rowconfigure(num_tr, weight=1)
            y_ch =tk.Frame(custom_trace)
            y_ch.grid(row=num_tr,column=0,columnspan=4,sticky=tk.NSEW)
            y_ch.grid_columnconfigure(0,weight=1)
            y_ch.grid_rowconfigure(0,weight=1)
            y1_traces.append(y_ch)

            w_y = ttk.Combobox(y_ch, values=choices,state="readonly",justify='center')
            w_y.current(1)
            w_y.grid(row=0,columnspan=2,sticky=tk.NSEW)
            y1_vars.append(w_y)

            buts.grid(row=num_tr+1,column=0,sticky=tk.NSEW)


        def remove_trace():
            global num_tr
            if num_tr>0:
                num_tr-=1
                y1_traces[-1].grid_forget()
                y1_traces[-1].destroy()
                y1_traces.pop()
                y1_vars.pop()

        custom_trace=tk.Toplevel(choose_plot)
        custom_trace.grid_columnconfigure(0, weight=1)
        custom_trace.grid_rowconfigure(0, weight=1)
        custom_trace.resizable(width=False, height=False)
        custom_trace.withdraw()
        custom_trace.protocol("WM_DELETE_WINDOW")
        custom_trace.title(title)

        y_ch =tk.Frame(custom_trace)
        y_ch.grid(row=0,column=0,columnspan=4,sticky=tk.NSEW)
        y_ch.grid_columnconfigure(0,weight=1)
        y_ch.grid_rowconfigure(0,weight=1)
        y1_traces.append(y_ch)

        w_y = ttk.Combobox(y_ch, values=choices,state="readonly",justify='center')
        w_y.current(1)
        w_y.grid(row=0,sticky=tk.NSEW)
        y1_vars.append(w_y)

        buts =tk.Frame(custom_trace)
        buts.grid(row=1,column=0,sticky=tk.NSEW)
        buts.grid_columnconfigure(0,weight=1)
        custom_apply = tk.Button(buts,text="Apply",command=apply_trace)
        custom_apply.grid(row=1,column=0,columnspan=2,sticky=tk.NSEW)
        custom_add = tk.Button(buts,text="+",command=add_trace)
        custom_add.grid(row=1,column=2,sticky=tk.NSEW)
        custom_remove = tk.Button(buts,text="-",command=remove_trace)
        custom_remove.grid(row=1,column=3,sticky=tk.NSEW)

        custom_trace.deiconify()
        custom_trace.grab_set()
        custom_trace.wait_window(custom_trace)

        try:
            return(list(sel_traces))
        except:
            return None

    global time_xaxis
    time_xaxis=True
    if button_text=="P":

        if len(s['P'].columns)>1:
            ask_trace('P Setpoint',s['P'])
        else:
            strace=1
        try:
            print(strace)
            fig,axes,lines,leg= plot_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],en['P'].iloc[:,0])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif button_text=="Pexp":

        if len(s['P'].columns)>1:
            ask_trace('P Setpoint',s['P'])
        else:
            strace=1
        try:
            fig,axes,lines,leg= plot_Pexp(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],en['P'].iloc[:,0],m['Pexp'])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="Q":

        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        try:
            fig,axes,lines,leg= plot_Q(time,m['Q'].iloc[:,0],s['Q'].iloc[:,strace-1],en['Q'].iloc[:,0])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="AVR":
        fig,axes,lines,leg= plot_AVR(time,m['V'].iloc[:,0],s['AVR'].iloc[:,0],m['Q'].iloc[:,0],en['AVR'].iloc[:,0])

    elif  button_text=="QV":

        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        try:
            fig,axes,lines,leg= plot_QV(time,m['V'].iloc[:,0],s['QV'].iloc[:,0],m['Q'].iloc[:,0],s['Q'][:,strace-1],en['QV'].iloc[:,0])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="F":
        if len(s['P'].columns)>1:
            ask_trace('P Setpoint',s['P'])
        else:
            strace=1
        try:
            fig,axes,lines,leg= plot_F_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],m['F'].iloc[:,0],s['F'].iloc[:,0],en['F'].iloc[:,0])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="PF":
        fig,axes,lines,leg= plot_PF(time,m['PF'].iloc[:,0],s['PF'].iloc[:,0],en['PF'].iloc[:,0])

    elif  button_text=="All Measurements":
        fig,axes,lines,leg= plot_meas(time,m)

    elif  button_text=="Q Capability":
        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        try:
            fig,axes,lines,leg= plot_PQ(time,m['P'].iloc[:,0],m['Q'].iloc[:,0],s['Q'].iloc[:,strace-1],en['Q'].iloc[:,0])
        except TypeError:
            messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif button_text=="Custom Plot":
        xtrace = ask_xtrace(data,"X-axis trace")
        if xtrace != None:
            ytraces=ask_ytrace(data,"Y-axis traces")
            print(ytraces)
            if ytraces:
                y1_traces=[]
                for tr in ytraces:
                    y1_traces.append({"tr":data[tr],"ax2":False})
                y2= messagebox.askquestion('2nd Y-Axis','Would you like adding 2nd Y-axis?',parent=choose_plot)
                if y2=="yes":
                    ytraces=ask_ytrace(data,"Y2-axis traces")
                    y2_traces=[]
                    for tr in ytraces:
                        y2_traces.append({"tr":data[tr],"ax2":True})
                else:
                    y2_traces=[]
                fig,axes,lines,leg=custom_plot(data[xtrace],y1_traces+y2_traces)

                if not isinstance(data[xtrace][0],pd._libs.tslibs.timestamps.Timestamp):
                    time_xaxis=False

    try:
        line_deads_val=[]
        for l in lines:
            line_deads_val.append(0)
        axes[0].set_zorder(0.1)
        if len(axes)==2:
            axes[0].patch.set_visible(False)
            axes[1].patch.set_visible(True)
            axes[1].set_facecolor('whitesmoke')
        ylims_0=[]
        for ax in axes:
            ylims_0.append(ax.get_ylim())
        xlim_0=fig.axes[0].get_xlim()


        lined = dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        master = tk.Toplevel(choose_plot)
        master.title("PLOT")
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)


        def destroyer():
            global grid_color
            global dead_flag
            global line_deads
            grid_color=((11,11,11),'#b0b0b0')
            line_deads=[]
            dead_flag=0

            master.destroy()


        def reset():
            global time_xaxis
            fig.axes[0].set_xlim(xlim_0)
            if time_xaxis:
                fig.axes[0].xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
            else:
                fig.axes[0].xaxis.set_major_locator(MaxNLocator(nbins=20))
                fig.axes[0].xaxis.set_minor_locator(AutoMinorLocator())

            for tick in axes[0].get_xticklabels():
                tick.set_rotation(30)
                tick.set_fontsize(10)
                tick.set_fontweight('normal')

            for ind,ax in enumerate(axes):
                ax.set_ylim(ylims_0[ind])
                ax.yaxis.set_major_locator(MaxNLocator(nbins=20))
                ax.yaxis.set_minor_locator(AutoMinorLocator())
                for tick in ax.get_yticklabels():
                    tick.set_rotation(0)
                    tick.set_fontsize(10)
                    tick.set_fontweight('normal')
            fig.canvas.draw()

        master.protocol("WM_DELETE_WINDOW")

        canvas_frame=tk.Frame(master)
        canvas = FigureCanvasTkAgg(fig, canvas_frame)
        canvas_frame.grid(row=0,columnspan=2,sticky=tk.NSEW)
        canvas_frame.grid_rowconfigure(0,weight=1)
        canvas_frame.grid_columnconfigure(0,weight=1)

        frame = tk.Frame(master)
        frame.grid(row=1,columnspan=2,sticky=tk.NSEW)
        frame.grid_rowconfigure(0,weight=1)
        frame.grid_columnconfigure(0,weight=1)

        toolbar = NavigationToolbar(canvas, frame)
        toolbar.update()

        canvas.get_tk_widget().grid(row=0,sticky=tk.NSEW)

        buttons_frame=tk.Frame(master)
        buttons_frame.grid(row=2,columnspan=2,sticky=tk.NSEW)
        buttons_frame.grid_columnconfigure(0,weight=1)


        quitbutton=HoverButton(buttons_frame,text="Quit",activebackground='red')
        quitbutton.config(command=destroyer)
        quitbutton.grid(row=1,column=0)
        resetbutton=HoverButton(buttons_frame, text="Reset",activebackground='red',background = "white",borderwidth=2,relief="raised")
        resetbutton.config(command=reset)
        resetbutton.grid(row=0,columnspan=2,sticky=tk.NSEW)


        def interact_title():
            def title():
                weight= title_weight_val.get()
                style= title_style_val.get()
                family= title_family_val.get()
                try:
                    size = float(e_title_size.get())
                except:
                    size = 14
                title_font={'family': family,
                    'style' : style,
                    'color':  'black',
                    'weight': weight,
                    'size': size}
                title_x= axes[0].title.get_position()[0]
                title_y= axes[0].title.get_position()[1]
                axes[0].set_title(e_title_text.get(),fontdict=title_font,x=title_x,y=title_y)
                fig.canvas.draw_idle()
                change_title.destroy()
            try:
                if 'normal' == change_title.state():
                    change_title.lift()
            except:
                change_title = tk.Toplevel(master)
                change_title.resizable(width=False, height=False)
                change_title.title("Title")

                title_text = tk.Label(change_title, text="Text").grid(row=0)
                e_title_text = tk.Entry(change_title,bd=5,width=40)
                e_title_text.insert(0,axes[0].get_title())
                e_title_text.grid(row=0,column=1)

                title_size = tk.Label(change_title, text="FontSize").grid(row=1)

                var_title=tk.StringVar(change_title)
                var_title.set(str(axes[0].title.get_fontsize()))
                e_title_size = tk.Spinbox(change_title, from_=2, to=30,bd=5,width=5,textvariable=var_title,increment=0.5)
                e_title_size.grid(row=1,column=1,sticky=tk.W)

                global weights
                global families
                global styles

                title_weight = tk.Label(change_title, text="FontWeight").grid(row=2)
                title_weight_val = tk.StringVar(change_title)
                title_weight_val.set(axes[0].title.get_fontweight())
                e_title_weight = tk.OptionMenu(change_title, title_weight_val, *weights)
                e_title_weight.grid(row=2,column=1,sticky=tk.W)

                title_family = tk.Label(change_title, text="FontFamily").grid(row=3)
                title_family_val = tk.StringVar(change_title)
                title_family_val.set(axes[0].title.get_fontfamily()[0])
                e_title_family = tk.OptionMenu(change_title, title_family_val, *families)
                e_title_family.grid(row=3,column=1,sticky=tk.W)

                title_style = tk.Label(change_title, text="FontStyle").grid(row=4)
                title_style_val = tk.StringVar(change_title)
                title_style_val.set(axes[0].title.get_fontstyle())
                e_title_style = tk.OptionMenu(change_title, title_style_val, *styles)
                e_title_style.grid(row=4,column=1,sticky=tk.W)

                quit_title=tk.Button(change_title, text='Quit',command=change_title.destroy).grid(row=5, column=0, sticky=tk.W, pady=4)
                apply_title = tk.Button(change_title,text='Apply title', command=title).grid(row=5,column=1,sticky=tk.W, pady=4)

        def interact_y_label():
            def ylabel():
                for ind,e_y in enumerate(y_entries):
                    weight= y_weights[ind].get()
                    style= y_styles[ind].get()
                    family= y_families[ind].get()
                    try:
                        size = float(y_sizes[ind].get())
                    except:
                        size = 14
                    y_font={'family': family,
                        'style' : style,
                        'color':  'black',
                        'weight': weight,
                        'size': size}
                    axes[ind].set_ylabel(y_entries[ind].get(),fontdict=y_font)
                    fig.canvas.draw_idle()
                change_y.destroy()

            try:
                if 'normal' == change_y.state():
                    change_y.lift()
            except:
                change_y = tk.Toplevel(master)
                change_y.resizable(width=False, height=False)
                change_y.title("Y-labels")
                y_entries=[]
                y_sizes=[]
                y_weights=[]
                y_styles=[]
                y_families=[]

                for ind,ax in enumerate(axes):


                    y_title = tk.Label(change_y, text="Y"+str(ind+1)+"-label").grid(row=0,column=2*ind,columnspan=2)

                    y_text = tk.Label(change_y, text="Text").grid(row=1,column=2*ind)
                    e_y_text = tk.Entry(change_y,bd=5,width=25)
                    e_y_text.insert(0,ax.get_ylabel())
                    e_y_text.grid(row=1,column=2*ind+1,sticky=tk.W)
                    y_entries.append(e_y_text)

                    var_y=tk.StringVar(change_y)
                    var_y.set(str(ax.yaxis.label.get_fontsize()))
                    y_size = tk.Label(change_y, text="FontSize").grid(row=2,column=2*ind)
                    e_y_size = tk.Spinbox(change_y, from_=2, to=30,bd=5,width=5,textvariable=var_y,increment=0.5)
                    e_y_size.grid(row=2,column=2*ind+1,sticky=tk.W)
                    y_sizes.append(e_y_size)

                    global weights
                    global families
                    global styles

                    y_weight = tk.Label(change_y, text="FontWeight").grid(row=3,column=2*ind)
                    y_weight_val = tk.StringVar(change_y)
                    y_weight_val.set(ax.yaxis.label.get_fontweight())
                    e_y_weight = tk.OptionMenu(change_y, y_weight_val, *weights)
                    e_y_weight.grid(row=3,column=2*ind+1,sticky=tk.W)
                    y_weights.append(y_weight_val)

                    y_family = tk.Label(change_y, text="FontFamily").grid(row=4,column=2*ind)
                    y_family_val = tk.StringVar(change_y)
                    y_family_val.set(ax.yaxis.label.get_fontfamily()[0])
                    e_y_family = tk.OptionMenu(change_y, y_family_val, *families)
                    e_y_family.grid(row=4,column=2*ind+1,sticky=tk.W)
                    y_families.append(y_family_val)

                    y_style = tk.Label(change_y, text="FontStyle").grid(row=5,column=2*ind)
                    y_style_val = tk.StringVar(change_y)
                    y_style_val.set(ax.yaxis.label.get_fontstyle())
                    e_y_style = tk.OptionMenu(change_y, y_style_val, *styles)
                    e_y_style.grid(row=5,column=2*ind+1,sticky=tk.W)
                    y_styles.append(y_style_val)

                y_frame = tk.Frame(change_y)
                y_frame.grid(row=6,column=0,columnspan=2*len(axes),pady=10)

                quit_y=tk.Button(y_frame, text='Quit',command=change_y.destroy).grid(row=1, column=0,columnspan=2, pady=4,sticky=tk.NSEW)
                apply_y = tk.Button(y_frame,text='Apply', command=ylabel).grid(row=1, column=2,columnspan=2, pady=4,sticky=tk.NSEW)


        def interact_grid():

            def apply_grid():
                global grid_color

                for ind,ax in enumerate(axes):
                    ax.grid(False,which='both')
                    if grid_ons[ind].get()=='Show':
                        ax.grid(which=grid_whichs[ind].get(),axis=grid_axes[ind].get(),linestyle=grid_styles[ind].get(),linewidth=float(grid_widths[ind].get()),c=grid_color[1],alpha=float(grid_alpha_val.get()))
                fig.canvas.draw_idle()
                change_grid.destroy()

            def grid_color():
                global grid_color
                grid_color=colorchooser.askcolor(title="Pick Color")
                if  grid_color != (None,None):
                    grid_color_button.config(background=grid_color[1])
                    grid_color_button.config(activebackground=grid_color_button.cget('background'))

            try:
                if 'normal' == change_grid.state():
                    change_grid.lift()
            except:
                change_grid = tk.Toplevel(master)
                change_grid.resizable(width=False, height=False)
                change_grid.title("Grid")

                global which
                global which_axis
                global linestyles
                global grid_ax
                global grid_tick
                on_off = ['Show','Hide']
                grid_whichs=[]
                grid_axes=[]
                grid_styles=[]
                grid_widths=[]
                grid_ons=[]

                for ind,ax in enumerate(axes):

                    gl=ax.get_xgridlines()[0]
                    grid_title = tk.Label(change_grid, text="Y"+str(ind+1)+"-grid").grid(row=0,column=2*ind,columnspan=2)

                    grid_on = tk.Label(change_grid, text="Y"+str(ind+1)+"-grid").grid(row=1,column=2*ind)
                    grid_on_val=tk.StringVar(change_grid)
                    grid_on_val.set('Show')
                    e_grid_on = tk.OptionMenu(change_grid, grid_on_val, *on_off)
                    e_grid_on.grid(row=1,column=2*ind+1,sticky=tk.W)
                    grid_ons.append(grid_on_val)

                    grid_which = tk.Label(change_grid, text="Ticks").grid(row=2,column=2*ind)
                    grid_which_val = tk.StringVar(change_grid)
                    grid_which_val.set(which[0])
                    e_grid_which = tk.OptionMenu(change_grid, grid_which_val, *which)
                    e_grid_which.grid(row=2,column=2*ind+1,sticky=tk.W)
                    grid_whichs.append(grid_which_val)

                    grid_axis = tk.Label(change_grid, text="Axes").grid(row=3,column=2*ind)
                    grid_axis_val = tk.StringVar(change_grid)
                    grid_axis_val.set(which_axis[0])
                    e_grid_axis = tk.OptionMenu(change_grid, grid_axis_val, *which_axis)
                    e_grid_axis.grid(row=3,column=2*ind+1,sticky=tk.W)
                    grid_axes.append(grid_axis_val)

                    grid_style= tk.Label(change_grid,text="Line Style").grid(row=4,column=2*ind)
                    grid_style_val=tk.StringVar(change_grid)
                    grid_style_val.set(gl.get_linestyle())
                    e_grid_style = tk.OptionMenu(change_grid, grid_style_val, *linestyles)
                    e_grid_style.grid(row=4,column=2*ind+1,sticky=tk.W)
                    grid_styles.append(grid_style_val)

                    grid_width= tk.Label(change_grid,text="Line Width").grid(row=5,column=2*ind)
                    grid_width_val=tk.StringVar(change_grid)
                    grid_width_val.set(gl.get_linewidth())
                    e_grid_width = tk.Spinbox(change_grid,from_=1, to=10,bd=5,width=5,textvariable=grid_width_val,increment=0.5)
                    e_grid_width.grid(row=5,column=2*ind+1,sticky=tk.W)
                    grid_widths.append(grid_width_val)

                grid_color_frame = tk.Frame(change_grid)
                grid_color_frame.grid(row=6,column=0,columnspan=2*len(axes),pady=10)

                grid_color_label= tk.Label(grid_color_frame,text="Color").grid(row=0,column=0)
                grid_color_button= tk.Button(grid_color_frame,text="          ",background =gl.get_c())
                grid_color_button.config(command=grid_color)
                grid_color_button.config(activebackground=grid_color_button.cget('background'))
                grid_color_button.grid(row=0,column=1)

                grid_alpha= tk.Label(grid_color_frame,text="Opacity").grid(row=0,column=2)
                grid_alpha_val=tk.StringVar(change_grid)
                grid_alpha_val.set(1)
                e_grid_alpha = tk.Spinbox(grid_color_frame,from_=0, to=1,bd=5,width=5,textvariable=grid_alpha_val,increment=0.05)
                e_grid_alpha.grid(row=0,column=3)

                quit_grid=tk.Button(grid_color_frame, text='Quit',command=change_grid.destroy).grid(row=1, column=0,columnspan=2, pady=4,sticky=tk.NSEW)
                apply_grid = tk.Button(grid_color_frame,text='Apply',command=apply_grid).grid(row=1,column=2,columnspan=2, pady=4,sticky=tk.NSEW)

        def interact_leg_label():
            def leglabel():
                for ind,e_leg in enumerate(leg_entries):
                    leg.get_texts()[ind].set_text((e_leg.get()))
                    if e_leg.get()=="":
                        leg.get_lines()[ind].set_visible(False)
                    else:
                        leg.get_lines()[ind].set_visible(True)
                if leg_f_val.get()=='Hide':
                    leg.set_frame_on(False)
                else:
                    leg.set_frame_on(True)
                try:
                    leg.get_frame().set_linewidth(float(leg_l_entry.get()))
                except:
                    leg.get_frame().set_linewidth(1)

                fig.canvas.draw_idle()
                change_leg.destroy()

            def leg_bg_color():
                bg_color=colorchooser.askcolor(title="Pick Color")
                if  bg_color != (None,None):
                    leg.get_frame().set_facecolor(bg_color[1])
                    leg_bc_button.config(background=bg_color[1])
                    leg_bc_button.config(activebackground=leg_bc_button.cget('background'))

            def leg_eg_color():
                eg_color=colorchooser.askcolor(title="Pick Color")
                if  eg_color != (None,None):
                    leg.get_frame().set_edgecolor(eg_color[1])
                    leg_ec_button.config(background=eg_color[1])
                    leg_ec_button.config(activebackground=leg_ec_button.cget('background'))

            try:
                if 'normal' == change_leg.state():
                    change_leg.lift()
            except:
                change_leg = tk.Toplevel(master)
                change_leg.resizable(width=False, height=False)
                change_leg.title("Legend-labels")
                leg_entries=[]

                i=0
                for ind,l in enumerate(leg.get_lines()):
                    label_leg = tk.Label(change_leg, text="Insert Legend"+str(ind+1)+"-label").grid(row=ind)
                    e_leg = tk.Entry(change_leg,bd=5,width=40)
                    e_leg.insert(0,leg.get_texts()[ind].get_text())
                    e_leg.grid(row=ind,column=1)
                    leg_entries.append(e_leg)
                    i+=1

                lf = leg.get_frame()
                lf_bcolor = '#%02x%02x%02x' %  (int(lf.get_facecolor()[0]*255),int(lf.get_facecolor()[1]*255),int(lf.get_facecolor()[2]*255))
                le_bcolor = '#%02x%02x%02x' %  (int(lf.get_edgecolor()[0]*255),int(lf.get_edgecolor()[1]*255),int(lf.get_edgecolor()[2]*255))

                leg_f_vals = ['Show','Hide']
                leg_f = tk.Label(change_leg,text="Frame").grid(row=i)
                leg_f_val = tk.StringVar(change_leg)
                leg_f_val.set(leg_f_vals[0])

                leg_f_options = tk.OptionMenu(change_leg, leg_f_val, *leg_f_vals)
                leg_f_options.grid(row=i,column=1,sticky=tk.W)

                leg_l_label = tk.Label(change_leg,text="Frame Line Width").grid(row=i+1)

                var_leg=tk.StringVar(change_leg)
                var_leg.set(str(lf.get_linewidth()))
                leg_l_entry = tk.Spinbox(change_leg, from_=1, to=10,bd=5,width=5,textvariable=var_leg,increment=0.5)
                leg_l_entry.grid(row=i+1,column=1,sticky=tk.W)

                leg_bc_label= tk.Label(change_leg,text="Background Color").grid(row=i+2)
                leg_bc_button= tk.Button(change_leg,text="          ",background =lf_bcolor,command=leg_bg_color)
                leg_bc_button.config(activebackground=leg_bc_button.cget('background'))
                leg_bc_button.grid(row=i+2,column=1,sticky=tk.W)

                leg_ec_label= tk.Label(change_leg,text="Edge Color").grid(row=i+3)
                leg_ec_button= tk.Button(change_leg,text="          ",background =le_bcolor,command=leg_eg_color)
                leg_ec_button.config(activebackground=leg_ec_button.cget('background'))
                leg_ec_button.grid(row=i+3,column=1,sticky=tk.W)




                quit_leg=tk.Button(change_leg, text='Quit',command=change_leg.destroy).grid(row=i+4, column=0, sticky=tk.W, pady=4)
                apply_leg = tk.Button(change_leg,text='Apply', command=leglabel).grid(row=i+4,column=1,sticky=tk.W, pady=4)

        def interact_x_label():
            def xlabel():
                weight= x_weight_val.get()
                style= x_style_val.get()
                family= x_family_val.get()
                try:
                    size = float(e_x_size.get())
                except:
                    size = 14
                x_font={'family': family,
                    'style' : style,
                    'color':  'black',
                    'weight': weight,
                    'size': size}
                if len(axes)>2:
                    axes[-1].set_xlabel(e_x_text.get(),fontdict=x_font)
                else:
                    axes[0].set_xlabel(e_x_text.get(),fontdict=x_font)
                fig.canvas.draw_idle()
                change_x.destroy()
            try:
                if 'normal' == change_x.state():
                    change_x.lift()
            except:
                change_x = tk.Toplevel(master)
                change_x.resizable(width=False, height=False)
                change_x.title("X-label")

                x_title = tk.Label(change_x, text="X-label").grid(row=0,columnspan=2)
                x_text = tk.Label(change_x, text="Text").grid(row=1)
                e_x_text = tk.Entry(change_x,bd=5,width=25)
                if axes[0].get_xlabel() != "":
                    e_x_text.insert(0,axes[0].get_xlabel())
                else:
                    e_x_text.insert(0,axes[-1].get_xlabel())
                e_x_text.grid(row=1,column=1)

                var_x = tk.StringVar(change_x)
                var_x.set(str(axes[0].xaxis.label.get_fontsize()))
                x_size = tk.Label(change_x, text="FontSize").grid(row=2)
                e_x_size = tk.Spinbox(change_x, from_=2, to=30,bd=5,width=5,textvariable=var_x,increment=0.5)
                e_x_size.grid(row=2,column=1,sticky=tk.W)

                global weights
                global families
                global styles

                x_weight = tk.Label(change_x, text="FontWeight").grid(row=3)
                x_weight_val = tk.StringVar(change_x)
                x_weight_val.set(axes[0].xaxis.label.get_fontweight())
                e_x_weight = tk.OptionMenu(change_x, x_weight_val, *weights)
                e_x_weight.grid(row=3,column=1,sticky=tk.W)

                x_family = tk.Label(change_x, text="FontFamily").grid(row=4)
                x_family_val = tk.StringVar(change_x)
                x_family_val.set(axes[0].xaxis.label.get_fontfamily()[0])
                e_x_family = tk.OptionMenu(change_x, x_family_val, *families)
                e_x_family.grid(row=4,column=1,sticky=tk.W)

                x_style = tk.Label(change_x, text="FontStyle").grid(row=5)
                x_style_val = tk.StringVar(change_x)
                x_style_val.set(axes[0].xaxis.label.get_fontstyle())
                e_x_style = tk.OptionMenu(change_x, x_style_val, *styles)
                e_x_style.grid(row=5,column=1,sticky=tk.W)


                quit_x=tk.Button(change_x, text='Quit',command=change_x.destroy).grid(row=6, column=0, sticky=tk.W, pady=4)
                apply_x = tk.Button(change_x,text='Apply', command=xlabel).grid(row=6,column=1,sticky=tk.W, pady=4)

        def interact_traces():
            global line_deads_val

            def tr_color(trace):
                color=colorchooser.askcolor(title="Pick Color")
                if  color != (None,None):
                    lines[trace].set_color(color[1])
                    trace_color_buttons[trace].config(background=color[1])
                    trace_color_buttons[trace].config(activebackground=trace_color_buttons[trace].cget('background'))
                    leg.get_lines()[trace].set_c(color[1])

            def edit_traces():
                global dead_flag
                global line_deads
                global line_deads_val
                for ind,trace in enumerate(trace_entries):
                    try:
                        lines[ind].set_linewidth(trace_widths[ind].get())
                        leg.get_lines()[ind].set_linewidth(trace_widths[ind].get())
                        leg.get_lines()[ind].set_linestyle(trace_styles[ind].get())
                        lines[ind].set_alpha(float(trace_alphas[ind].get()))
                        lines[ind].set_linestyle(trace_styles[ind].get())
                        if dead_flag !=0:
                            line_deads[ind].remove()
                            line_deads.pop(ind)
                        lb=lines[ind].axes.fill_between(lines[ind].get_data()[0],lines[ind].get_data()[1]-float(trace_deads[ind].get()),lines[ind].get_data()[1]+float(trace_deads[ind].get()),alpha=0.5,facecolor=lines[ind].get_color())
                        line_deads_val[ind]=float(trace_deads[ind].get())
                        line_deads.insert(ind,lb)
                    except:
                        print(trace_styles[ind].get())
                        lines[ind].set_linewidth(2)
                        lines[ind].set_alpha(1)
                        lines[ind].set_linestyle('-')
                dead_flag+=1
                fig.canvas.draw_idle()
                change_traces.destroy()

            try:
                if 'normal' == change_traces.state():
                    change_traces.lift()
            except:
                change_traces=tk.Toplevel(master)
                change_traces.resizable(width=False,height=False)
                change_traces.title("Traces")

                trace_entries=[]
                trace_widths=[]
                trace_alphas=[]
                trace_styles=[]
                trace_color_buttons=[]
                trace_deads=[]

                for ind,line in enumerate(lines):

                    trace_title= tk.Label(change_traces,text=line.get_label()).grid(row=0,column=2*ind,columnspan=2)
                    trace_index=ind
                    trace_entries.append(trace_index)

                    if not isinstance (lines[ind].get_color(),str):
                        trace_color = '#%02x%02x%02x' %  (int(lines[ind].get_color()[0]*255),int(lines[ind].get_color()[1]*255),int(lines[ind].get_color()[2]*255))
                    else:
                        trace_color = lines[ind].get_color()


                    trace_width= tk.Label(change_traces,text="Width").grid(row=1,column=2*ind)
                    trace_width_val=tk.StringVar(change_traces)
                    trace_width_val.set(line.get_linewidth())
                    e_trace_width = tk.Spinbox(change_traces,from_=1, to=30,bd=5,width=5,textvariable=trace_width_val,increment=0.5)
                    e_trace_width.grid(row=1,column=2*ind+1,sticky=tk.W)
                    trace_widths.append(e_trace_width)

                    trace_alpha= tk.Label(change_traces,text="Opacity").grid(row=2,column=2*ind)
                    trace_alpha_val=tk.StringVar(change_traces)
                    trace_alpha_val.set(line.get_alpha())
                    e_trace_alpha = tk.Spinbox(change_traces,from_=0, to=1,bd=5,width=5,textvariable=trace_alpha_val,increment=0.05)
                    e_trace_alpha.grid(row=2,column=2*ind+1,sticky=tk.W)
                    trace_alphas.append(e_trace_alpha)

                    trace_style= tk.Label(change_traces,text="Style").grid(row=3,column=2*ind)
                    trace_style_val=tk.StringVar(change_traces)
                    trace_style_val.set(line.get_linestyle())
                    e_trace_style = tk.OptionMenu(change_traces, trace_style_val, *linestyles)
                    e_trace_style.grid(row=3,column=2*ind+1,sticky=tk.W)
                    trace_styles.append(trace_style_val)

                    trace_color_label= tk.Label(change_traces,text="Color").grid(row=4,column=2*ind)
                    trace_color_button= tk.Button(change_traces,text="          ",background =trace_color)
                    trace_color_button.config(activebackground=trace_color_button.cget('background'))
                    trace_color_button.config(command=lambda trace=trace_index: tr_color(trace))
                    trace_color_button.grid(row=4,column=2*ind+1,sticky=tk.W)
                    trace_color_buttons.append(trace_color_button)


                    trace_dead_label = tk.Label(change_traces,text='Deadband').grid(row=5,column=2*ind)
                    trace_dead_val = tk.StringVar(change_traces)
                    trace_dead_val.set(line_deads_val[ind])
                    e_trace_dead = tk.Spinbox(change_traces,from_=0, to=5000,bd=5,width=10,textvariable=trace_dead_val,increment=50)
                    e_trace_dead.grid(row=5,column=2*ind+1,sticky=tk.W)
                    trace_deads.append(trace_dead_val)

                but_frame = tk.Frame(change_traces)
                but_frame.grid(row=6,column=0,columnspan=2*len(lines),pady=10)

                quit_traces=tk.Button(but_frame, text='Quit',command=change_traces.destroy).grid(row=1, column=0,columnspan=2, pady=4,sticky=tk.NSEW)
                apply_traces = tk.Button(but_frame,text='Apply',command=edit_traces).grid(row=1,column=2,columnspan=2, pady=4,sticky=tk.NSEW)

        def interact_axes():

            def edit_axes():
                fig.canvas.draw_idle()
                change_axes.destroy()

            def quit_axes():
                ax.set_facecolor((0.9607843137254902, 0.9607843137254902, 0.9607843137254902, 1.0))
                fig.set_facecolor((1.0, 1.0, 1.0, 1.0))
                change_axes.destroy()


            def plot_bg_color():
                bg_color=colorchooser.askcolor(title="Pick Color")
                if  bg_color != (None,None):
                    for ax in axes:
                        ax.set_facecolor(bg_color[1])
                    axes_bg_color_button.config(background=bg_color[1])
                    axes_bg_color_button.config(activebackground=axes_bg_color_button.cget('background'))


            def plot_mg_color():
                mg_color=colorchooser.askcolor(title="Pick Color")
                if  mg_color != (None,None):
                    fig.set_facecolor(mg_color[1])
                    axes_mg_color_button.config(background=mg_color[1])
                    axes_mg_color_button.config(activebackground=axes_mg_color_button.cget('background'))

            try:
                if 'normal' == change_axes.state():
                    change_axes.lift()
            except:
                change_axes = tk.Toplevel(master)
                change_axes.resizable(width=False,height=False)
                change_axes.title("Axes")

                axes_bg_color='#%02x%02x%02x' %  (int(axes[0].get_facecolor()[0]*255),int(axes[0].get_facecolor()[1]*255),int(axes[0].get_facecolor()[2]*255))
                axes_mg_color='#%02x%02x%02x' %  (int(fig.get_facecolor()[0]*255),int(fig.get_facecolor()[1]*255),int(fig.get_facecolor()[2]*255))

                axes_bg_color_label = tk.Label(change_axes,text="Plot Background Color").grid(row=0)
                axes_bg_color_button = tk.Button(change_axes,text="          ",background=axes_bg_color,command=plot_bg_color)
                axes_bg_color_button.config(activebackground=axes_bg_color_button.cget('background'))
                axes_bg_color_button.grid(row=0,column=1)

                axes_mg_color_label = tk.Label(change_axes,text="Plot Margin Color").grid(row=1)
                axes_mg_color_button = tk.Button(change_axes,text="          ",background=axes_mg_color,command=plot_mg_color)
                axes_mg_color_button.config(activebackground=axes_mg_color_button.cget('background'))
                axes_mg_color_button.grid(row=1,column=1)

                quit_axes=tk.Button(change_axes, text='Quit',command=quit_axes).grid(row=3, column=0, sticky=tk.W, pady=4)
                apply_axes = tk.Button(change_axes,text='Apply', command=edit_axes).grid(row=3,column=1,sticky=tk.W, pady=4)

        def interact_y_limits():
            def ylimits():
                for ind,l_y in enumerate(ymin_lims):
                    axes[ind].set_ylim(float(l_y.get()),float(ymax_lims[ind].get()))
                    # ax.yaxis.set_minor_locator(AutoMinorLocator())
                fig.canvas.draw_idle()
                change_ylim.destroy()

            try:
                if 'normal' == change_ylim.state():
                    change_ylim.lift()
            except:
                change_ylim = tk.Toplevel(master)
                change_ylim.resizable(width=False,height=False)
                change_ylim.title("Y-limits")
                ymax_lims=[]
                ymin_lims=[]
                for ind,ax in enumerate(axes):

                    limit_y_min = tk.Label(change_ylim, text="Insert "+ax.get_ylabel()+"-min").grid(row=2*ind)
                    l_y_min = tk.Entry(change_ylim,bd=5,width=40)
                    l_y_min.insert(0,round(ax.get_ylim()[0],3))
                    l_y_min.grid(row=2*ind,column=1)
                    ymin_lims.append(l_y_min)

                    limit_y_max = tk.Label(change_ylim,text="Insert "+ax.get_ylabel()+"-max").grid(row=2*ind+1)
                    l_y_max = tk.Entry(change_ylim,bd=5,width=40)
                    l_y_max.insert(0,round(ax.get_ylim()[1],3))
                    l_y_max.grid(row=2*ind+1,column=1)
                    ymax_lims.append(l_y_max)

                quit_y=tk.Button(change_ylim, text='Quit',command=change_ylim.destroy).grid(row=2*len(axes)+3, column=0, sticky=tk.W, pady=4)
                apply_y = tk.Button(change_ylim,text='Apply', command=ylimits).grid(row=2*len(axes)+3,column=1,sticky=tk.W, pady=4)
        def interact_x_ticks():

                def apply_xticks():
                    int=e_x_tick.get()
                    axes[0].xaxis.set_major_locator(MultipleLocator(float(int)))

                    try:
                        rot=  e_x_tick_rot.get()
                        s = e_x_tick_size.get()
                        for tick in axes[0].get_xticklabels():
                            tick.set_rotation(float(rot))
                            tick.set_fontsize(float(s))
                            tick.set_fontweight(var_weight_xtick.get())
                        fig.canvas.draw()
                        change_xticks.destroy()
                    except RuntimeError:
                        messagebox.showwarning("Warning","Too many ticks-Zoom in",parent=change_xticks)
                        axes[0].xaxis.set_major_locator(MaxNLocator(nbins=20))
                        axes[0].xaxis.set_minor_locator(AutoMinorLocator())
                        for tick in axes[0].get_xticklabels():
                            tick.set_rotation(30)
                            tick.set_fontsize(10)
                            tick.set_fontweight('normal')
                        fig.canvas.draw_idle()
                        change_xticks.destroy()

                def reset_xticks():
                    axes[0].xaxis.set_major_locator(MaxNLocator(nbins=20))
                    axes[0].xaxis.set_minor_locator(AutoMinorLocator())
                    for tick in axes[0].get_xticklabels():
                        tick.set_rotation(30)
                        tick.set_fontsize(10)
                        tick.set_fontweight('normal')
                    fig.canvas.draw_idle()
                    change_xticks.destroy()

                try:
                    if 'normal' == change_xticks().state():
                        change_xticks.lift()
                except:
                    change_xticks=tk.Toplevel(master)
                    change_xticks.resizable(width=False,height=False)
                    change_xticks.title("X-ticks")

                    x_tick_val = tk.StringVar(change_xticks)
                    x_tick_val.set(axes[0].get_xticks()[1]-axes[0].get_xticks()[0])
                    x_tick = tk.Label(change_xticks, text="Put ticks every:").grid(row=0,column=0)
                    e_x_tick = tk.Spinbox(change_xticks,from_=10, to=20000,bd=5,width=10,textvariable=x_tick_val,increment=10)
                    e_x_tick.grid(row=0,column=1,sticky=tk.W)

                    x_tick_rot = tk.StringVar(change_xticks)
                    x_tick_rot.set(axes[0].get_xticklabels()[0].get_rotation())
                    x_tick = tk.Label(change_xticks, text="Rotation:").grid(row=1,column=0)
                    e_x_tick_rot = tk.Spinbox(change_xticks,from_=0, to=360,bd=5,width=10,textvariable=x_tick_rot,increment=10)
                    e_x_tick_rot.grid(row=1,column=1,sticky=tk.W)

                    x_tick_size = tk.StringVar(change_xticks)
                    x_tick_size.set(axes[0].get_xticklabels()[0].get_fontsize())
                    x_tick = tk.Label(change_xticks, text="FontSize:").grid(row=2,column=0)
                    e_x_tick_size = tk.Spinbox(change_xticks,from_=2, to=30,bd=5,width=10,textvariable=x_tick_size,increment=1)
                    e_x_tick_size.grid(row=2,column=1,sticky=tk.W)

                    x_tick_weight_label = tk.Label(change_xticks, text="FontWeight").grid(row=3)
                    var_weight_xtick = tk.StringVar(change_xticks)
                    var_weight_xtick.set(axes[0].get_xticklabels()[0].get_fontweight())
                    x_tick_weight = tk.OptionMenu(change_xticks, var_weight_xtick, *weights)
                    x_tick_weight.grid(row=3,column=1,sticky=tk.W)

                    apply_xtick = tk.Button(change_xticks, text='Apply',command=apply_xticks).grid(row=4,column=0,pady=5)
                    reset_xtick = tk.Button(change_xticks, text='Reset',command=reset_xticks).grid(row=4,column=1,pady=5)

        def interact_x_ticks_time():

            global weights
            def apply_xticks():

                try:
                    x_val = float(e_x_tick.get())
                except:
                    x_val = 10
                x_int = var_xtick.get()

                if x_int == 'sec':
                    loc = mdates.SecondLocator(interval = int(x_val))
                    loc.MAXTICKS=20000
                    fig.axes[0].xaxis.set_major_locator(loc)
                elif x_int == 'min':
                    loc = mdates.MinuteLocator(interval = int(x_val))
                    loc.MAXTICKS=20000
                    fig.axes[0].xaxis.set_major_locator(loc)
                elif x_int == 'h':
                    fig.axes[0].xaxis.set_major_locator(mdates.HourLocator(interval = int(x_val)))
                try:
                    rot = e_x_tick_rot.get()
                    s = e_x_tick_size.get()
                    for tick in axes[0].get_xticklabels():
                        tick.set_rotation(float(rot))
                        tick.set_fontsize(float(s))
                        tick.set_fontweight(var_weight_xtick.get())
                    fig.canvas.draw()
                    change_xticks.destroy()

                except RuntimeError:
                    messagebox.showwarning("Warning","Too many ticks-Zoom in",parent=change_xticks)
                    fig.axes[0].xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
                    for tick in axes[0].get_xticklabels():
                        tick.set_rotation(30)
                        tick.set_fontsize(10)
                        tick.set_fontweight('normal')
                    fig.canvas.draw_idle()
                    change_xticks.destroy()


            def reset_xticks():
                fig.axes[0].xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
                for tick in axes[0].get_xticklabels():
                    tick.set_rotation(30)
                    tick.set_fontsize(10)
                    tick.set_fontweight('normal')
                fig.canvas.draw_idle()
                change_xticks.destroy()

            try:
                if 'normal' == change_xticks().state():
                    change_xticks.lift()
            except:
                change_xticks=tk.Toplevel(master)
                change_xticks.resizable(width=False,height=False)
                change_xticks.title("X-ticks")
                xtick_label = tk.Label(change_xticks, text="Put X ticks every: ").grid(row=0,column=0)


                x_tick_val = tk.StringVar(change_xticks)
                x_tick_val.set(10)
                e_x_tick = tk.Spinbox(change_xticks,from_=1, to=60,bd=5,width=10,textvariable=x_tick_val,increment=1)
                e_x_tick.grid(row=0,column=1)

                xtick_int = ['sec','min','h']
                var_xtick = tk.StringVar(change_xticks)
                var_xtick.set(xtick_int[1])
                w_xtick = tk.OptionMenu(change_xticks, var_xtick, *xtick_int)
                w_xtick.grid(row=0,column=2)

                x_tick_rot = tk.StringVar(change_xticks)
                x_tick_rot.set(axes[0].get_xticklabels()[0].get_rotation())
                y_tick = tk.Label(change_xticks, text="Rotation:").grid(row=1,column=0)
                e_x_tick_rot = tk.Spinbox(change_xticks,from_=0, to=360,bd=5,width=10,textvariable=x_tick_rot,increment=10)
                e_x_tick_rot.grid(row=1,column=1,sticky=tk.W)

                x_tick_size = tk.StringVar(change_xticks)
                x_tick_size.set(axes[0].get_xticklabels()[0].get_fontsize())
                x_tick = tk.Label(change_xticks, text="FontSize:").grid(row=2,column=0)
                e_x_tick_size = tk.Spinbox(change_xticks,from_=2, to=30,bd=5,width=10,textvariable=x_tick_size,increment=1)
                e_x_tick_size.grid(row=2,column=1,sticky=tk.W)

                x_tick_weight_label = tk.Label(change_xticks, text="FontWeight").grid(row=3)
                var_weight_xtick = tk.StringVar(change_xticks)
                var_weight_xtick.set(axes[0].get_xticklabels()[0].get_fontweight())
                x_tick_weight = tk.OptionMenu(change_xticks, var_weight_xtick, *weights)
                x_tick_weight.grid(row=3,column=1,sticky=tk.W)

                apply_xtick = tk.Button(change_xticks, text='Apply',command=apply_xticks).grid(row=4,column=0,pady=5)
                reset_xtick = tk.Button(change_xticks, text='Reset',command=reset_xticks).grid(row=4,column=1,pady=5)

        def interact_y_ticks():

            global weights

            def apply_yticks():
                for ind,ax in enumerate(axes):
                    rot=y_rots[ind].get()
                    s = y_sizes[ind].get()
                    w = y_weights[ind].get()
                    for tick in ax.get_yticklabels():
                        tick.set_rotation(float(rot))
                        tick.set_fontsize(float(s))
                        tick.set_fontweight(w)
                    int=y_ticks[ind].get()
                    ax.yaxis.set_major_locator(MultipleLocator(float(int)))

                try:
                    fig.canvas.draw()
                    change_yticks.destroy()
                except RuntimeError:
                    messagebox.showwarning("Warning","Too many ticks-Zoom in",parent=change_yticks)
                    for ax in axes:
                        ax.yaxis.set_major_locator(MaxNLocator(nbins=20))
                        ax.yaxis.set_minor_locator(AutoMinorLocator())
                        for tick in ax.get_yticklabels():
                            tick.set_rotation(0)
                            tick.set_fontsize(10)
                            tick.set_fontweight('normal')
                    fig.canvas.draw_idle()
                    change_yticks.destroy()

            def reset_yticks():
                for ax in axes:
                    ax.yaxis.set_major_locator(MaxNLocator(nbins=20))
                    ax.yaxis.set_minor_locator(AutoMinorLocator())
                    for tick in ax.get_yticklabels():
                        tick.set_rotation(0)
                        tick.set_fontsize(10)
                        tick.set_fontweight('normal')
                fig.canvas.draw_idle()
                change_yticks.destroy()

            try:
                if 'normal' == change_yticks().state():
                    change_yticks.lift()
            except:
                change_yticks=tk.Toplevel(master)
                change_yticks.resizable(width=False,height=False)
                change_yticks.title("Y-ticks")
                y_tick_entries=[]
                y_ticks=[]
                y_rots=[]
                y_sizes=[]
                y_weights=[]
                for ind,ax in enumerate(axes):

                    y_title = tk.Label(change_yticks, text="Y"+str(ind+1)+"-label").grid(row=0,column=2*ind,columnspan=2)
                    y_tick_entries.append(y_title)

                    y_tick_val = tk.StringVar(change_yticks)
                    y_tick_val.set(ax.get_yticks()[1]-ax.get_yticks()[0])
                    y_tick = tk.Label(change_yticks, text="Put ticks every:").grid(row=1,column=2*ind)
                    e_y_tick = tk.Spinbox(change_yticks,from_=10, to=20000,bd=5,width=10,textvariable=y_tick_val,increment=10)
                    e_y_tick.grid(row=1,column=2*ind+1,sticky=tk.W)
                    y_ticks.append(e_y_tick)

                    y_tick_rot = tk.StringVar(change_yticks)
                    y_tick_rot.set(ax.get_yticklabels()[0].get_rotation())
                    y_tick = tk.Label(change_yticks, text="Rotation:").grid(row=2,column=2*ind)
                    e_y_tick_rot = tk.Spinbox(change_yticks,from_=0, to=360,bd=5,width=10,textvariable=y_tick_rot,increment=10)
                    e_y_tick_rot.grid(row=2,column=2*ind+1,sticky=tk.W)
                    y_rots.append(e_y_tick_rot)

                    y_tick_size = tk.StringVar(change_yticks)
                    y_tick_size.set(ax.get_yticklabels()[0].get_fontsize())
                    y_tick = tk.Label(change_yticks, text="FontSize:").grid(row=3,column=2*ind)
                    e_y_tick_size = tk.Spinbox(change_yticks,from_=2, to=30,bd=5,width=10,textvariable=y_tick_size,increment=1)
                    e_y_tick_size.grid(row=3,column=2*ind+1,sticky=tk.W)
                    y_sizes.append(e_y_tick_size)

                    y_tick_weight_label = tk.Label(change_yticks, text="FontWeight").grid(row=4,column=2*ind)
                    var_weight_ytick = tk.StringVar(change_yticks)
                    var_weight_ytick.set(ax.get_yticklabels()[0].get_fontweight())
                    y_tick_weight = tk.OptionMenu(change_yticks, var_weight_ytick, *weights)
                    y_tick_weight.grid(row=4,column=2*ind+1,sticky=tk.W)
                    y_weights.append(var_weight_ytick)

                ytick_frame = tk.Frame(change_yticks)
                ytick_frame.grid(row=5,column=0,columnspan=2*len(axes),pady=10)
                apply_ytick = tk.Button(ytick_frame, text='Apply',command=apply_yticks).grid(row=0,column=0,pady=5)
                reset_ytick = tk.Button(ytick_frame, text='Reset',command=reset_yticks).grid(row=0,column=1,pady=5)

        global texts
        global vlines
        global hlines

        drs=[]
        texts=[]
        def add_text():
            props = dict(boxstyle='round', facecolor='#F5DEB3', alpha=1)
            y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
            x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/10
            ask_text = simpledialog.askstring("Add TextBox","Insert text",parent=master)
            text = fig.axes[0].text(x,y,ask_text,rotation=0,c='#000000',fontdict={'size':12,'weight':'bold'},bbox=props,picker=5)
            texts.append(text)
            fig.canvas.draw_idle()
            dr = move_obj(text,fig,None,master)
            dr.connect_obj()
            drs.append(dr)

        dvs=[]
        vlines=[]
        def add_vertical():
            x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/2
            if axes[0].get_facecolor()<(0.5,0.5,0.5,1):
                c='#FFFFFF'
            else:
                c='#000000'
            v_line=fig.axes[0].axvline(x=x,linewidth=2,ls="--",c=c,alpha=1,picker=5)
            vlines.append(v_line)
            fig.canvas.draw_idle()
            dv = move_obj(v_line,fig,"Vertical",master)
            dv.connect_obj()
            dvs.append(dv)

        dhs=[]
        hlines=[]
        def add_horizontal():
            y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
            if axes[0].get_facecolor()<(0.5,0.5,0.5,1):
                c='#FFFFFF'
            else:
                c='#000000'
            h_line=fig.axes[0].axhline(y=y,linewidth=2,ls="--",c=c,alpha=1,picker=5)
            hlines.append(h_line)
            fig.canvas.draw_idle()
            dh = move_obj(h_line,fig,"Horizontal",master)
            dh.connect_obj()
            dhs.append(dh)

        das=[]
        def add_arrow():
            def apply_arrow():
                choise = variable.get()
                x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/2
                y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
                xstart = fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/10
                if choise == "No Arrow":
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='-',color="#000000",ls='-',alpha=1),picker=5)
                    fig.canvas.draw_idle()
                    da = move_obj(arrow_line,fig,"Arrow",master)
                    da.connect_obj()
                    das.append(da)
                elif choise == "Single Arrow":
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='->',color="#000000",ls='-',alpha=1),picker=5)
                    fig.canvas.draw_idle()
                    da = move_obj(arrow_line,fig,"Arrow",master)
                    da.connect_obj()
                    das.append(da)

                elif choise == "Double Arrow":
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='<->',color="#000000",ls='-',alpha=1),picker=5)
                    fig.canvas.draw_idle()
                    da = move_obj(arrow_line,fig,"Arrow",master)
                    da.connect_obj()
                    das.append(da)
                arrow_choice.destroy()

            arrow_choice=tk.Toplevel(master)
            arrow_choice.resizable(width=False, height=False)
            arrow_choice.geometry("220x100")
            arrow_choice.grid_columnconfigure(0, weight=1)
            arrow_choice.grid_rowconfigure(0, weight=1)
            ch =tk.Frame(arrow_choice)
            ch.grid(row=0,column=0,sticky=tk.NSEW)
            ch.grid_columnconfigure(0,weight=1)
            choices = ['No Arrow', 'Single Arrow', 'Double Arrow']
            variable = tk.StringVar(ch)
            variable.set('No Arrow')
            w = tk.OptionMenu(ch, variable, *choices)
            w.grid(row=0,columnspan=2,sticky=tk.NSEW)
            buts =tk.Frame(arrow_choice)
            buts.grid(row=1,column=0,sticky=tk.NSEW)
            buts.grid_columnconfigure(0,weight=1)
            arrow_apply = tk.Button(buts,text="Apply",command=apply_arrow)
            arrow_apply.grid(row=1,column=1,pady=5,sticky=tk.NSEW)
            arrow_quit  = tk.Button(buts,text="Quit",command=arrow_choice.destroy)
            arrow_quit.grid(row=1,column=0,pady=5,sticky=tk.NSEW)

        menubar=tk.Menu(master)

        labels=tk.Menu(menubar,tearoff=0)
        labels.add_command(label="Title",command = interact_title)
        labels.add_command(label="Traces",command = interact_traces)
        labels.add_command(label="Y labels",command = interact_y_label)
        labels.add_command(label="X label",command = interact_x_label)
        labels.add_command(label="Legend",command = interact_leg_label)
        labels.add_command(label="Figure",command = interact_axes)
        labels.add_command(label="Grid",command = interact_grid)
        menubar.add_cascade(label="Style",menu=labels)

        limits=tk.Menu(menubar,tearoff=0)
        limits.add_command(label="Change Y limits",command = interact_y_limits)
        menubar.add_cascade(label="Limits",menu=limits)

        ticks = tk.Menu(menubar,tearoff=0)
        ticks.add_command(label="Change Y ticks",command = interact_y_ticks)
        if time_xaxis:
            ticks.add_command(label="Change X ticks",command = interact_x_ticks_time)
        else:
            ticks.add_command(label="Change X ticks",command = interact_x_ticks)
        menubar.add_cascade(label="Ticks",menu=ticks)

        annotates=tk.Menu(menubar,tearoff=0)
        annotates.add_command(label="Text",command=add_text)
        annotates.add_command(label="Vertical Line",command=add_vertical)
        annotates.add_command(label="Horizontal Line",command=add_horizontal)
        annotates.add_command(label="Arrow Line",command=add_arrow)
        menubar.add_cascade(label="Annotate",menu=annotates)


        annots = []
        infos=[]
        for ax in axes:
            annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",bbox=dict(boxstyle="round", fc="w"))
            annot.set_visible(False)
            annots.append(annot)
            info=ax.annotate('Double Click to edit',
            xy=(0.74,0.9),
            xycoords=('axes fraction'),
            size=12,bbox=dict(boxstyle="round", fc="w",alpha=0.5))
            infos.append(info)
            info.set_visible(False)

        annot_dic = dict(zip(axes, annots))
        info_dic = dict(zip(axes, infos))

        def update_annot(l,annot,ind):
            x,y = l.get_data()
            xc = x[ind["ind"][0]]
            yc = y[ind["ind"][0]]
            annot.xy = (xc, yc)
            try:
                text = "({},{})".format(str(xc).split("T")[1].split(".")[0],yc)
                annot.set_text(text)
                annot.get_bbox_patch().set_facecolor(l.get_color())
            except:pass

        def hover(event):
            if event.inaxes in axes:
                for ax in axes:
                    for line in ax.lines:
                        cont, ind = line.contains(event)
                        annot = annot_dic[ax]
                        info = info_dic[ax]
                        if cont:
                            if (line in hlines)|(line in vlines):
                                info.set_visible(True)
                            else:
                                update_annot(line, annot, ind)
                                annot.set_visible(True)
                                fig.canvas.draw_idle()
                                break
                        else:
                            if annot.get_visible():
                                annot.set_visible(False)
                                fig.canvas.draw_idle()
                            if info.get_visible():
                                info.set_visible(False)
                                fig.canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", hover)

        # we will set up a dict mapping legend line to orig line, and enable
        # picking on the legend line

        def onpick(event):
            global oldx
            global deadband

            # on the pick event, find the orig line corresponding to the
            # legend proxy line, and toggle the visibility
            if event.artist in lined.keys():
                legline = event.artist
                origline = lined[legline]
                vis = not origline.get_visible()
                origline.set_visible(vis)
                try:
                    if tuple(lines[-1].get_facecolor()[0][0:3]) == origline.get_color():
                        lines[-1].set_visible(vis)
                except:
                    pass
                # Change the alpha on the line in the legend so we can see what lines
                # have been toggled
                if vis:
                    origline.set_pickradius(5)
                    legline.set_alpha(1.0)
                else:
                    origline.set_pickradius(0)
                    legline.set_alpha(0.2)
                fig.canvas.draw_idle()

        canvas.mpl_connect('pick_event', onpick)
        master.config(menu=menubar)
    except:pass

i=0
buttons=[]
buttons_frame=tk.Frame(choose_plot,borderwidth=2,relief="groove")
buttons_frame.grid(row=0,column=0,sticky=tk.NSEW)
buttons_frame.grid_columnconfigure(0,weight=1)
buttons_frame.grid_columnconfigure(1,weight=1)
buttons_frame.config(background='#000000')

photos=[]
for k,v, in plots.items():
    if v == "P":
        f = io.BytesIO(base64.b64decode(Pim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "Q":
        f = io.BytesIO(base64.b64decode(Qim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "AVR":
        f = io.BytesIO(base64.b64decode(AVRim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "F":
        f = io.BytesIO(base64.b64decode(Fim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "PF":
        f = io.BytesIO(base64.b64decode(PFim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "Q Capability":
        f = io.BytesIO(base64.b64decode(QCAPim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    elif v == "All Measurements":
        f = io.BytesIO(base64.b64decode(ALLMEASim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)
    else:
        f = io.BytesIO(base64.b64decode(CUSTOMim))
        image = Image.open(f)
        photo = ImageTk.PhotoImage(image,master=choose_plot)
        photos.append(photo)

    buttons_frame.grid_rowconfigure(int(np.floor(i/2)),weight=1)
    b=tk.Button(buttons_frame,text=v,image= photos[i],relief='flat',bd=0)
    b.config(command= lambda btn=b: plot_choise(btn))
    b.grid(row=int(np.floor(i/2)),column=i%2,padx=10,pady=10,sticky=tk.NSEW)
    i=i+1
if (i%2)==1:
    b.grid(row=int(np.floor(i/2)),column=0,columnspan=2,padx=10,pady=10,sticky=tk.NS)
buttons_frame.grid_rowconfigure(int(np.floor(i/2))+1,weight=1)
quit_button=tk.Button(buttons_frame,text='Quit',relief='flat',bd=2,command=destroyer)
quit_button.grid(row=int(np.floor(i/2))+1,columnspan=2,pady=10,sticky=tk.NSEW)

choose_plot.mainloop()
