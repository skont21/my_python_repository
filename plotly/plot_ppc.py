# %matplotlib notebook
from plot_maplot_v1 import *
import tkinter as tk
from tkinter import colorchooser,filedialog,simpledialog,messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib as mpl
import sys
import re
mpl.use('TkAgg')

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CBOLD = '\33[1m'
CURL = '\33[4m'
CEND = '\33[0m'

# csv=input("Please enter the path of you csv file:")

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
choose_plot.geometry("")
# x=choose_plot.winfo_x()
# y=choose_plot.winfo_y()


def plot_choise(button):
    global strace
    def ask_deadband(title):
        global deadband

        def apply_db():
            global deadband
            try:
                deadband=float(e_db.get())
            except:
                messagebox.showwarning("Warning","Invalid Input")
            input_db.destroy()

        input_db=tk.Toplevel(choose_plot)
        input_db.geometry("+{}+{}".format(choose_plot.winfo_x(),choose_plot.winfo_y()))
        input_db.withdraw()
        input_db.protocol("WM_DELETE_WINDOW")
        input_db.title(title)
        tk.Label(input_db,text='Enter Deadband').grid(row=0)
        e_db=tk.Entry(input_db)
        e_db.grid(row=0,column=1)
        apply_db=tk.Button(input_db,text="Apply",command=apply_db).grid(row=2,column=0,columnspan=2,pady=4)
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
        # strace=vs.get()

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
        if len(s['P'].columns)>1:
            ask_trace('P Setpoint',s['P'])
        else:
            strace=1
        fig,axes,lines,leg= plot_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],en['P'].iloc[:,0],pdb)

    elif  button_text=="Q":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        fig,axes,lines,leg= plot_Q(time,m['Q'].iloc[:,0],s['Q'].iloc[:,strace-1],en['Q'].iloc[:,0],qdb)

    elif  button_text=="AVR":
        ask_deadband('Voltage Deadband in V')
        avrdb=deadband
        fig,axes,lines,leg= plot_AVR(time,m['V'].iloc[:,0],s['AVR'].iloc[:,0],m['Q'].iloc[:,0],en['AVR'].iloc[:,0],avrdb)

    elif  button_text=="QV":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        fig,axes,lines,leg= plot_QV(time,m['V'].iloc[:,0],s['QV'].iloc[:,0],m['Q'].iloc[:,0],s['Q'][:,strace-1],en['QV'].iloc[:,0],qdb)

    elif  button_text=="F":
        ask_deadband('P Deadband in kW')
        pdb=deadband
        if len(s['P'].columns)>1:
            ask_trace('P Setpoint',s['P'])
        else:
            strace=1
        print(strace)
        fig,axes,lines,leg= plot_F_P(time,m['P'].iloc[:,0],s['P'].iloc[:,strace-1],m['F'].iloc[:,0],s['F'].iloc[:,0],en['F'].iloc[:,0],pdb)

    elif  button_text=="PF":
        ask_deadband('PF Deadband')
        pfdb=deadband
        fig,axes,lines,leg= plot_PF(time,m['PF'].iloc[:,0],s['PF'].iloc[:,0],en['PF'].iloc[:,0],pfdb)

    elif  button_text=="All Measurements":
        fig,axes,lines,leg= plot_meas(time,m['P'].iloc[:,0],m['Q'].iloc[:,0],m['V'].iloc[:,0],m['PF'].iloc[:,0],m['F'].iloc[:,0])

    elif  button_text=="Q Capability":
        ask_deadband('Q Deadband in kVAr')
        qdb=deadband
        if len(s['Q'].columns)>1:
            ask_trace('Q Setpoint',s['Q'])
        else:
            strace=1
        fig,axes,lines,leg= plot_PQ(time,m['P'].iloc[:,0],m['Q'].iloc[:,0],s['Q'][:,strace-1],en['Q'].iloc[:,0],qdb)

    lined = dict()
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # 5 pts tolerance
        lined[legline] = origline

    master = tk.Toplevel()
    master.title("PLOT")

    def destroyer():
        master.quit()
        master.destroy()
    master.protocol("WM_DELETE_WINDOW",destroyer)

    frame = tk.Frame(master)

    canvas = FigureCanvasTkAgg(fig, master)
    toolbar = NavigationToolbar2Tk(canvas, frame)
    toolbar.update()

    canvas.get_tk_widget().grid(row=1)
    frame.grid(row=2,sticky=tk.W)

    quitbutton = tk.Button(master, text="Quit", command=destroyer)
    quitbutton.grid(row=2)

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
            change_title = tk.Toplevel()
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
            change_y = tk.Toplevel()
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
            change_x = tk.Toplevel()
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
            change_ylim = tk.Toplevel()
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
            # print(text)
            pick_color=colorchooser.askcolor(title="Pick Color("+text+")")

            if  pick_color != (None,None):
                for ind,l in enumerate(lines):
                    # print(l.get_label())
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
                    line_button.grid(row=ind,column=1,columnspan=2)

        quit_y=tk.Button(change_color, text='Quit',command=change_color.destroy).grid(row=2*len(axes)+3, column=0, sticky=tk.W, pady=4)

    menubar=tk.Menu(master)

    labels=tk.Menu(menubar,tearoff=0)
    labels.add_command(label="Change Title",command = interact_title)
    labels.add_command(label="Change Y label",command = interact_y_label)
    labels.add_command(label="Change X label",command = interact_x_label)

    menubar.add_cascade(label="Labels",menu=labels)

    limits=tk.Menu(menubar,tearoff=0)
    limits.add_command(label="Change Y limits",command = interact_y_limits)
    # limits.add_command(label="Change X limits",command = interact_x_limits)

    menubar.add_cascade(label="Limits",menu=limits)

    colors=tk.Menu(menubar,tearoff=0)
    colors.add_command(label="Change Line Colors",command=interact_colors)

    menubar.add_cascade(label="LineColors",menu=colors)

    # we will set up a dict mapping legend line to orig line, and enable
    # picking on the legend line

    def onpick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
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

    choose_plot.destroy()

i=0
buttons=[]
for k,v, in plots.items():
    # print(k,")",v)
    b=tk.Button(choose_plot,text=v)
    # buttons.append(b)
    b.config(command= lambda btn=b: plot_choise(btn))
    b.grid(row=0,column=i)
    i=i+1

choose_plot.mainloop()
