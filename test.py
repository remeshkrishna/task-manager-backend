import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("taskmanager.db")

# Enable foreign keys (just in case)
conn.execute("PRAGMA foreign_keys = ON;")

# Execute the PRAGMA command
cursor = conn.execute("PRAGMA foreign_key_list(tasktable);")

# Print the result
foreign_keys = cursor.fetchall()
print("Foreign Keys in Task Table:", foreign_keys)

# Close connection
conn.close()
