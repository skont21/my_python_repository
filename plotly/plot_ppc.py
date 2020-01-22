# %matplotlib notebook
from plot_maplot_v1 import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib as mpl
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

csv=input("Please enter the path of you csv file:")
data = get_data_from_csv(csv)
(time,m,s,en)=get_traces(data)
print(CBOLD+"Traces Found:"+CEND+"\n")
print(CBOLD+"Measurements"+CEND)
print("------------")
for k in m.keys():
    print(k,"------>",m[k].name)
print(CBOLD+"Setpoints"+CEND)
print("------------")
plots=dict()
i=1
for k in s.keys():
    plots[str(i)]=k
    print(k,"------>",s[k].name)
    i=i+1
if ('P' in s.keys())&('Q' in s.keys()):
    plots[str(i)]='Q Capability'
    i=i+1
plots[str(i)]="All Measurements"
print(CBOLD+"Enable/Disable"+CEND)
print("-------------")
for k in en.keys():
    print(k,"------>",en[k].name)

print("\n"+"What plot would you like to generate?"+"\n\n"+CBOLD+"Available Choises"+CEND+"\n")
for k,v, in plots.items():
    print(k,")",v)
while True:
    choise = input(CBOLD+"Choose by Number:"+CEND)
    print("\n")
    try:
        choise=int(choise)
        if choise in range(1,len(plots)+1):
            break
        else:
            print("\n"+"Enter a valid nuber"+"\n")
    except:
        print("\n"+"Enter a valid nuber:"+"\n")



if plots[str(choise)]=="P":
    pdb=float(input("Enter the desired setpoint deadband(kW):"))
    fig,axes,lines,leg= plot_P(time,m['P'],s['P'],en['P'],pdb)
elif  plots[str(choise)]=="Q":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    fig,axes,lines,leg= plot_Q(time,m['Q'],s['Q'],en['Q'],qdb)
elif  plots[str(choise)]=="AVR":
    avrdb=float(input("Enter the desired setpoint deadband(V):"))
    fig,axes,lines,leg= plot_AVR(time,m['V'],s['AVR'],m['Q'],en['AVR'],avrdb)
elif  plots[str(choise)]=="QV":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    fig,axes,lines,leg= plot_QV(time,m['V'],s['QV'],m['Q'],s['Q'],en['QV'],qdb)
elif  plots[str(choise)]=="F":
    pdb=float(input("Enter the desired setpoint deadband(kW):"))
    fig,axes,lines,leg= plot_F_P(time,m['P'],s['P'],m['F'],s['F'],en['F'],pdb)
elif  plots[str(choise)]=="PF":
    pfdb=float(input("Enter the desired setpoint deadband:"))
    fig,axes,lines,leg= plot_PF(time,m['PF'],s['PF'],en['PF'],pfdb)
elif  plots[str(choise)]=="All Measurements":
    fig,axes,lines,leg= plot_meas(time,m['P'],m['Q'],m['V'],m['PF'],m['F'])
elif  plots[str(choise)]=="Q Capability":
    qdb=float(input("Enter the desired setpoint deadband(kVAr):"))
    fig,axes,lines,leg= plot_PQ(time,m['P'],m['Q'],s['Q'],en['Q'],qdb)


master = tk.Tk(className=' PLOT')

def destroyer():
    master.quit()
    master.destroy()
master.protocol("WM_DELETE_WINDOW",destroyer)

frame = tk.Frame(master)

canvas = FigureCanvasTkAgg(fig, master)
toolbar = NavigationToolbar2Tk(canvas, frame)
toolbar.update()

canvas.get_tk_widget().grid(row=0)
frame.grid(row=1,sticky=tk.W)


quitbutton = tk.Button(master, text="Quit", command=destroyer)
quitbutton.grid(row=1,padx=5)

def interact(*args):

    def interact_title():
        if e_title.get()!='':
            title_x= axes[0].title.get_position()[0]
            title_y= axes[0].title.get_position()[1]
            axes[0].set_title(e_title.get(),fontdict=font,x=title_x,y=title_y)
            fig.canvas.draw()
            change_title.destroy()

    def interact_y_label():
        for ind,e_y in enumerate(y_entries):
            axes[ind].set_ylabel(e_y.get())
            fig.canvas.draw()
        change_y.destroy()

    def interact_x_label():
        if e_x.get()!='':
            axes[0].set_xlabel(e_x.get())
            fig.canvas.draw()
            change_x.destroy()

    if label_variable.get()=="Change Title":
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
            apply_title = tk.Button(change_title,text='Apply title', command=interact_title).grid(row=3,column=1,sticky=tk.W, pady=4)

    elif label_variable.get()=="Change Y label":
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
            apply_y = tk.Button(change_y,text='Apply', command=interact_y_label).grid(row=len(axes)+3,column=1,sticky=tk.W, pady=4)

    elif label_variable.get()=="Change X label":
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
            apply_x = tk.Button(change_x,text='Apply', command=interact_x_label).grid(row=3,column=1,sticky=tk.W, pady=4)

label_variable = tk.StringVar(master)
label_variable.set("Labels")
label_tuple=("Change Title","Change Y label","Change X label")
labels= tk.OptionMenu(master,label_variable,*label_tuple,command=interact)
labels.grid(row=1,sticky=tk.E)

# we will set up a dict mapping legend line to orig line, and enable
# picking on the legend line
lined = dict()
for legline, origline in zip(leg.get_lines(), lines):
    legline.set_picker(5)  # 5 pts tolerance
    lined[legline] = origline

def onpick(event):
    # on the pick event, find the orig line corresponding to the
    # legend proxy line, and toggle the visibility
    legline = event.artist
    origline = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)
    fig.canvas.draw()

canvas.mpl_connect('pick_event', onpick)

master.mainloop()
