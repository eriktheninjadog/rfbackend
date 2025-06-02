import re
import os

#booktools.py

from explaintext_in_simple_cantonese import just_render_text
from newscrawler import render_from_chinese_to_audio_and_upload
import openrouter



def summarize_novel(file_path):
    if not os.path.exists(file_path+".summary"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        summary_file_path = file_path + ".summary"
        api = openrouter.OpenRouterAPI()
        summary = api.open_router_ai21_jamba_1_6_large("Summarize this text in 2000 characters or less:\n" + content)
        # Split the content into paragraphs
        with open(summary_file_path, 'w', encoding='utf-8') as f:
            f.write(summary)        
        print(f"Summary saved to {summary_file_path}")
    
    sumamry_file = open(file_path+".summary", 'r', encoding='utf-8')
    summary = sumamry_file.read()
    sumamry_file.close()
    # Print the summary
    print("Summary of the book:")
    print(summary)        
    return summary

def split_book_into_chapters(file_path, output_dir=None):
    """
    Split a book file into separate chapter files.
    
    Args:
        file_path (str): Path to the book file
        output_dir (str, optional): Directory to save chapter files. If None, uses the same directory as the book.
    
    Returns:
        list: List of paths to the created chapter files
    """
    
    summary = summarize_novel(file_path)
    # Read the book content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define different patterns for chapter detection
    chapter_patterns = [
                r'(?:\n|\r\n)\d+[\s\n\r]',  # "1" format

                r'(?:\n|\r\n)\d+\.[\s\n\r]',  # "1." format
        r'\n\s*\n[A-Z ]+\n\s*\n',  # Empty line, capital letters and spaces only, empty line
        r'\n[A-Z| ]+\n',  # Two empty lines, capital word, two empty lines
        r'(?:\n|\r\n)(?:Chapter|CHAPTER) \d+[\s\n\r]',  # "Chapter X" format
        r'(?:\n|\r\n)(?:Chapter|CHAPTER) [A-Z]+[\s\n\r]',  # "Chapter ABC" format
        r'(?:\n|\r\n)(?:第)[\u4e00-\u9fff]+(?:章)[\s\n\r]',  # Chinese "第X章" format
        r'(?:\n|\r\n)(?:BOOK|Book) \d+[\s\n\r]',  # "Book X" format
        r'(?:\n|\r\n)(?:PART|Part) \d+[\s\n\r]',  # "Part X" format
        r'(?:\n|\r\n)(?:\* \* \*|\-\-\-\-\-|\* \* \* \* \*)[\s\n\r]',  # Common separators
    ]
    
    # Try each pattern until we find one that gives good results
    chapters = []
    for pattern in chapter_patterns:
        # Find all matches
        matches = list(re.finditer(pattern, content))
        
        # If we found a reasonable number of chapters, use this pattern
        if len(matches) > 1 and len(matches) < 200:  # Arbitrary thresholds
            print(f"Using pattern: {pattern} - Found {len(matches)} chapters")
            
            # Get the start positions of each chapter
            start_positions = [match.start() for match in matches]
            start_positions.append(len(content))  # Add the end of the file
            
            # Extract each chapter
            for i in range(len(matches)):
                chapter_title = content[matches[i].start():matches[i].end()].strip()
                chapter_content = content[start_positions[i]:start_positions[i+1]]
                chapters.append((chapter_title, chapter_content))
            
            break
    
    # If no pattern worked well, try a fallback: just split into equal parts
    if not chapters:
        print("No good chapter pattern found. Falling back to equal parts.")
        # Split into 10 equal parts as a fallback
        chunk_size = len(content) // 10
        for i in range(10):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < 9 else len(content)
            chapters.append((f"Part {i+1}", content[start:end]))
    
    # Save chapters to files
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    chapter_files = []
    book_name = os.path.splitext(os.path.basename(file_path))[0]
    
    for i, (title, content) in enumerate(chapters):
        # Clean up title for filename use
        clean_title = re.sub(r'[^\w\s-]', '', title).strip()
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
            
        # Create filename
        filename = f"{book_name}_chapter_{i+1:03d}.txt"
        if clean_title:
            filename = f"{book_name}_chapter_{i+1:03d}_{clean_title}.txt"
        
        file_path = os.path.join(output_dir, filename)
        
        # Write chapte  r to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        chaptersummary_file_path = file_path + ".summary"
        if os.path.exists(chaptersummary_file_path):
            with open(chaptersummary_file_path, 'r', encoding='utf-8') as f:
                chaptersummary = f.read()
            print(f"Existing summary found for chapter {i+1}")
        else:
            api = openrouter.OpenRouterAPI()
            chaptersummary = api.open_router_claude_3_7_sonnet(system_content="You are a cantonese expert, helping with translating book chapters of written english to spoken Cantonese. Only respond using Cantonese written with Traditional Chinese. No Jyutping. Here is a summary of the book:\n"+summary,text="Translate chapter spoken Cantonese spoken daily in Hong Kong:\n" + content )
            chaptersummary_file_path = file_path + ".summary"
            with open(chaptersummary_file_path, 'w', encoding='utf-8') as f:
                f.write(chaptersummary)
            print(f"Chapter {i+1} saved to {file_path}")
            just_render_text(chaptersummary, "giver_" + str(i)+".mp3")
        print(f"Chapter {i+1} summary saved to {chaptersummary_file_path}")        
        chapter_files.append(file_path)
    
    return chapter_files


if __name__ == "__main__":
    split_book_into_chapters("/home/erik/Downloads/thegiver.txt")