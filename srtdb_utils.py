import os
import re
import subprocess
from pathlib import Path

def parse_srt(file_path: str):
    """Efficiently parse SRT files with tolerance for variations"""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    blocks = []
    pattern = re.compile(
        r'(\d+)\s*\n(\d{1,2}:\d{2}:\d{2}[\.,]\d{3})\s*[-~—>]+\s*(\d{1,2}:\d{2}:\d{2}[\.,]\d{3})\n([\s\S]*?)(?=\n\n\d|\Z)',
        re.MULTILINE
    )
    
    for match in pattern.finditer(content):
        idx = match.group(1).strip()
        start = match.group(2).replace(',', '.').strip()
        end = match.group(3).replace(',', '.').strip()
        text = re.sub(r'\n+', ' ', match.group(4)).strip()
        blocks.append({
            "file": os.path.basename(file_path),
            "path": file_path,
            "index": idx,
            "start": start,
            "end": end,
            "text": text
        })
    return blocks

def fast_search(directory: str, keywords: list, match_type='any'):
    """Find blocks containing keywords with configurable matching"""
    valid_files = [f for f in os.listdir(directory) if f.lower().endswith('.srt')]
    all_blocks = []
    keywords = [k.lower() for k in keywords]
    matcher = any if match_type == 'any' else all
    
    for file in valid_files:
        file_path = os.path.join(directory, file)
        blocks = parse_srt(file_path)
        for block in blocks:
            text_lower = block["text"].lower()
            if matcher(kw in text_lower for kw in keywords):
                all_blocks.append(block)
    return all_blocks

def setup_srt_directory(directory: str):
    """Create directory and download SRT files if needed"""
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        
        if not any(path.glob('*.srt')):
            print(f"⏳ No SRT files found. Downloading from server...")
            cmd = [
                'scp', 
                'storage.eriktamm.com:/home/erik/srt_archive/*.srt',
                f'{directory}/'
            ]
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded .srt files to {directory}")
        return True
    except Exception as e:
        print(f"🚨 Error setting up directory: {e}")
        return False
