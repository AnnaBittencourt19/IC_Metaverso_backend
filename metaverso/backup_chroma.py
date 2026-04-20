#!/usr/bin/env python3
"""
Script to prepare and backup ChromaDB for Render deployment
This exports the local ChromaDB so it can be uploaded to Render disk
"""

import os
import shutil
import json
from datetime import datetime

LOCAL_CHROMA_PATH = "./chroma_db_export"
BACKUP_DIR = "./chroma_backup"

def backup_chroma():
    """Backup ChromaDB to a directory that can be uploaded"""
    print(f"📦 Backing up ChromaDB from {LOCAL_CHROMA_PATH}...")
    
    if not os.path.exists(LOCAL_CHROMA_PATH):
        print(f"❌ Error: {LOCAL_CHROMA_PATH} not found!")
        return False
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"chroma_{timestamp}")
    
    try:
        # Copy entire directory
        shutil.copytree(LOCAL_CHROMA_PATH, backup_path, dirs_exist_ok=True)
        print(f"✅ ChromaDB backed up to {backup_path}")
        
        # Create info file
        info = {
            "timestamp": timestamp,
            "source": LOCAL_CHROMA_PATH,
            "destination_render": "/var/data/chroma",
            "instructions": "Upload contents of this directory to Render persistent disk at /var/data/chroma"
        }
        
        with open(os.path.join(backup_path, "BACKUP_INFO.json"), "w") as f:
            json.dump(info, f, indent=2)
        
        print(f"📝 Backup info saved to {os.path.join(backup_path, 'BACKUP_INFO.json')}")
        return True
        
    except Exception as e:
        print(f"❌ Error during backup: {e}")
        return False

if __name__ == "__main__":
    success = backup_chroma()
    exit(0 if success else 1)
