import os
import threading
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import subprocess
import sys

# Function to initialize the database
def initialize_db(conn):
  c = conn.cursor()
  c.execute('''
      CREATE TABLE IF NOT EXISTS files (
          filename TEXT,
          filepath TEXT,
          modified_time REAL
      )
  ''')
  c.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
  c.execute('CREATE INDEX IF NOT EXISTS idx_filepath ON files(filepath)')
  conn.commit()

# Function to index files on the C: drive
def index_files(update_callback=None, complete_callback=None):
  conn = sqlite3.connect('file_index.db')
  initialize_db(conn)
  c = conn.cursor()

  # Directories to skip (you can modify this list)
  skip_dirs = ['C:\\$Recycle.Bin', 'C:\\System Volume Information']

  file_count = 0
  start_time = time.time()

  # Fetch existing file paths and their modified times
  c.execute('SELECT filepath, modified_time FROM files')
  existing_files = {row[0]: row[1] for row in c.fetchall()}

  # Set to keep track of current files
  current_files = set()

  for root, dirs, files in os.walk('C:\\', topdown=True):
      # Skip directories
      dirs[:] = [d for d in dirs if os.path.join(root, d) not in skip_dirs]

      # Handle progress callback
      if update_callback:
          update_callback(root)

      for name in files:
          filepath = os.path.join(root, name)
          try:
              modified_time = os.path.getmtime(filepath)
              current_files.add(filepath)

              if filepath in existing_files:
                  if existing_files[filepath] == modified_time:
                      continue  # File unchanged, skip
                  else:
                      # Update modified_time for changed file
                      c.execute('UPDATE files SET modified_time = ? WHERE filepath = ?', (modified_time, filepath))
                      file_count += 1
              else:
                  # Insert new file
                  c.execute('INSERT INTO files (filename, filepath, modified_time) VALUES (?, ?, ?)',
                            (name.lower(), filepath, modified_time))
                  file_count += 1
          except Exception as e:
              # Handle any exceptions (e.g., permission errors)
              continue

      # Commit periodically to reduce memory usage
      if file_count >= 1000:
          conn.commit()
          file_count = 0

  # Remove deleted files from the database
  c.execute('SELECT filepath FROM files')
  all_indexed_files = set(row[0] for row in c.fetchall())
  deleted_files = all_indexed_files - current_files

  if deleted_files:
      c.executemany('DELETE FROM files WHERE filepath = ?', [(fp,) for fp in deleted_files])
      file_count += len(deleted_files)

  conn.commit()
  conn.close()
  end_time = time.time()
  if complete_callback:
      complete_callback(end_time - start_time, len(current_files))

# Function to build the initial index (run in a separate thread)
def build_initial_index(update_callback, complete_callback):
  index_files(update_callback=update_callback, complete_callback=complete_callback)

# Function to search the indexed files
def search_files(query):
  conn = sqlite3.connect('file_index.db')
  c = conn.cursor()
  search_query = f'%{query.lower()}%'
  c.execute('SELECT filename, filepath FROM files WHERE filename LIKE ? LIMIT 1000', (search_query,))
  results = c.fetchall()
  conn.close()
  return results

# Function to open the containing folder and select the file
def open_containing_folder(filepath):
  folder = os.path.dirname(filepath)
  if os.path.exists(folder):
      try:
          # Open the containing folder and select the file
          subprocess.run(['explorer', '/select,', filepath])
      except Exception as e:
          messagebox.showerror("Error", f"Cannot open file: {e}")
  else:
      messagebox.showerror("Error", f"Folder does not exist:\n{folder}")

# GUI Application
class FileSearchApp(tk.Tk):
  def __init__(self):
      super().__init__()
      self.title("File Search Tool")
      self.geometry("900x700")
      self.create_widgets()
      self.check_and_start_indexing()

  def create_widgets(self):
      # Top Frame for Search and Refresh
      top_frame = ttk.Frame(self)
      top_frame.pack(pady=10, padx=10, fill=tk.X)

      # Search Entry
      self.search_var = tk.StringVar()
      self.search_var.trace('w', self.update_search)
      self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=80)
      self.search_entry.pack(side=tk.LEFT, padx=(0,10), fill=tk.X, expand=True)
      self.search_entry.focus()

      # Refresh Button
      self.refresh_button = ttk.Button(top_frame, text="Refresh Index", command=self.refresh_index)
      self.refresh_button.pack(side=tk.RIGHT)

      # Results Listbox with Scrollbar
      results_frame = ttk.Frame(self)
      results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

      self.results_scrollbar = ttk.Scrollbar(results_frame)
      self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

      self.results_listbox = tk.Listbox(results_frame, yscrollcommand=self.results_scrollbar.set)
      self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
      self.results_scrollbar.config(command=self.results_listbox.yview)
      self.results_listbox.bind('<Double-Button-1>', self.open_selected_folder)

      # Status Bar
      self.status_var = tk.StringVar()
      self.status_label = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
      self.status_label.pack(pady=5, padx=5, fill=tk.X, side=tk.BOTTOM)

  def check_and_start_indexing(self):
      if not os.path.exists('file_index.db'):
          self.start_indexing()
      else:
          # Optionally, you can implement checks to see if the index is up-to-date
          self.status_var.set("Index loaded. Ready to search.")
          self.update_search()

  def start_indexing(self):
      self.refresh_button.config(state=tk.DISABLED)
      self.status_var.set("Indexing files on C:\\ drive...")
      self.indexing_thread = threading.Thread(target=build_initial_index, args=(self.update_status, self.indexing_complete))
      self.indexing_thread.daemon = True
      self.indexing_thread.start()

  def refresh_index(self):
      confirm = messagebox.askyesno("Refresh Index", "Refreshing the index may take some time. Continue?")
      if confirm:
          self.start_indexing()

  def update_status(self, current_directory):
      self.status_var.set(f"Indexing: {current_directory}")

  def indexing_complete(self, elapsed_time, total_files):
      self.status_var.set(f"Indexing completed in {elapsed_time:.2f} seconds. Indexed {total_files} files.")
      self.refresh_button.config(state=tk.NORMAL)
      self.update_search()

  def update_search(self, *args):
      query = self.search_var.get()
      if not query.strip():
          self.results_listbox.delete(0, tk.END)
          return

      # To keep the UI responsive, perform search in a separate thread
      threading.Thread(target=self.perform_search, args=(query,)).start()

  def perform_search(self, query):
      results = search_files(query)
      self.results_listbox.delete(0, tk.END)
      for filename, filepath in results:
          display_text = f"{filename} | {filepath}"
          self.results_listbox.insert(tk.END, display_text)

  def open_selected_folder(self, event):
      selection = self.results_listbox.curselection()
      if selection:
          index = selection[0]
          item = self.results_listbox.get(index)
          try:
              filepath = item.split('|', 1)[1].strip()
              open_containing_folder(filepath)
          except IndexError:
              messagebox.showerror("Error", "Invalid selection.")

if __name__ == "__main__":
  # Check if the script is running on Windows
  if sys.platform != "win32":
      messagebox.showerror("Unsupported OS", "This tool is only supported on Windows.")
      sys.exit(1)

  app = FileSearchApp()
  app.mainloop()
