# -*- coding: utf-8 -*-

import sqlite3, tkinter

class Scrollbox(tkinter.Listbox):
    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)
        self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)
        
    def grid(self, row, column, sticky='nse', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set

class DataListbox(Scrollbox):
    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)
        
        self.linked_box = None
        self.link_field = None
        self.link_value = None
        
        self.cursor = connection.cursor()
        self.field = field
        self.table = table
        
        self.bind('<<ListboxSelect>>', self.on_select)
        
        self.sql_select = "select " + self.field + ", _id from " + self.table
        
        if sort_order:
            self.sql_sort = " order by " + ','.join(sort_order)
        else:
            self.sql_sort = " order by " + self.field
            
    def clear(self):
        self.delete(0, tkinter.END)
    
    def link(self, widget, link_field):
        self.linked_box = widget
        widget.link_field = link_field
    
    def requery(self, link_value=None):
        self.link_value = link_value    # Store the id, so we know the "master" record we're populated from
        if link_value and self.link_field:
            sql = self.sql_select + " where " + self.link_field + " = ?" + self.sql_sort
            print(sql)    #TODO delete this line
            self.cursor.execute(sql, (link_value,))
        else:
            print(self.sql_select + self.sql_sort)    #TODO delete this line
            self.cursor.execute(self.sql_select + self.sql_sort)
        
        # clear the listbox contents before re-loading
        self.clear()
        for value in self.cursor:
            self.insert(tkinter.END, value[0])
            
        if self.linked_box:
            self.linked_box.clear()
    
    def on_select(self, event):
        if self.linked_box:
            try:
                print(self is event.widget)    #TODO delete this line        
                index = int(self.curselection()[0])
                value = self.get(index),
            
            
                # Get the ID from the database row
                # Make sure we're getting the correct one, by including the link_value if appropriate
                if self.link_value:
                    value = value[0], self.link_value
                    sql_where = " where " + self.field + " = ? and " + self.link_field + " = ?" 
                else:
                    sql_where = " where " + self.field + " = ?"
                
                link_id = self.cursor.execute(self.sql_select + sql_where, value).fetchone()[1]
                
                self.linked_box.requery(link_id)
            
            except:
                pass
        
if __name__ == "__main__":
    db = sqlite3.connect("music.db")
    mainWindow = tkinter.Tk()
    mainWindow.title('Music DB Browser')
    mainWindow.geometry('1024x768')
    
    mainWindow.columnconfigure(0, weight=2)
    mainWindow.columnconfigure(1, weight=2)
    mainWindow.columnconfigure(2, weight=2)
    mainWindow.columnconfigure(3, weight=1) # spacer column on right
    
    mainWindow.rowconfigure(0, weight=1)
    mainWindow.rowconfigure(1, weight=5)
    mainWindow.rowconfigure(2, weight=5)
    mainWindow.rowconfigure(3, weight=1)
    
    # ==== Labels =====
    tkinter.Label(mainWindow, text="Artists").grid(row=0, column=0, sticky='nsew')
    tkinter.Label(mainWindow, text="Albums").grid(row=0, column=1, sticky='nsew')
    tkinter.Label(mainWindow, text="Songs").grid(row=0, column=2, sticky='nsew')
    
    # ==== Artists Listbox ====
    artistList = DataListbox(mainWindow, db, "artists", "name")
    artistList.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(30, 0))
    artistList.config(border=2, relief='sunken')
    
    artistList.requery()
    
    # ==== Artists ScrollBar ====
    artistScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=artistList.yview)
    artistScroll.grid(row=1, column=0, sticky='nse', rowspan=2)
    artistList['yscrollcommand'] = artistScroll.set
    
    # ==== Albums Listbox ====
    albumLV = tkinter.Variable(mainWindow)
    albumLV.set(("Choose an artist",))
    albumList = DataListbox(mainWindow, db, "albums", "name", sort_order=("name",))
    albumList.grid(row=1, column=1, sticky='nsew', padx=(30, 0))
    albumList.config(border=2, relief='sunken')
    
    artistList.link(albumList, "artist")
    
    albumScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=albumList.yview)
    albumScroll.grid(row=1, column=1, sticky='nse', rowspan=2)
    albumList['yscrollcommand'] = albumScroll.set
    
    # ==== Songs Listbox ====
    songsLV = tkinter.Variable(mainWindow)
    songsLV.set(("Choose an album",))
    songList = DataListbox(mainWindow, db, "songs", "title", sort_order=("track",))
    songList.grid(row=1, column=2, sticky='nsew', padx=(30, 0))
    songList.config(border=2, relief='sunken')
    
    albumList.link(songList, "album")
    
    songScroll = tkinter.Scrollbar(mainWindow, orient=tkinter.VERTICAL, command=songList.yview)
    songScroll.grid(row=1, column=2, sticky='nse', rowspan=2)
    songList['yscrollcommand'] = songScroll.set
    
    mainWindow.mainloop()
    print("Closing database connection")
    db.close()
     
    
    
    
    
    
    
    
    
    
