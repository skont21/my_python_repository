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
    def __init__(self,obj,figure,align):
        self.obj=obj
        self.figure=figure
        self.pick=None
        self.align=align

    def connect_obj(self):
        'connect to all the events we need'
        self.cidpress = self.figure.canvas.mpl_connect('pick_event', self.on_pick_obj)
        self.cidrelease = self.figure.canvas.mpl_connect('button_release_event', self.on_release_obj)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion_obj)
        self.ciddouble = self.figure.canvas.mpl_connect('button_press_event', self.onclik)

    def on_pick_obj(self, event):
        print(self.figure.axes[0].texts)
        'on button pick we will see if the mouse is over us and store some data'
        if isinstance(event.artist, Text):
            if isinstance(self.obj,Text):
                xlim_cur=self.figure.axes[0].get_xlim()[1]-self.figure.axes[0].get_xlim()[0]
                ylim_cur=self.figure.axes[0].get_ylim()[1]-self.figure.axes[0].get_ylim()[0]
                xlen=xlim_cur/29.808
                ylen=ylim_cur/7.556
                x0, y0 = self.obj.get_position()
                print(x0,y0)
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
        if isinstance(self.obj,Text):
            self.obj.set_position((event.xdata,event.ydata))
            self.figure.canvas.draw()
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
        self.figure.canvas.draw()

    def onclik(self,event):
        if self.pick is None:
            return
        if event.dblclick:
            if event.button == 1:
                if self.obj in self.figure.axes[0].texts:
                    delete= tk.messagebox.askquestion('Delete TextBox','Are you sure you want to delete the texbox?',icon = 'warning')
                    if delete =="yes":
                        self.obj.remove()
                        self.figure.canvas.draw()
                elif self.obj in self.figure.axes[0].lines:
                    delete= tk.messagebox.askquestion('Delete Line','Are you sure you want to delete the line?',icon = 'warning')
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
        MsgBox = tk.messagebox.askquestion ('Exit Application','Are you sure you want to exit the application',icon = 'warning')
        if MsgBox == 'yes':
           sys.exit()
        else:
            tk.messagebox.showinfo('Return','You will now return to the application screen')


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
        fig,axes,lines,leg= plot_meas(time,m['P'].iloc[:,0],m['Q'].iloc[:,0],m['V'].iloc[:,0],m['PF'].iloc[:,0],m['F'].iloc[:,0])

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
            dr = move_obj(text,fig,None)
            dr.connect_obj()
            drs.append(dr)

        dvs=[]
        vlines=[]
        def add_vertical():
            x=fig.axes[0].get_xlim()[0]+(fig.axes[0].get_xlim()[1]-fig.axes[0].get_xlim()[0])/2
            v_line=fig.axes[0].axvline(x=x,linewidth=2,ls="--",c='k',picker=5)
            vlines.append(v_line)
            fig.canvas.draw()
            dv = move_obj(v_line,fig,"Vertical")
            dv.connect_obj()
            dvs.append(dv)

        dhs=[]
        hlines=[]
        def add_horizontal():
            y=fig.axes[0].get_ylim()[0]+(fig.axes[0].get_ylim()[1]-fig.axes[0].get_ylim()[0])/10
            h_line=fig.axes[0].axhline(y=y,linewidth=2,ls="--",c='k',picker=5)
            hlines.append(h_line)
            fig.canvas.draw()
            dh = move_obj(h_line,fig,"Horizontal")
            dh.connect_obj()
            dhs.append(dh)

        menubar=tk.Menu(master)

        labels=tk.Menu(menubar,tearoff=0)
        labels.add_command(label="Change Title",command = interact_title)
        labels.add_command(label="Change Y label",command = interact_y_label)
        labels.add_command(label="Change X label",command = interact_x_label)

        menubar.add_cascade(label="Labels",menu=labels)

        limits=tk.Menu(menubar,tearoff=0)
        limits.add_command(label="Change Y limits",command = interact_y_limits)

        menubar.add_cascade(label="Limits",menu=limits)

        colors=tk.Menu(menubar,tearoff=0)
        colors.add_command(label="Change Line Colors",command=interact_colors)

        menubar.add_cascade(label="LineColors",menu=colors)

        annotates=tk.Menu(menubar,tearoff=0)
        annotates.add_command(label="Text",command=add_text)
        annotates.add_command(label="Vertical Line",command=add_vertical)
        annotates.add_command(label="Horizontal Line",command=add_horizontal)

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
