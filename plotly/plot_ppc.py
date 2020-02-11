# %matplotlib notebook
from plot_maplot_v1 import *
import tkinter as tk
from tkinter import colorchooser,filedialog,simpledialog,messagebox,font
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
        # print(self.figure.axes[0].texts)
        'on button pick we will see if the mouse is over us and store some data'
        if isinstance(event.artist, Text):
            if isinstance(self.obj,Text):

                transf = self.figure.axes[0].transData.inverted()
                bb = self.obj.get_window_extent(renderer = self.figure.canvas.renderer)
                bb_datacoords = bb.transformed(transf)

                x0 = event.mouseevent.xdata
                y0 = event.mouseevent.ydata
                # print(mdates.num2date(bb_datacoords.xmax))
                # print(mdates.num2date(self.obj.xy[0]))
                if self.align=="Arrow":
                    print(mdates.num2date(bb_datacoords.xmin))
                    print(mdates.num2date(bb_datacoords.xmax))
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
                print(xlim_cur)
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
                    delete= tk.messagebox.askquestion('Delete TextBox','Are you sure you want to delete the texbox?',icon = 'warning',parent=self.parent)
                    if delete =="yes":
                        self.obj.remove()
                        self.figure.canvas.draw()
                elif self.obj in self.figure.axes[0].lines:
                    delete= tk.messagebox.askquestion('Delete Line','Are you sure you want to delete the line?',icon = 'warning',parent=self.parent)
                    if delete =="yes":
                        self.obj.remove()
                        self.figure.canvas.draw()


    def disconnect_obj(self):
        'disconnect all the stored connection ids'
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)

csv=''
while not csv:
    input_csv = tk.Tk()
    input_csv.withdraw()
    csv = filedialog.askopenfilename(initialdir = "/home",title = "Select csv file",filetypes = (("csv files","*.csv"),))
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
choose_plot.grid_columnconfigure(0, weight=1)
choose_plot.grid_rowconfigure(0, weight=1)


def plot_choise(button):
    global strace

    def ask_deadband(title):
        global deadband

        def apply_db(event=None):
            global deadband
            try:
                deadband=float(e_db.get())
            except:
                deadband=""
                messagebox.showwarning("Warning","Invalid Input",parent=input_db)
            input_db.destroy()

        def func(event):
            global deadband
            try:
                deadband=float(e_db.get())
            except:
                deadband=""
                messagebox.showwarning("Warning","Invalid Input",parent=input_db)
            input_db.destroy()
        # deadband=""
        input_db=tk.Toplevel(choose_plot)
        input_db.geometry("+{}+{}".format(choose_plot.winfo_x(),choose_plot.winfo_y()))
        input_db.withdraw()
        input_db.protocol("WM_DELETE_WINDOW")
        input_db.title(title)
        tk.Label(input_db,text='Enter Deadband').grid(row=0)
        e_db=tk.Entry(input_db)
        e_db.focus()
        e_db.grid(row=0,column=1)
        apply_db=tk.Button(input_db,text="Apply",command=apply_db)
        apply_db.grid(row=2,column=0,columnspan=2,pady=4)
        input_db.bind('<Return>',func)
        input_db.deiconify()
        input_db.grab_set()
        input_db.wait_window(input_db)


    def ask_trace(title,sets):
        global strace
        def destroyer():
            input_trace.destroy()

        def get_strace():
            global strace
            strace=vs.get()

        strace=""
        input_trace=tk.Toplevel(choose_plot)
        input_trace.geometry("+{}+{}".format(choose_plot.winfo_x(),choose_plot.winfo_y()))
        input_trace.resizable(width=False, height=False)
        input_trace.withdraw()
        input_trace.protocol("WM_DELETE_WINDOW")
        input_trace.title(title)

        j=0
        vs=tk.IntVar()
        for s in sets.columns:
            sb=tk.Radiobutton(input_trace,text=s,variable=vs,value=j+1)
            sb.grid(row=j+1,column=0,columnspan=2)
            sb.config(command= get_strace)
            j=j+1

        tk.Label(input_trace,text="Please select trace for "+title).grid(row=0,column=0,columnspan=2)
        quit_trace = tk.Button(input_trace,text='Apply',command=destroyer)
        quit_trace.grid(row=j+1,columnspan=2)
        input_trace.deiconify()
        input_trace.grab_set()
        input_trace.wait_window(input_trace)

    button_text = button.cget("text")

    def ask_xtrace(data,title):
        global sel_x
        def apply_trace():
            global sel_x
            sel_x = var_x.get()
            custom_trace.destroy()
        def disable_event():
            pass
        custom_trace=tk.Toplevel(choose_plot)
        custom_trace.resizable(width=False, height=False)
        custom_trace.geometry("220x100")
        custom_trace.grid_columnconfigure(0, weight=1)
        custom_trace.grid_rowconfigure(0, weight=1)
        custom_trace.withdraw()
        custom_trace.protocol("WM_DELETE_WINDOW",disable_event)
        custom_trace.title(title)
        # custom_trace.overrideredirect(True)

        choices = list(data.columns)

        x_ch =tk.Frame(custom_trace)
        x_ch.grid(row=0,column=0,sticky=tk.NSEW)
        x_ch.grid_columnconfigure(0,weight=1)

        var_x = tk.StringVar(x_ch)
        var_x.set('TIME')
        w_x = tk.OptionMenu(x_ch, var_x, *choices)
        w_x.grid(row=0,columnspan=2,sticky=tk.NSEW)

        buts =tk.Frame(custom_trace)
        buts.grid(row=1,column=0,sticky=tk.NSEW)
        buts.grid_columnconfigure(0,weight=1)
        custom_apply = tk.Button(buts,text="Apply",command=apply_trace)
        custom_apply.grid(row=1,column=0,columnspan=2,pady=5,sticky=tk.NSEW)
        # custom_quit  = tk.Button(buts,text="Quit",command=custom_trace.destroy)
        # custom_quit.grid(row=1,column=0,pady=5,sticky=tk.NSEW)

        custom_trace.deiconify()
        custom_trace.grab_set()
        custom_trace.wait_window(custom_trace)
        return(sel_x)

    def ask_ytrace(data,title):
        global sel_traces
        sel_traces=[]
        y1_traces=[]
        y1_vars=[]
        choices = list(data.columns)
        def disable_event():
            pass

        def apply_trace():
            global sel_traces
            for var in y1_vars:
                sel_traces.append(var.get())
            custom_trace.destroy()

        def add_trace():
            global num_tr
            num_tr+=1
            y_ch =tk.Frame(custom_trace)
            y_ch.grid(row=num_tr,column=0,sticky=tk.NSEW)
            y_ch.grid_columnconfigure(0,weight=1)
            var_y = tk.StringVar(y_ch)
            var_y.set(list(data.columns)[1])
            y1_vars.append(var_y)
            w_y = tk.OptionMenu(y_ch, var_y, *choices)
            w_y.grid(row=num_tr,columnspan=2,sticky=tk.NSEW)
            buts.grid(row=num_tr+1,column=0,sticky=tk.NSEW)
            y1_traces.append(y_ch)

        def remove_trace():
            global num_tr
            if num_tr>0:
                num_tr-=1
                y1_traces[-1].grid_forget()
                y1_traces[-1].destroy()
                y1_traces.pop()
                y1_vars.pop()

        custom_trace=tk.Toplevel(choose_plot)
        custom_trace.resizable(width=False, height=False)
        custom_trace.grid_columnconfigure(0, weight=1)
        custom_trace.grid_rowconfigure(0, weight=1)
        custom_trace.withdraw()
        custom_trace.protocol("WM_DELETE_WINDOW",disable_event)
        custom_trace.title(title)

        y_ch =tk.Frame(custom_trace)
        y_ch.grid(row=0,column=0,sticky=tk.NSEW)
        y_ch.grid_columnconfigure(0,weight=1)
        y1_traces.append(y_ch)
        var_y = tk.StringVar(y_ch)
        var_y.set(list(data.columns)[1])
        y1_vars.append(var_y)
        w_y = tk.OptionMenu(y_ch, var_y, *choices)
        w_y.grid(row=0,columnspan=2,sticky=tk.NSEW)

        buts =tk.Frame(custom_trace)
        buts.grid(row=1,column=0,sticky=tk.NSEW)
        buts.grid_columnconfigure(0,weight=1)
        custom_apply = tk.Button(buts,text="Apply",command=apply_trace)
        custom_apply.grid(row=1,column=0,columnspan=2,sticky=tk.NSEW)
        # custom_quit  = tk.Button(buts,text="Quit",command=custom_trace.destroy)
        # custom_quit.grid(row=1,column=0,sticky=tk.NSEW)
        custom_add = tk.Button(buts,text="+",command=add_trace)
        custom_add.grid(row=1,column=2,sticky=tk.NSEW)
        custom_remove = tk.Button(buts,text="-",command=remove_trace)
        custom_remove.grid(row=1,column=3,sticky=tk.NSEW)

        custom_trace.deiconify()
        custom_trace.grab_set()
        custom_trace.wait_window(custom_trace)

        return(list(sel_traces))

    if button_text=="P":

        ask_deadband('P Deadband in kW')
        pdb=deadband
        if type(deadband)==float:
            if len(s['P'].columns)>1:
                ask_trace('P Setpoint',s['P'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],en['P'].iloc[:,0],pdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif button_text=="Pexp":

        ask_deadband('P Deadband in kW')
        pdb=deadband
        if type(deadband)==float:
            if len(s['P'].columns)>1:
                ask_trace('P Setpoint',s['P'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_Pexp(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],en['P'].iloc[:,0],m['Pexp'],pdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="Q":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if type(deadband)==float:
            if len(s['Q'].columns)>1:
                ask_trace('Q Setpoint',s['Q'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_Q(time,m['Q'].iloc[:,0],s['Q'].iloc[:,strace-1],en['Q'].iloc[:,0],qdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="AVR":
        ask_deadband('Voltage Deadband in V')
        avrdb=deadband
        if type(deadband)==float:
            fig,axes,lines,leg= plot_AVR(time,m['V'].iloc[:,0],s['AVR'].iloc[:,0],m['Q'].iloc[:,0],en['AVR'].iloc[:,0],avrdb)

    elif  button_text=="QV":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if type(deadband)==float:
            if len(s['Q'].columns)>1:
                ask_trace('Q Setpoint',s['Q'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_QV(time,m['V'].iloc[:,0],s['QV'].iloc[:,0],m['Q'].iloc[:,0],s['Q'][:,strace-1],en['QV'].iloc[:,0],qdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="F":
        ask_deadband('P Deadband in kW')
        pdb=deadband
        if type(deadband)==float:
            if len(s['P'].columns)>1:
                ask_trace('P Setpoint',s['P'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_F_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],m['F'].iloc[:,0],s['F'].iloc[:,0],en['F'].iloc[:,0],pdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)

    elif  button_text=="PF":
        ask_deadband('PF Deadband')
        pfdb=deadband
        if type(deadband)==float:
            fig,axes,lines,leg= plot_PF(time,m['PF'].iloc[:,0],s['PF'].iloc[:,0],en['PF'].iloc[:,0],pfdb)

    elif  button_text=="All Measurements":
        fig,axes,lines,leg= plot_meas(time,m)

    elif  button_text=="Q Capability":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if type(deadband)==float:
            if len(s['Q'].columns)>1:
                ask_trace('Q Setpoint',s['Q'])
            else:
                strace=1
            try:
                fig,axes,lines,leg= plot_PQ(time,m['P'].iloc[:,0],m['Q'].iloc[:,0],s['Q'].iloc[:,strace-1],en['Q'].iloc[:,0],qdb)
            except TypeError:
                messagebox.showwarning("Warning","Select a trace",parent=choose_plot)
    elif button_text=="Custom Plot":
        xtrace = ask_xtrace(data,"Select X-axis trace")

        ytraces=ask_ytrace(data,"Select Y-axis traces")
        y1_traces=[]
        for tr in ytraces:
            y1_traces.append({"tr":data[tr],"ax2":False})
        y2= messagebox.askquestion('2nd Y-Axis','Would you like adding 2nd Y-axis?',parent=choose_plot)
        if y2=="yes":
            ytraces=ask_ytrace(data,"Select Y2-axis traces")
            y2_traces=[]
            for tr in ytraces:
                y2_traces.append({"tr":data[tr],"ax2":True})
        else:
            y2_traces=[]
        fig,axes,lines,leg=custom_plot(data[xtrace],y1_traces+y2_traces)


    axes[0].set_zorder(0.1)
    axes[0].patch.set_visible(False)
    ylim_0=fig.axes[0].get_ylim()
    xlim_0=fig.axes[0].get_ylim()

    try:
        lined = dict()
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        master = tk.Toplevel(choose_plot)
        master.title("PLOT")

        def destroyer():
            master.destroy()
        def undo():
            try:
                VLs[-1].remove()
                fig.canvas.draw()
                VLs.pop()
            except:
                pass
        master.protocol("WM_DELETE_WINDOW")

        frame = tk.Frame(master)

        canvas = FigureCanvasTkAgg(fig, master)
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()

        canvas.get_tk_widget().grid(row=1)
        frame.grid(row=2,sticky=tk.W)

        buttons_frame=tk.Frame(master)
        buttons_frame.grid(row=3)
        quitbutton = tk.Button(buttons_frame, text="Quit", command=destroyer)
        quitbutton.grid(row=0,column=0)
        undobutton=tk.Button(buttons_frame, text="Undo",command=undo)
        undobutton.grid(row=0,column=1)

        def interact_title():
            def title():
                if e_title.get()!='':
                    title_x= axes[0].title.get_position()[0]
                    title_y= axes[0].title.get_position()[1]
                    axes[0].set_title(e_title.get(),fontdict=font,x=title_x,y=title_y)
                    fig.canvas.draw()
                    change_title.destroy()
            try:
                if 'normal' == change_title.state():
                    change_title.lift()
            except:
                change_title = tk.Toplevel(master)
                change_title.resizable(width=False, height=False)
                change_title.title("Title")
                label_title = tk.Label(change_title, text="Insert Title").grid(row=0)
                e_title = tk.Entry(change_title,bd=5,width=40)
                e_title.insert(0,axes[0].get_title())
                e_title.grid(row=0,column=1)
                quit_title=tk.Button(change_title, text='Quit',command=change_title.destroy).grid(row=3, column=0, sticky=tk.W, pady=4)
                apply_title = tk.Button(change_title,text='Apply title', command=title).grid(row=3,column=1,sticky=tk.W, pady=4)

        def interact_y_label():
            def ylabel():
                for ind,e_y in enumerate(y_entries):
                    axes[ind].set_ylabel(e_y.get())
                    fig.canvas.draw()
                change_y.destroy()

            try:
                if 'normal' == change_y.state():
                    change_y.lift()
            except:
                change_y = tk.Toplevel(master)
                change_y.resizable(width=False, height=False)
                change_y.title("Y-labels")
                y_entries=[]
                for ind,ax in enumerate(axes):
                    label_y = tk.Label(change_y, text="Insert Y"+str(ind+1)+"-label").grid(row=ind)
                    e_y = tk.Entry(change_y,bd=5,width=40)
                    e_y.insert(0,ax.get_ylabel())
                    e_y.grid(row=ind,column=1)
                    y_entries.append(e_y)
                quit_y=tk.Button(change_y, text='Quit',command=change_y.destroy).grid(row=len(axes)+3, column=0, sticky=tk.W, pady=4)
                apply_y = tk.Button(change_y,text='Apply', command=ylabel).grid(row=len(axes)+3,column=1,sticky=tk.W, pady=4)

        def interact_leg_label():
            def leglabel():
                for ind,e_leg in enumerate(leg_entries):
                    leg.get_texts()[ind].set_text((e_leg.get()))
                fig.canvas.draw()
                change_leg.destroy()

            try:
                if 'normal' == change_leg.state():
                    change_leg.lift()
            except:
                change_leg = tk.Toplevel(master)
                change_leg.resizable(width=False, height=False)
                change_leg.title("Legend-labels")
                leg_entries=[]
                for ind,l in enumerate(leg.get_lines()):
                    label_leg = tk.Label(change_leg, text="Insert Legend"+str(ind+1)+"-label").grid(row=ind)
                    e_leg = tk.Entry(change_leg,bd=5,width=40)
                    e_leg.insert(0,leg.get_texts()[ind].get_text())
                    e_leg.grid(row=ind,column=1)
                    leg_entries.append(e_leg)
                quit_leg=tk.Button(change_leg, text='Quit',command=change_leg.destroy).grid(row=len(leg.get_lines())+3, column=0, sticky=tk.W, pady=4)
                apply_leg = tk.Button(change_leg,text='Apply', command=leglabel).grid(row=len(leg.get_lines())+3,column=1,sticky=tk.W, pady=4)

        def interact_x_label():
            def xlabel():
                if e_x.get()!='':
                    axes[0].set_xlabel(e_x.get())
                    fig.canvas.draw()
                    change_x.destroy()
            try:
                if 'normal' == change_x.state():
                    change_x.lift()
            except:
                change_x = tk.Toplevel(master)
                change_x.resizable(width=False, height=False)
                change_x.title("X-label")
                label_x = tk.Label(change_x, text="Insert X-label").grid(row=0)
                e_x = tk.Entry(change_x,bd=5,width=40)
                e_x.insert(0,axes[0].get_xlabel())
                e_x.grid(row=0,column=1)
                quit_x=tk.Button(change_x, text='Quit',command=change_x.destroy).grid(row=3, column=0, sticky=tk.W, pady=4)
                apply_x = tk.Button(change_x,text='Apply', command=xlabel).grid(row=3,column=1,sticky=tk.W, pady=4)

        def interact_y_limits():
            def ylimits():
                for ind,l_y in enumerate(ymin_lims):
                    axes[ind].set_ylim(float(l_y.get()),float(ymax_lims[ind].get()))
                    # ax.yaxis.set_minor_locator(AutoMinorLocator())
                fig.canvas.draw()
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
                x_val = var_val.get()
                x_int = var_xtick.get()
                if x_int == 'sec':
                    loc = mdates.SecondLocator(interval = int(x_val))
                    loc.MAXTICKS=10000
                    fig.axes[0].xaxis.set_major_locator(loc)
                elif x_int == 'min':
                    loc = mdates.MinuteLocator(interval = int(x_val))
                    loc.MAXTICKS=10000
                    fig.axes[0].xaxis.set_major_locator(loc)
                elif x_int == 'h':
                    fig.axes[0].xaxis.set_major_locator(mdates.HourLocator(interval = int(x_val)))
                fig.canvas.draw()
                change_xticks.destroy()

            def reset_xticks():
                fig.axes[0].xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
                fig.canvas.draw()
                change_xticks.destroy()

            try:
                if 'normal' == change_xticks().state():
                    change_xticks.lift()
            except:
                change_xticks=tk.Toplevel(master)
                change_xticks.resizable(width=False,height=False)
                change_xticks.title("X-ticks")
                xtick_label = tk.Label(change_xticks, text="Put X ticks every: ").grid(row=0,column=0)
                # xtick_inp1 = tk.Entry(change_xticks,bd=5,width=5)
                # xtick_inp1.grid(row=0,column=1)

                xtick_val = ['1','5','10','15','30','45']
                var_val = tk.StringVar(change_xticks)
                var_val.set(xtick_val[0])
                wval_xtick = tk.OptionMenu(change_xticks, var_val, *xtick_val)
                wval_xtick.grid(row=0,column=1)

                xtick_int = ['sec','min','h']
                var_xtick = tk.StringVar(change_xticks)
                var_xtick.set(xtick_int[0])
                w_xtick = tk.OptionMenu(change_xticks, var_xtick, *xtick_int)
                w_xtick.grid(row=0,column=2)

                apply_xtick = tk.Button(change_xticks, text='Apply',command=apply_xticks).grid(row=1,column=0,pady=5)
                reset_xtick = tk.Button(change_xticks, text='Reset',command=reset_xticks).grid(row=1,column=1,pady=5)

        def interact_colors():
            def OnClick(btn):
                text = btn.cget("text")
                pick_color=colorchooser.askcolor(title="Pick Color("+text+")")

                if  pick_color != (None,None):
                    for ind,l in enumerate(lines):
                        if l.get_label()==text:
                            l.set_c(pick_color[1])
                            leg.get_lines()[ind].set_c(pick_color[1])
                    if "Setpoint" in text:
                        lines[-1].set_color(pick_color[1])

                fig.canvas.draw()

            try:
                if 'normal' == change_color.state():
                    change_color.lift()
            except:
                change_color = tk.Toplevel()
                # change_color.resizable(width=False,height=False)
                change_color.title("ColorChanger")
                tk.Label(change_color,text="Pick a line:").grid(row=0,sticky=tk.W)
                for ind,line in enumerate(lines):
                    if not (line.get_label() == "_collection0"):
                        line_button=tk.Button(change_color,text=line.get_label())
                        line_button.config(command=lambda btn=line_button: OnClick(btn))
                        line_button.grid(row=0,column=ind+1)

            quit_y=tk.Button(change_color, text='Quit',command=change_color.destroy)
            quit_y.grid(row=1, column=0, sticky=tk.W, pady=5)

        global texts
        global vlines
        global hlines

        drs=[]
        texts=[]
        def add_text():
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
            x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/10
            ask_text = simpledialog.askstring("Add TextBox","Insert text",parent=master)
            text_rot = simpledialog.askfloat("Text Rotation","Insert text rotation(deg)",parent=master)
            text = fig.axes[0].text(x,y,ask_text,rotation=text_rot,fontdict={'size':12,'weight':'bold'},bbox=props,picker=5)
            texts.append(text)
            fig.canvas.draw()
            dr = move_obj(text,fig,None,master)
            dr.connect_obj()
            drs.append(dr)

        dvs=[]
        vlines=[]
        def add_vertical():
            x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/2
            v_line=fig.axes[0].axvline(x=x,linewidth=2,ls="--",c='k',picker=5)
            vlines.append(v_line)
            fig.canvas.draw()
            dv = move_obj(v_line,fig,"Vertical",master)
            dv.connect_obj()
            dvs.append(dv)

        dhs=[]
        hlines=[]
        def add_horizontal():
            y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
            h_line=fig.axes[0].axhline(y=y,linewidth=2,ls="--",c='k',picker=5)
            hlines.append(h_line)
            fig.canvas.draw()
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
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='-'),picker=5)
                    fig.canvas.draw()
                    da = move_obj(arrow_line,fig,"Arrow",master)
                    da.connect_obj()
                    das.append(da)
                elif choise == "Single Arrow":
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='->'),picker=5)
                    # arrow_line.draggable(state=True)
                    fig.canvas.draw()
                    da = move_obj(arrow_line,fig,"Arrow",master)
                    da.connect_obj()
                    das.append(da)

                elif choise == "Double Arrow":
                    arrow_line = fig.axes[0].annotate(s="",xy=(x,y),xytext=(xstart,y), arrowprops=dict(lw=2,arrowstyle='<->'),picker=5)
                    fig.canvas.draw()
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
        labels.add_command(label="Change Title",command = interact_title)
        labels.add_command(label="Change Y label",command = interact_y_label)
        labels.add_command(label="Change X label",command = interact_x_label)
        labels.add_command(label="Change Legend labels",command = interact_leg_label)

        menubar.add_cascade(label="Labels",menu=labels)

        limits=tk.Menu(menubar,tearoff=0)
        limits.add_command(label="Change Y limits",command = interact_y_limits)

        menubar.add_cascade(label="Limits",menu=limits)

        limits=tk.Menu(menubar,tearoff=0)
        limits.add_command(label="Change X ticks",command = interact_x_ticks)

        menubar.add_cascade(label="X ticks",menu=limits)

        colors=tk.Menu(menubar,tearoff=0)
        colors.add_command(label="Change Line Colors",command=interact_colors)

        menubar.add_cascade(label="LineColors",menu=colors)

        annotates=tk.Menu(menubar,tearoff=0)
        annotates.add_command(label="Text",command=add_text)
        annotates.add_command(label="Vertical Line",command=add_vertical)
        annotates.add_command(label="Horizontal Line",command=add_horizontal)
        annotates.add_command(label="Arrow Line",command=add_arrow)

        menubar.add_cascade(label="Annotate",menu=annotates)



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
                    legline.set_alpha(1.0)
                else:
                    legline.set_alpha(0.2)
                fig.canvas.draw()

        canvas.mpl_connect('pick_event', onpick)
        master.config(menu=menubar)
    except:pass

i=0
buttons=[]
buttons_frame=tk.Frame(choose_plot,borderwidth=2,relief="groove")
buttons_frame.grid(row=0,column=0,sticky=tk.NSEW)
buttons_frame.grid_columnconfigure(0,weight=1)

for k,v, in plots.items():
    buttons_frame.grid_rowconfigure(i,weight=1)
    b=HoverButton(buttons_frame,text=v,activebackground='green')
    b.config(command= lambda btn=b: plot_choise(btn))
    b.grid(row=i,column=0,sticky=tk.NSEW)
    i=i+1

r=1
meas_frame=tk.Frame(choose_plot)
meas_frame.grid(row=1,column=0,sticky=tk.NSEW)
meas_frame.grid_rowconfigure(0,weight=1)
# ,columnspan=len(m)+1)
tk.Label(meas_frame,text='Measurements:',borderwidth=2,relief="groove").grid(row=0,column=0,padx=5)
for key in m.keys():
    for c in m[key].columns:
        meas_frame.grid_columnconfigure(r,weight=1)
        tk.Label(meas_frame,text=c).grid(row=0,column=r,padx=5)
        r+=1
r=1
sets_frame=tk.Frame(choose_plot)
sets_frame.grid(row=2,column=0,sticky=tk.NSEW)
sets_frame.grid_rowconfigure(0,weight=1)

tk.Label(sets_frame,text='Setpoints:',borderwidth=2,relief="groove").grid(row=0,column=0,padx=5)
for key in s.keys():
    for c in s[key].columns:
        sets_frame.grid_columnconfigure(r,weight=1)
        tk.Label(sets_frame,text=c).grid(row=0,column=r,padx=5)
        r+=1
r=1
en_frame=tk.Frame(choose_plot)
en_frame.grid(row=3,column=0,sticky=tk.NSEW)
en_frame.grid_rowconfigure(0,weight=1)

tk.Label(en_frame,text='Enabled/Disabled:',borderwidth=2,relief="groove").grid(row=0,column=0,padx=5)
for key in en.keys():
    for c in en[key].columns:
        en_frame.grid_columnconfigure(r,weight=1)
        tk.Label(en_frame,text=c).grid(row=0,column=r,padx=5)
        r+=1

quit_button=tk.Button(choose_plot,text='Quit',command=destroyer)
quit_button.grid(columnspan=i,pady=10)
choose_plot.mainloop()
