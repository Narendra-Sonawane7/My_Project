#!/usr/bin/env python3
"""
SEEU Database Migration Script
================================
This script converts your SQLite database (SEEU.db) to JSON format (SEEU.json)
while preserving ALL your data - conversations, memories, preferences, etc.

HOW TO USE:
1. Place this script in your SEEU project root folder
2. Run: python migrate_seeu_db.py
3. Follow the on-screen instructions

WHAT IT DOES:
- Reads all data from Database/SEEU.db
- Converts it to JSON format
- Saves to Database/SEEU.json
- Creates a backup of your SQLite database
- Preserves all conversations, memories, and settings

SAFE TO RUN:
- Your original SEEU.db will NOT be deleted
- A backup (.backup) is automatically created
- You can switch back if needed
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime

class DatabaseMigrator:
    """Handles migration from SQLite to JSON"""

    def __init__(self):
        self.sqlite_path = 'Database/SEEU.db'
        self.json_path = 'Database/SEEU.json'
        self.backup_path = 'Database/SEEU.db.backup'

    def check_files(self):
        """Check if required files exist"""
        print("🔍 Checking files...")

        # Check if Database directory exists
        if not os.path.exists('Database'):
            print("❌ Database folder not found!")
            print("   Please run this script from your SEEU project root folder")
            return False

        # Check if SQLite database exists
        if not os.path.exists(self.sqlite_path):
            print(f"❌ SQLite database not found at: {self.sqlite_path}")
            print("   Make sure SEEU.db is in the Database folder")
            return False

        # Check if JSON already exists
        if os.path.exists(self.json_path):
            print(f"⚠️  JSON database already exists at: {self.json_path}")
            response = input("   Do you want to overwrite it? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("   Migration cancelled.")
                return False

        print("✅ All checks passed!")
        return True

    def create_backup(self):
        """Create backup of SQLite database"""
        print(f"\n🔒 Creating backup...")
        try:
            shutil.copy2(self.sqlite_path, self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False

    def migrate_data(self):
        """Migrate all data from SQLite to JSON"""
        print("\n🔄 Starting migration...")
        print("="*60)

        try:
            # Connect to SQLite
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            # Initialize JSON structure
            json_data = {
                'conversations': [],
                'long_term_memory': [],
                'user_preferences': [],
                'sessions': [],
                'response_cache': [],
                'metadata': {
                    'version': '1.0',
                    'migrated_from': 'SQLite',
                    'migration_date': datetime.now().isoformat(),
                    'created': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat()
                }
            }

            # Migrate conversations
            print("\n📋 Migrating conversations...")
            try:
                cursor.execute("""
                    SELECT id, user_message, assistant_response, timestamp, session_id, category
                    FROM conversations ORDER BY id
                """)
                for row in cursor.fetchall():
                    json_data['conversations'].append({
                        'id': row[0],
                        'user_message': row[1],
                        'assistant_response': row[2],
                        'timestamp': row[3],
                        'session_id': row[4],
                        'category': row[5]
                    })
                print(f"   ✅ Migrated {len(json_data['conversations'])} conversations")
            except sqlite3.Error as e:
                print(f"   ⚠️  Error migrating conversations: {e}")

            # Migrate long_term_memory
            print("\n🧠 Migrating long-term memories...")
            try:
                cursor.execute("""
                    SELECT id, memory_type, content, keywords, importance,
                           timestamp, last_accessed, access_count
                    FROM long_term_memory ORDER BY id
                """)
                for row in cursor.fetchall():
                    json_data['long_term_memory'].append({
                        'id': row[0],
                        'memory_type': row[1],
                        'content': row[2],
                        'keywords': row[3],
                        'importance': row[4],
                        'timestamp': row[5],
                        'last_accessed': row[6],
                        'access_count': row[7]
                    })
                print(f"   ✅ Migrated {len(json_data['long_term_memory'])} memories")
            except sqlite3.Error as e:
                print(f"   ⚠️  Error migrating memories: {e}")

            # Migrate user_preferences
            print("\n⚙️  Migrating user preferences...")
            try:
                cursor.execute("""
                    SELECT id, preference_key, preference_value, timestamp
                    FROM user_preferences ORDER BY id
                """)
                for row in cursor.fetchall():
                    json_data['user_preferences'].append({
                        'id': row[0],
                        'preference_key': row[1],
                        'preference_value': row[2],
                        'timestamp': row[3]
                    })
                print(f"   ✅ Migrated {len(json_data['user_preferences'])} preferences")
            except sqlite3.Error as e:
                print(f"   ⚠️  Error migrating preferences: {e}")

            # Migrate sessions
            print("\n📁 Migrating sessions...")
            try:
                cursor.execute("""
                    SELECT session_id, start_time, end_time, message_count
                    FROM sessions ORDER BY start_time
                """)
                for row in cursor.fetchall():
                    json_data['sessions'].append({
                        'session_id': row[0],
                        'start_time': row[1],
                        'end_time': row[2],
                        'message_count': row[3]
                    })
                print(f"   ✅ Migrated {len(json_data['sessions'])} sessions")
            except sqlite3.Error as e:
                print(f"   ⚠️  Error migrating sessions: {e}")

            # Migrate response_cache
            print("\n💾 Migrating response cache...")
            try:
                cursor.execute("""
                    SELECT id, query_hash, response, timestamp
                    FROM response_cache ORDER BY id
                """)
                for row in cursor.fetchall():
                    json_data['response_cache'].append({
                        'id': row[0],
                        'query_hash': row[1],
                        'response': row[2],
                        'timestamp': row[3]
                    })
                print(f"   ✅ Migrated {len(json_data['response_cache'])} cache entries")
            except sqlite3.Error as e:
                print(f"   ⚠️  Error migrating cache: {e}")

            # Close SQLite connection
            conn.close()

            # Write JSON file
            print(f"\n💾 Writing JSON database to: {self.json_path}")
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

            # Verify JSON file
            if os.path.exists(self.json_path):
                file_size = os.path.getsize(self.json_path)
                print(f"   ✅ JSON database created successfully ({file_size:,} bytes)")

            # Return statistics
            return json_data

        except Exception as e:
            print(f"\n❌ Migration Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def print_summary(self, json_data):
        """Print migration summary"""
        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📊 Migration Summary:")
        print(f"   • Conversations:    {len(json_data['conversations'])}")
        print(f"   • Memories:         {len(json_data['long_term_memory'])}")
        print(f"   • Preferences:      {len(json_data['user_preferences'])}")
        print(f"   • Sessions:         {len(json_data['sessions'])}")
        print(f"   • Cache Entries:    {len(json_data['response_cache'])}")

        print(f"\n📁 Files Created:")
        print(f"   • New JSON DB:      {self.json_path}")
        print(f"   • SQLite Backup:    {self.backup_path}")
        print(f"   • Original DB:      {self.sqlite_path} (unchanged)")

        print(f"\n🎯 Next Steps:")
        print(f"   1. Replace Backend/Brain.py with the new JSON-based version")
        print(f"   2. Restart SEEU - it will automatically use {self.json_path}")
        print(f"   3. Test that SEEU remembers all your data")
        print(f"   4. Once confirmed working, you can delete {self.sqlite_path}")

        print("\n" + "="*60)

    def run(self):
        """Run the complete migration process"""
        print("\n" + "="*60)
        print("🦅 SEEU Database Migration Tool")
        print("="*60)
        print("This will convert your SQLite database to JSON format")
        print("Your existing data will be preserved and backed up")
        print("="*60 + "\n")

        # Step 1: Check files
        if not self.check_files():
            return False

        # Step 2: Create backup
        if not self.create_backup():
            return False

        # Step 3: Migrate data
        json_data = self.migrate_data()
        if not json_data:
            return False

        # Step 4: Print summary
        self.print_summary(json_data)

        return True


def main():
    """Main entry point"""
    migrator = DatabaseMigrator()
    success = migrator.run()

    if success:
        print("\n✅ Migration completed successfully!")
        print("💡 You can now use SEEU with JSON storage.")
        print("📝 Don't forget to replace Brain.py with the JSON version!\n")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        print("💡 Your original database is safe and unchanged.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()