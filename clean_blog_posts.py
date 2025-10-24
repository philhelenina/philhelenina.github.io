#!/usr/bin/env python3
"""
Clean up blog post titles and formatting
- Remove category tags from titles
- Remove excessive HTML formatting (bold, italics, quotes) while preserving images
- Maintain category metadata
"""

import os
import re
from pathlib import Path

def clean_title(title):
    """Remove category tags from title"""
    # Remove patterns like [Paper Review - NLP], [Book Summary, NLP], etc.
    cleaned = re.sub(r'^\[.*?\]\s*', '', title)
    return cleaned.strip()

def clean_html_formatting(content):
    """Remove excessive formatting but preserve images, links, and structure"""
    # Don't touch img tags, figure tags
    # Remove <strong>, <em>, <b>, <i> tags but keep content

    # Skip if content has images - we'll be more careful with those
    has_images = '<img' in content or '<figure' in content

    if not has_images:
        # Safe to do simple replacements
        content = re.sub(r'<strong>(.*?)</strong>', r'\1', content, flags=re.DOTALL)
        content = re.sub(r'<em>(.*?)</em>', r'\1', content, flags=re.DOTALL)
        content = re.sub(r'<b>(.*?)</b>', r'\1', content, flags=re.DOTALL)
        content = re.sub(r'<i>(.*?)</i>', r'\1', content, flags=re.DOTALL)

    return content

def process_blog_post(filepath):
    """Process a single blog post"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Extract h1 title
    h1_match = re.search(r'<h1>(.*?)</h1>', content, re.DOTALL)
    if h1_match:
        old_title = h1_match.group(1).strip()
        new_title = clean_title(old_title)

        if old_title != new_title:
            # Replace h1
            content = content.replace(f'<h1>{old_title}</h1>', f'<h1>{new_title}</h1>')

            # Also update <title> tag
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                old_page_title = title_match.group(1)
                new_page_title = old_page_title.replace(old_title, new_title)
                content = content.replace(f'<title>{old_page_title}</title>',
                                        f'<title>{new_page_title}</title>')

    # Clean formatting (conservative approach - only if no images)
    content = clean_html_formatting(content)

    # Only write if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    blog_dir = Path('blog')

    # Category pages to skip
    skip_files = {
        'paper-review.html', 'book-summary.html', 'book-review.html',
        'speech-technology.html', 'algorithm.html', 'aesthetics.html',
        'nlp.html', 'phonology.html', 'psycholinguistics.html',
        'graduate-research.html', 'information-theory.html', 'python-code.html',
        'nlp-code.html', 'philosophy.html', 'bash-code.html', 'ctdsi.html',
        'data.html', 'leetcode.html', 'mac-os.html', 'nlu.html', 'perl-code.html',
        'phonetics.html'
    }

    modified_count = 0

    for html_file in sorted(blog_dir.glob('*.html')):
        if html_file.name in skip_files:
            continue

        if process_blog_post(html_file):
            modified_count += 1
            print(f'✓ Cleaned {html_file.name}')

    print(f'\n✓ Modified {modified_count} files')

if __name__ == '__main__':
    main()
