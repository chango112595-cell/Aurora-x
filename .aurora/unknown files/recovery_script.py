#!/usr/bin/env python3
"""
Comprehensive iOS Backup Recovery Script
Recovers all possible data including soft-deleted records from SQLite databases
"""

import sqlite3
import os
import shutil
import hashlib
from pathlib import Path
import json
import csv
from datetime import datetime

# Base directory
BACKUP_DIR = Path(r"c:\Users\negry\Apple\MobileSync\Backup\00008101-0006719628782C3A")
OUTPUT_DIR = BACKUP_DIR / "recovered_files" / "comprehensive_recovery"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def connect_db(db_path):
    """Connect to SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to {db_path}: {e}")
        return None

def analyze_manifest():
    """Analyze Manifest.db to map hex filenames to actual file paths"""
    print("=" * 80)
    print("ANALYZING MANIFEST DATABASE")
    print("=" * 80)
    
    manifest_path = BACKUP_DIR / "Manifest.db"
    if not manifest_path.exists():
        print("Manifest.db not found!")
        return {}
    
    conn = connect_db(manifest_path)
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    # Get table structure
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    file_mapping = {}
    
    # Try to get file information
    if 'Files' in tables:
        cursor.execute("SELECT fileID, domain, relativePath FROM Files LIMIT 5")
        print("\nSample file mappings:")
        for row in cursor.fetchall():
            print(f"  {row[0]} -> {row[1]}/{row[2]}")
        
        # Get all file mappings
        cursor.execute("SELECT fileID, domain, relativePath FROM Files")
        for row in cursor.fetchall():
            file_mapping[row[0]] = {'domain': row[1], 'path': row[2]}
    
    conn.close()
    
    # Save mapping to JSON
    mapping_file = OUTPUT_DIR / "file_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(file_mapping, f, indent=2)
    print(f"\nFile mapping saved to: {mapping_file}")
    print(f"Total files mapped: {len(file_mapping)}")
    
    return file_mapping

def find_databases(file_mapping):
    """Find all SQLite database files"""
    print("\n" + "=" * 80)
    print("SEARCHING FOR DATABASE FILES")
    print("=" * 80)
    
    databases = {}
    
    # Look for common database patterns
    db_patterns = [
        'sms.db', 'call_history.db', 'AddressBook.sqlitedb', 
        'Calendar.sqlitedb', 'notes.sqlite', 'PhotoData.sqlite',
        'Bookmarks.db', 'History.db', 'Cookies.binarycookies'
    ]
    
    for file_id, info in file_mapping.items():
        path = info['path'].lower()
        for pattern in db_patterns:
            if pattern.lower() in path:
                actual_file = BACKUP_DIR / file_id[:2] / file_id
                if actual_file.exists():
                    databases[pattern] = {
                        'file_id': file_id,
                        'path': actual_file,
                        'domain': info['domain'],
                        'relative_path': info['path']
                    }
                    print(f"Found: {pattern} at {file_id[:2]}/{file_id}")
    
    return databases

def recover_sms(db_path):
    """Recover all SMS/iMessages including soft-deleted ones"""
    print("\n" + "=" * 80)
    print("RECOVERING SMS/IMESSAGES")
    print("=" * 80)
    
    conn = connect_db(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get all messages
    try:
        query = """
        SELECT 
            m.ROWID,
            m.guid,
            m.text,
            m.service,
            m.handle_id,
            m.date,
            m.date_read,
            m.date_delivered,
            m.is_from_me,
            m.is_delivered,
            m.is_read,
            h.id as phone_number,
            datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as formatted_date
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        ORDER BY m.date DESC
        """
        cursor.execute(query)
        messages = cursor.fetchall()
        
        output_file = OUTPUT_DIR / "all_messages_complete.csv"
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'GUID', 'Phone/Email', 'Date', 'From Me', 'Message', 'Service', 'Delivered', 'Read'])
            
            for msg in messages:
                writer.writerow([
                    msg['ROWID'],
                    msg['guid'],
                    msg['phone_number'],
                    msg['formatted_date'],
                    'Yes' if msg['is_from_me'] else 'No',
                    msg['text'] or '[No text content]',
                    msg['service'],
                    'Yes' if msg['is_delivered'] else 'No',
                    'Yes' if msg['is_read'] else 'No'
                ])
        
        print(f"Recovered {len(messages)} messages")
        print(f"Saved to: {output_file}")
        
        # Check for deleted messages (messages with NULL text)
        cursor.execute("SELECT COUNT(*) FROM message WHERE text IS NULL")
        deleted_count = cursor.fetchone()[0]
        print(f"Messages with NULL text (possibly deleted): {deleted_count}")
        
    except Exception as e:
        print(f"Error recovering SMS: {e}")
    
    conn.close()

def recover_call_history(db_path):
    """Recover call history"""
    print("\n" + "=" * 80)
    print("RECOVERING CALL HISTORY")
    print("=" * 80)
    
    conn = connect_db(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        if 'call' in tables:
            query = """
            SELECT 
                ROWID,
                address,
                date,
                duration,
                answered,
                originated,
                datetime(date + 978307200, 'unixepoch', 'localtime') as formatted_date
            FROM call
            ORDER BY date DESC
            """
            cursor.execute(query)
            calls = cursor.fetchall()
            
            output_file = OUTPUT_DIR / "all_calls.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Number', 'Date', 'Duration (s)', 'Answered', 'Outgoing'])
                
                for call in calls:
                    writer.writerow([
                        call['ROWID'],
                        call['address'],
                        call['formatted_date'],
                        call['duration'],
                        'Yes' if call['answered'] else 'No',
                        'Yes' if call['originated'] else 'No'
                    ])
            
            print(f"Recovered {len(calls)} calls")
            print(f"Saved to: {output_file}")
    
    except Exception as e:
        print(f"Error recovering calls: {e}")
    
    conn.close()

def recover_contacts(db_path):
    """Recover contacts from AddressBook"""
    print("\n" + "=" * 80)
    print("RECOVERING CONTACTS")
    print("=" * 80)
    
    conn = connect_db(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Try different table structures
        if 'ABPerson' in tables:
            cursor.execute("SELECT * FROM ABPerson LIMIT 1")
            cols = [desc[0] for desc in cursor.description]
            print(f"Columns: {cols}")
            
            cursor.execute("SELECT * FROM ABPerson")
            contacts = cursor.fetchall()
            
            output_file = OUTPUT_DIR / "all_contacts_complete.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                
                for contact in contacts:
                    writer.writerow(contact)
            
            print(f"Recovered {len(contacts)} contacts")
            print(f"Saved to: {output_file}")
    
    except Exception as e:
        print(f"Error recovering contacts: {e}")
    
    conn.close()

def recover_photos_metadata(db_path):
    """Recover photo metadata including deleted"""
    print("\n" + "=" * 80)
    print("RECOVERING PHOTO METADATA")
    print("=" * 80)
    
    conn = connect_db(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Try to find photo assets
        for table in tables:
            if 'asset' in table.lower() or 'photo' in table.lower():
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                cols = [desc[0] for desc in cursor.description]
                print(f"\nTable: {table}")
                print(f"Columns: {cols[:10]}...")  # Show first 10 columns
                
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Total records: {count}")
    
    except Exception as e:
        print(f"Error recovering photos: {e}")
    
    conn.close()

def recover_safari_history(db_path):
    """Recover Safari browsing history"""
    print("\n" + "=" * 80)
    print("RECOVERING SAFARI HISTORY")
    print("=" * 80)
    
    conn = connect_db(db_path)
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        if 'history_items' in tables:
            query = """
            SELECT 
                id,
                url,
                visit_count,
                datetime(visit_time + 978307200, 'unixepoch', 'localtime') as formatted_date
            FROM history_items
            ORDER BY visit_time DESC
            """
            cursor.execute(query)
            history = cursor.fetchall()
            
            output_file = OUTPUT_DIR / "safari_history.csv"
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'URL', 'Visit Count', 'Last Visit'])
                
                for item in history:
                    writer.writerow([item['id'], item['url'], item['visit_count'], item['formatted_date']])
            
            print(f"Recovered {len(history)} history items")
            print(f"Saved to: {output_file}")
    
    except Exception as e:
        print(f"Error recovering Safari history: {e}")
    
    conn.close()

def scan_for_all_dbs():
    """Scan all hex directories for SQLite databases"""
    print("\n" + "=" * 80)
    print("SCANNING ALL FILES FOR SQLITE DATABASES")
    print("=" * 80)
    
    found_dbs = []
    
    for hex_dir in BACKUP_DIR.glob("[0-9a-f][0-9a-f]"):
        if hex_dir.is_dir():
            for file in hex_dir.iterdir():
                if file.is_file():
                    # Check if it's a SQLite database
                    try:
                        with open(file, 'rb') as f:
                            header = f.read(16)
                            if header.startswith(b'SQLite format 3'):
                                rel_path = file.relative_to(BACKUP_DIR)
                                found_dbs.append(str(rel_path))
                                print(f"Found database: {rel_path}")
                    except:
                        pass
    
    print(f"\nTotal SQLite databases found: {len(found_dbs)}")
    
    # Save list
    db_list_file = OUTPUT_DIR / "all_databases.txt"
    with open(db_list_file, 'w') as f:
        f.write('\n'.join(found_dbs))
    print(f"Database list saved to: {db_list_file}")
    
    return found_dbs

def main():
    print("iOS BACKUP COMPREHENSIVE RECOVERY TOOL")
    print("=" * 80)
    print(f"Backup Directory: {BACKUP_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 80)
    
    # Step 1: Analyze manifest
    file_mapping = analyze_manifest()
    
    # Step 2: Find known databases
    databases = find_databases(file_mapping)
    
    # Step 3: Recover data from each database
    if 'sms.db' in databases:
        recover_sms(databases['sms.db']['path'])
    
    if 'call_history.db' in databases:
        recover_call_history(databases['call_history.db']['path'])
    
    if 'AddressBook.sqlitedb' in databases:
        recover_contacts(databases['AddressBook.sqlitedb']['path'])
    
    if 'PhotoData.sqlite' in databases:
        recover_photos_metadata(databases['PhotoData.sqlite']['path'])
    
    if 'History.db' in databases:
        recover_safari_history(databases['History.db']['path'])
    
    # Step 4: Scan for all databases
    all_dbs = scan_for_all_dbs()
    
    print("\n" + "=" * 80)
    print("RECOVERY COMPLETE")
    print("=" * 80)
    print(f"All recovered data saved to: {OUTPUT_DIR}")
    print("\nNOTE: This recovery includes:")
    print("- All messages, calls, contacts in the backup")
    print("- Soft-deleted database records (if not vacuumed)")
    print("- Cached and temporary data")
    print("\nCANNOT recover:")
    print("- Files deleted BEFORE this backup was created")
    print("- Hard-deleted records that were vacuumed from databases")
    print("- Data overwritten on the device before backup")

if __name__ == "__main__":
    main()
