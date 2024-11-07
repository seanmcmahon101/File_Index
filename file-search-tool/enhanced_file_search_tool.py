import os
import threading
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import ctypes
import subprocess

# Function to index files on the C: drive
def index_files(progress_callback=None):
  conn = sqlite3.connect('file_index.db')
  c = conn.cursor()
  c.execute('DROP TABLE IF EXISTS files')
  c.execute('CREATE TABLE files (filename TEXT, filepath TEXT)')
  conn.commit()

  # Create an index on the filename column
  c.execute('CREATE INDEX idx_filename ON files(filename)')
  conn.commit()

  # Directories to skip (you can modify this list)
  skip_dirs = ['C:\\$Recycle.Bin', 'C:\\System Volume Information']

  file_count = 0
  start_time = time.time()

  for root, dirs, files in os.walk('C:\\', topdown=True):
      # Skip directories
      dirs[:] = [d for d in dirs if os.path.join(root, d) not in skip_dirs]

      # Handle progress callback
      if progress_callback:
          progress_callback(root)

      # Collect file data
      file_data = []
      for name in files:
          filepath = os.path.join(root, name)
          try:
              file_data.append((name.lower(), filepath))
              file_count += 1
          except Exception as e:
              # Handle any exceptions (e.g., permission errors)
              pass

      # Insert file data into the database
      if file_data:
          try:
              c.executemany('INSERT INTO files (filename, filepath) VALUES (?, ?)', file_data)
              conn.commit()
          except sqlite3.Error as e:
              print(f'Error inserting files: {e}')

  conn.close()
  end_time = time.time()
  print(f'Indexing completed in {end_time - start_time:.2f} seconds.')
  print(f'Indexed {file_count} files.')

# Function to search the indexed files
def search_files(query):
  conn = sqlite3.connect('file_index.db')
  c = conn.cursor()
  search_query = f'%{query.lower()}%'
  c.execute('SELECT filename, filepath FROM files WHERE filename LIKE ? LIMIT 1000', (search_query,))
  results = c.fetchall()
  conn.close()
  return results

# Function to open the containing folder
def open_containing_folder(filepath):
  folder = os.path.dirname(filepath)
  if os.path.exists(folder):
      os.startfile(folder)
  else:
      messagebox.showerror("Error", f"Folder does not exist:\n{folder}")

# GUI Application
class FileSearchApp(tk.Tk):
  def __init__(self):
      super().__init__()
      self.title("File Search Tool")
      self.geometry("800x600")
      self.create_widgets()
      self.indexing_thread = threading.Thread(target=self.start_indexing)
      self.indexing_thread.daemon = True
      self.indexing_thread.start()

  def create_widgets(self):
      # Search Entry
      self.search_var = tk.StringVar()
      self.search_var.trace('w', self.update_search)
      self.search_entry = ttk.Entry(self, textvariable=self.search_var, width=100)
      self.search_entry.pack(pady=10, padx=10, fill=tk.X)

      # Results Listbox
      self.results_listbox = tk.Listbox(self)
      self.results_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
      self.results_listbox.bind('<Double-Button-1>', self.open_selected_folder)

      # Status Bar
      self.status_var = tk.StringVar()
      self.status_label = ttk.Label(self, textvariable=self.status_var)
      self.status_label.pack(pady=5, padx=5, side=tk.BOTTOM, anchor=tk.W)

  def start_indexing(self):
      self.status_var.set("Indexing files on C:\\ drive...")
      index_files(progress_callback=self.update_status)
      self.status_var.set("Indexing completed. Ready to search.")

  def update_status(self, current_directory):
      self.status_var.set(f"Indexing: {current_directory}")

  def update_search(self, *args):
      query = self.search_var.get()
      if not query.strip():
          self.results_listbox.delete(0, tk.END)
          return

      results = search_files(query)
      self.results_listbox.delete(0, tk.END)
      for filename, filepath in results:
          self.results_listbox.insert(tk.END, f"{filename} | {filepath}")

  def open_selected_folder(self, event):
      selection = self.results_listbox.curselection()
      if selection:
          index = selection[0]
          item = self.results_listbox.get(index)
          filepath = item.split('|', 1)[1].strip()
          open_containing_folder(filepath)

if __name__ == "__main__":
  app = FileSearchApp()
  app.mainloop()