# ./app.py
"""Builds the book scanner app"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from isbntools.app import registry, meta
import json

def returnBookMetadata(ISBN:str|int) -> str|dict:
    """Attemps to find information on a book given its ISBN number"""
    
    ISBN = str(ISBN) #isbntools.app.meta() only accepts string values
    ISBN.replace('-', '')
    
    try:
        data = eval(registry.bibformatters['json'](meta(ISBN))) # Converts JSON formatted string into regular dictionary
        
    except Exception as e:
        data = f'An Error Occurred : {e}'
        
    return data

class MainMenu(tk.Menu):
    """The application's menu bar"""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        settings_menu = tk.Menu(self, tearoff=False)
        self.autofill978 = tk.StringVar()
        self.autofill978.set(self.master.return_settings()["autofill-978"])
        settings_menu.add_checkbutton(label='Autofill \'978-\'', variable=self.autofill978, onvalue='1', offvalue='0', command=lambda: self.master.edit_settings("autofill-978", self.autofill978.get()))
        self.add_cascade(label='About', command= self._show_about)
        self.add_cascade(label='Quit', command=self.master.destroy) 
        self.add_cascade(label='Settings', menu=settings_menu)

    def _show_about(self) -> None:
        """Shows the about dialogue"""

        about_detail = 'Book Scanner App\nby Alex Toogood-Johnson\nFor assistance please contact the author'
        messagebox.showinfo(title='About', message=about_detail)

class App(tk.Tk):
    """The Book Scanner App"""

    def __init__(self, **kwargs) -> None:
        tk.Tk.__init__(self, **kwargs)
        
        self.geometry('600x300')
        self.resizable(False, False) # Window size cannot be changed
        self.title('Book Scanner App - Alex Toogood-Johnson')
        
        self.config(menu=MainMenu(self)) # Adds the menu to the top of the GUI
        self.taskbar_icon = ImageTk.PhotoImage(Image.open('Book Scanner/Data/logo.png'))
        self.iconphoto(True, self.taskbar_icon) # Sets the icon displayed in the taskbar and on the app
        
        self.create_page_layout()
        
    def create_page_layout(self) -> None:
        """Creates the notebook and frames that form the GUI"""
        
        book_entry = ttk.Notebook(self, width=600)
        inspect_record = tk.Frame(book_entry, height=275)
        view_books = tk.Frame(book_entry, height=275) # These frames form the content of the GUI
        manual_entry = tk.Frame(book_entry, height=275)
        automatic_entry = tk.Frame(book_entry, height=275)

        ISBNEntry = ttk.Labelframe(automatic_entry, text='ISBN Entry', width=140, height=132)
        self.ISBN = tk.StringVar()
        if self.return_settings()["autofill-978"] == '1':
            self.ISBN.set('978-')
        tk.Entry(ISBNEntry, textvariable=self.ISBN, width=20, relief=tk.GROOVE).pack(pady=60)
        tk.Label(ISBNEntry, background='#f0f0f0', width=40).pack()
        tk.Button(ISBNEntry, text='Submit', width=20, relief=tk.GROOVE, command=self.submit_automatic_entry).pack()
        tk.Button(ISBNEntry, text='Clear', command=self.clear_automatic_entry, width=20, relief=tk.GROOVE).pack(pady=20)
        ISBNEntry.place(x=5, y=5) # This labelframe allows the user to enter an ISBN to query
        
        ManualEntry = ttk.Labelframe(manual_entry, text='Enter Book Details', width=140, height=100)
        self.type = tk.StringVar()
        self.title = tk.StringVar()
        self.author = tk.StringVar()
        self.year = tk.StringVar()
        self.identifier = tk.StringVar()
        self.publisher = tk.StringVar()
        self.reset_manual_entry_variables()
        tk.Entry(ManualEntry, width=90, textvariable=self.type, relief=tk.GROOVE).pack(padx=20, pady=8)
        tk.Entry(ManualEntry, width=90, textvariable=self.title, relief=tk.GROOVE).pack(padx=20, pady=8)
        tk.Entry(ManualEntry, width=90, textvariable=self.author, relief=tk.GROOVE).pack(padx=20, pady=8)
        tk.Entry(ManualEntry, width=90, textvariable=self.year, relief=tk.GROOVE).pack(padx=20, pady=8)
        tk.Entry(ManualEntry, width=90, textvariable=self.identifier, relief=tk.GROOVE).pack(padx=20, pady=8)
        tk.Entry(ManualEntry, width=90, textvariable=self.publisher, relief=tk.GROOVE).pack(padx=20, pady=8)
        ManualEntry.place(x=5, y=5)
        tk.Button(manual_entry, text='Reset Entry Fields', width=30, relief=tk.GROOVE, command=self.reset_manual_entry_variables).place(x=40, y=245)
        tk.Button(manual_entry, text='Submit', width=30, relief=tk.GROOVE, command=self.manual_add_to_records).place(x=320, y=245)
        
        BookDetails = ttk.Labelframe(automatic_entry, text='Book Details', width=140, height=132)
        tk.Label(BookDetails, width=40, height=1, background='#f0f0f0').pack()
        self.search_results = tk.StringVar()
        tk.Label(BookDetails, width=30, height=9, background='#f5f5f5', textvariable=self.search_results, wraplength=200, relief=tk.GROOVE).pack(pady=5)
        tk.Button(BookDetails, text='Add book to records', relief=tk.GROOVE, command=self.add_to_records).pack(pady=20)
        BookDetails.place(x=300, y=5) # This labelframe shows the results of an ISBN query
        
        var = tk.Variable(value=self.get_book_names())
        listbox = tk.Listbox(view_books,width=95 ,height=13, listvariable=var, selectmode=tk.SINGLE)
        listbox.place(x=10, y=10) # This shows a list of all books contained within 'books.json'
        scrollbar = ttk.Scrollbar(view_books, orient=tk.VERTICAL, command=listbox.yview)
        listbox['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y) #Adds a scrollbar to listbox
        tk.Button(view_books, text='Refresh', width=30, relief=tk.GROOVE, command=lambda: var.set(self.get_book_names())).place(x=40, y=235)
        tk.Button(view_books, text='Analyse Book Data', width=30, relief=tk.GROOVE).place(x=320, y=235)
        
        self.inspect_book = tk.StringVar()
        self.inspect_book_results = tk.StringVar()
        tk.Entry(inspect_record, width=90, textvariable=self.inspect_book, relief=tk.GROOVE).pack(pady=20)
        tk.Button(inspect_record, text='Clear', width=30, relief=tk.GROOVE, command=self.clear_inspect_record_fields).place(x=40, y=60)
        tk.Button(inspect_record, text='Inspect', width=30, relief=tk.GROOVE, command=self.inspect_record).place(x=320, y=60)
        tk.Label(inspect_record, width=70, height=7, background='#f5f5f5', textvariable=self.inspect_book_results, wraplength=200, relief=tk.GROOVE).place(x=40, y=115)
        tk.Button(inspect_record, text='Delete Record', width=70, relief=tk.GROOVE, command=self.delete_record).place(x=40, y=240)
        
        book_entry.add(automatic_entry, text='  ~       Automatic Entry       ~  ')
        book_entry.add(manual_entry, text='  ~       Manual Entry        ~  ')
        book_entry.add(inspect_record, text='  ~       Inspect Record       ~  ')
        book_entry.add(view_books, text='  ~      View Books      ~  ')
        book_entry.place(x=0, y=-2) # Adds each frame to the main notebook
        
    def add_to_records(self, book_dict=None) -> None:
        """Adds a book to the records"""
        
        if not book_dict:
            book_dict = returnBookMetadata(self.ISBN.get())
        
        if isinstance(book_dict, str): # If the given ISBN is an error message, it is ignored
            return
        else:
            with open("Book Scanner/Data/books.json", 'r') as books_file:
                books = json.load(books_file)
            books["books"].append(book_dict)
            with open("Book Scanner/Data/books.json", 'w') as books_file:
                books_file.write(json.dumps(books))
            self.clear_automatic_entry() # Clears all boxes
    
    def reset_manual_entry_variables(self) -> None:
        self.type.set('Type')
        self.title.set('Title')
        self.author.set('Author')
        self.year.set('Year')
        self.identifier.set('ISBN')
        self.publisher.set('Publisher')
            
    def manual_add_to_records(self) -> None:
        type = self.type.get()
        if type in ('', 'Type'):
            type = 'book'
        title = self.title.get()
        if title == 'Title':
            return
        author = self.author.get()
        if author == 'Author':
            return
        year = self.year.get()
        if year == 'Year':
            return
        identifier = self.identifier.get().replace('-', '')
        if identifier == 'ISBN':
            return
        publisher = self.publisher.get()
        if publisher == 'Publisher':
            return
        
        book_dict = {'type' : type, 'title' : title, 'author' : [{'name' : author}], 'year' : year, 'identifier' : [{'type' : 'ISBN', 'id' : identifier}], 'publisher' : publisher}
        self.add_to_records(book_dict)
        
    def clear_automatic_entry(self) -> None:
        """Clears the boxes in the 'Automatic Entry' notebook tab"""
        
        self.search_results.set('')
        if self.return_settings()["autofill-978"] == '1':
            self.ISBN.set('978-')
        else:
            self.ISBN.set('')
        
    def submit_automatic_entry(self) -> None:
        """Displays the results for a given ISBN query"""
        
        book_dict = returnBookMetadata(self.ISBN.get())
        
        if isinstance(book_dict, str):
            self.search_results.set(book_dict)
        else:
            title = 'Title : ' + book_dict['title']
            author = 'Author : ' + book_dict['author'][0]['name']
            year = 'Year : ' + book_dict['year']
            publisher = 'Publisher : ' + book_dict['publisher']
            self.search_results.set('\n'.join([title, author, year, publisher]))

    def get_book_names(self) -> list:
        """Returns a list of each book in 'books.json' and the corresponding author"""
        
        with open("Book Scanner/Data/books.json", 'r') as books_json_file:
            books_dictionary = json.load(books_json_file)["books"]
            
        return [(book['title'], '|',book['author'][0]['name']) for book in books_dictionary]
    
    def return_settings(self) -> dict:
        """Returns a dict of app settings from 'settings.json'"""
        
        with open("Book Scanner/Data/settings.json", 'r') as settings_json_file:
            settings = json.load(settings_json_file)["settings"]
        return settings

    def edit_settings(self, setting_name, updated_value) -> None:
        """Changes a setting (setting_name) to updated_value"""
        
        with open("Book Scanner/Data/settings.json", 'r') as settings_json_file:
            settings = json.load(settings_json_file)
            
        if setting_name in settings["settings"].keys():
            settings["settings"][setting_name] = updated_value
            
        with open("Book Scanner/Data/settings.json", 'w') as settings_json_file:
            settings_json_file.write(json.dumps(settings))
            
    def inspect_record(self) -> None:
        records = self.inspect_book.get().replace('{', '').replace('}', '').split('|')
        record = [record.strip() for record in records]
        if len(record) == 2:
            with open("Book Scanner/Data/books.json", 'r') as books_json_file:
                books_dictionary = json.load(books_json_file)["books"]
            for book in books_dictionary:
                if book['author'][0]['name'] == record[1]:
                    if record[0] in book['title']:
                        title = 'Title : ' + book['title']
                        author = 'Author : ' + book['author'][0]['name']
                        year = 'Year : ' + book['year']
                        publisher = 'Publisher : ' + book['publisher']
                        self.inspect_book_results.set('\n'.join([title, author, year, publisher]))
        else:
            self.inspect_book_results.set('No books found with that title and author')
            
    def delete_record(self) -> None:
        """Deletes a selected book from the system"""
        
        records = self.inspect_book.get().replace('{', '').replace('}', '').split('|')
        record = [record.strip() for record in records]
        if self.inspect_book_results.get() == 'No books found with that title and author':
            return
        else:
            with open("Book Scanner/Data/books.json", 'r') as books_json_file:
                books_dictionary = json.load(books_json_file)
            for book in books_dictionary["books"]:
                if book['author'][0]['name'] == record[1]:
                    if record[0] in book['title']:
                        books_dictionary["books"].remove(book)
                        with open("Book Scanner/Data/books.json", 'w') as books_file:
                            books_file.write(json.dumps(books_dictionary))
                        self.clear_inspect_record_fields()
                        return
                    
    def clear_inspect_record_fields(self) -> None:
        self.inspect_book.set('')
        self.inspect_book_results.set('')
                            
if __name__ == "__main__":
    app = App()
    app.mainloop()
