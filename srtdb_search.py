import argparse
import os
import json
from srtdb_utils import fast_search, setup_srt_directory
from srtdb_openrouter import  llm_match,OpenRouterClient

# Common grammatical patterns mapping
COMMON_PATTERNS = {
    "first": "首先",
    "slowly_verb": "慢慢 + [動詞]",
    "how_to": "點樣 + [動詞]",
    "negative_action": "唔好 + [動詞]",
    "future_tense": "會 + [動詞]"
}

def parse_pattern(input_pattern: str):
    """Translate natural language patterns to Cantonese descriptions"""
    if input_pattern in COMMON_PATTERNS:
        return COMMON_PATTERNS[input_pattern]
    return input_pattern

import random
import subprocess


def make_mp3_from_search(keywords,pattern,result):
    filename = "srt_search_"+keywords[0]+"_"+pattern+".json"
    filename = filename.replace(' ','_')
    with open(filename, 'w') as f:
        json.dump(result, f)    
    # Construct the remote destination
    remote_destination = f"erik@storage.eriktamm.com:/home/erik/make_mp3/{filename}"
    print(f"Uploading search results to {remote_destination}")

    # Execute SCP command to upload the file
    try:
        result = subprocess.run(
            ["scp", filename, remote_destination],
            check=True,
            text=True,
            capture_output=True
        )
        print(f"Upload successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Upload failed: {e.stderr}")
    # Code to generate MP3 from result
    return filename

def search_srt_files(directory="/var/srt_archive/", keywords=None, pattern=None, match='any', batch_size=5, max_nr = 10,model="anthropic/claude-3.7-sonnet"):
        """
        Search SRT files for keywords and/or grammatical patterns
        
        Args:
            directory (str): Path to SRT files directory
            keywords (list): Keywords for direct search
            pattern (str): Grammatical pattern requiring LLM processing
            match (str): Keyword matching strategy ('any' or 'all')
            batch_size (int): LLM batch size for processing
            model (str): OpenRouter model to use
            
        Returns:
            list: List of matching blocks
        """
        
        # Keyword search (no LLM)
        if keywords and not pattern:
            print("just doing a simple search  "+ str(directory) + " " + str(keywords) + " " + match)
            result = fast_search(directory, keywords, match)
            if len(result) > max_nr:
                result =  random.sample(result, max_nr)
                make_mp3_from_search(keywords, pattern, result)
                return result
            make_mp3_from_search(keywords, pattern, result)
            return result

        # LLM-assisted pattern search
        candidates = fast_search(directory, keywords or [""], 'any') if keywords else []
        
        print(f"⚡ Found {len(candidates)} candidate blocks")
        print(f"🧠 Using {model} to match: '{pattern}'...")
        
        results = []
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i+batch_size]
            print(f"   Processing batch {(i//batch_size)+1}/{len(candidates)//batch_size + 1}")
            
            for block in batch:
                if llm_match( block['text'], pattern, model):
                    results.append(block)
                    if len(results) >= max_nr:
                        make_mp3_from_search(keywords, pattern, result)
                        return results        
        make_mp3_from_search(keywords, pattern, result)
        return results

def main():
    parser = argparse.ArgumentParser(
        description="Search Cantonese SRT files",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("directory", help="Path to SRT files directory")
    parser.add_argument("-k", "--keywords", nargs='+', 
                        help="Keywords for direct search (no LLM)")
    parser.add_argument("-p", "--pattern", 
                        help="Grammatical pattern requiring LLM processing\n" \
                             "Examples:\n" \
                             "  --pattern first\n" \
                             "  --pattern '慢慢 + [動詞]'")
    parser.add_argument("-m", "--match", choices=['any', 'all'], default='any',
                        help="Keyword matching: 'any' or 'all' (default: any)")
    parser.add_argument("-b", "--batch", type=int, default=5,
                        help="LLM batch size (default: 5)")
    parser.add_argument("--model", default="anthropic/claude-3.7-sonnet",
                        help="OpenRouter model (default: anthropic/claude-3.7-sonnet)")
    parser.add_argument("--list-patterns", action="store_true",
                        help="Show common grammatical patterns")
    
    args = parser.parse_args()
    
    if args.list_patterns:
        print("🧩 Common grammatical patterns:")
        for k, v in COMMON_PATTERNS.items():
            print(f"- {k}: {v}")
        return
    
    if not setup_srt_directory(args.directory):
        return
    
    # Parse pattern if provided
    pattern = parse_pattern(args.pattern) if args.pattern else None
    
    # Keyword search (no LLM)
    if args.keywords and not args.pattern:
        results = fast_search(args.directory, args.keywords, args.match)
        print(f"🔍 Found {len(results)} matches:")
        for i, block in enumerate(results, 1):
            print(f"\n📍 Match {i} [{block['file']}] ({block['start']} - {block['end']}):")
            print(f"   {block['text']}")
        return
    
    # LLM-assisted pattern search
    candidates = fast_search(args.directory, args.keywords or [""], 'any') if args.keywords else []
    
    print(f"⚡ Found {len(candidates)} candidate blocks")
    print(f"🧠 Using {args.model} to match: '{pattern}'...")
    
    results = []
    for i in range(0, len(candidates), args.batch):
        batch = candidates[i:i+args.batch]
        print(f"   Processing batch {(i//args.batch)+1}/{len(candidates)//args.batch + 1}")
        
        for block in batch:
            if llm_match(block['text'], pattern, args.model):
                results.append(block)
    
    # Output final results
    if not results:
        print("\n❌ No matching blocks found")
        return
    
    print(f"\n🎯 Found {len(results)} pattern matches:")
    for block in results:
        print(f"\n📄 {block['file']} [{block['start']} - {block['end']}]")
        print(f"   {block['text']}")
        print(f"   Path: {block['path']}")

if __name__ == "__main__":
    main()
