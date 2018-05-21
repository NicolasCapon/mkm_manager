#!/usr/bin/python3
import os
import tkinter
import tkinter.ttk as ttk
import controller

# root = Tk()
# w, h = root.winfo_screenwidth(), root.winfo_screenheight()
# root.geometry("%dx%d+0+0" % (w, h))

# Frame2 = LabelFrame(root, text="Card list", borderwidth=2, relief=GROOVE)
# Frame2.pack(side=RIGHT, anchor=W, fill=BOTH, expand=YES)
# Label(Frame2, text="Frame 2").pack(padx=10, pady=10)

# Frame3 = LabelFrame(root, text="Commands", borderwidth=2, relief=GROOVE)
# Frame3.pack(side=BOTTOM, anchor=W, fill=BOTH, expand=YES)
# Label(Frame3, text="Frame 3").pack(padx=10, pady=10)

# Frame1 = LabelFrame(root, text="Card infos", borderwidth=2, relief=GROOVE)
# Frame1.pack(side=LEFT, anchor=W, fill=BOTH, expand=YES)
# Label(Frame1, text="Frame 1").pack(padx=10, pady=10)

# root.mainloop()

class mkm_seller_gui(tkinter.Tk):
    
    def __init__(self, parent):        
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.mkm_seller_controller = controller.mkm_seller_controller()
        
        # Draw menu bar
        menubar = tkinter.Menu(self)

        menu1 = tkinter.Menu(menubar, tearoff=0)
        menu1.add_command(label="Open CSV", command=self.populate_treeView)
        menu1.add_command(label="Create CSV", command=self.populate_treeView)
        menu1.add_separator()
        menu1.add_command(label="MKM Log In", command=self.populate_treeView)
        
        menubar.add_cascade(label="File", menu=menu1)
        self.config(menu=menubar)
        
        # Draw basic layout
        # self.grid()
        
        self.label = tkinter.LabelFrame(self, text="Card infos", borderwidth=2, relief=tkinter.GROOVE)
        self.label.grid(column=0,row=0,sticky='nesw')

        label2 = tkinter.LabelFrame(self, text="Card list", width=450, borderwidth=2, relief=tkinter.GROOVE)
        label2.grid(column=1,row=0, rowspan=2, sticky='nesw')

        label4 = tkinter.LabelFrame(self, text="Commands", borderwidth=2, relief=tkinter.GROOVE)
        label4.grid(column=0,row=1,sticky='nesw')

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        
        self.tree = ttk.Treeview(label2)
        vsb = ttk.Scrollbar(label2, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        #tree.configure(yscrollcommand=vsb.set)
        titles = ("set", "condition", "language", "price", "extra", "number")
        self.tree["columns"] = titles
        for title in titles:
            self.tree.column(title, minwidth=40, width=110, stretch=False)
            self.tree.heading(title, text=title)
        # On double click :
        self.tree.bind("<Double-1>", self.on_treeView_click)
        self.tree.pack(fill="both", expand=True)
        label2.pack_propagate(0)
        
        # card image
        self.label_image = tkinter.Label(self.label, text="card image", relief=tkinter.GROOVE)
        self.label_image.grid(column=0,row=0, sticky='nesw')
        
        label_card_info = tkinter.Label(self.label, relief=tkinter.GROOVE)
        label_card_info.grid(column=1,row=0, sticky='nesw')
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)       
        
        # card info details
        info_list = ["name","expansion", "rarity", "link", "reprints number", "Number of articles", "Number of foil articles"]
        for i, infos in enumerate(info_list):
            tkinter.Label(label_card_info, text=infos, relief=tkinter.GROOVE).grid(column=0,row=i, sticky='nesw')
            tkinter.Label(label_card_info, text=infos, relief=tkinter.GROOVE).grid(column=1,row=i, sticky='nesw')
        
    def populate_treeView(self):
        self.mkm_seller_controller.populate_card_tree(self.tree)
        
    def on_treeView_click(self, event):
        self.mkm_seller_controller.show_card_details(self.tree, self.label)

if __name__ == "__main__":
    app = mkm_seller_gui(None)
    app.title("Test App")
    w, h = app.winfo_screenwidth(), app.winfo_screenheight()
    app.geometry("%dx%d+0+0" % (w, h))
    app.mainloop()