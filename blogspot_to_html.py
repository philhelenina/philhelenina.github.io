#!/usr/bin/env python3
"""
Blogspot XML to HTML Converter
Converts Blogspot export XML to individual HTML blog posts
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import re
import os
from pathlib import Path

# Namespace for Atom feeds
ATOM_NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'blogger': 'http://schemas.google.com/blogger/2018'
}

def clean_filename(title):
    """Convert title to filename-safe string"""
    # Remove special characters and convert to lowercase
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    # Replace spaces with hyphens
    filename = re.sub(r'[-\s]+', '-', filename)
    # Limit length
    return filename[:100]

def should_exclude_post(labels):
    """Check if post should be excluded based on labels"""
    excluded_categories = [
        'ai ethics & law',
        'ai ethics',
        'law'
    ]

    for label in labels:
        label_lower = label.lower()
        for excluded in excluded_categories:
            if excluded in label_lower:
                return True
    return False

def extract_category_from_labels(labels):
    """Extract main category from labels"""
    category_mapping = {
        'speech technology': 'speech-technology',
        'book summary': 'book-summaries',
        'paper review': 'paper-reviews',
        'aesthetics': 'aesthetics',
        'algorithm': 'algorithm',
        'research': 'research',
        'tutorial': 'tutorials',
        'data science': 'data-science',
        'nlp': 'nlp',
        'linguistics': 'linguistics'
    }

    for label in labels:
        label_lower = label.lower()
        for key, value in category_mapping.items():
            if key in label_lower:
                return value

    return 'general'

def create_html_post(title, date, content, labels, original_url):
    """Create HTML content for a blog post"""
    date_str = date.strftime("%B %d, %Y")

    # Clean up content - remove Blogger-specific elements
    content = re.sub(r'<div[^>]*blogger[^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Cheonkam Jeong</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <article class="blog-post">
        <h1>{title}</h1>
        <p class="post-date">{date_str}</p>

        {content}

        <p class="post-meta">
            <strong>Categories:</strong> {', '.join(labels)}
        </p>

        <p class="post-meta">
            <small>Original post: <a href="{original_url}" target="_blank">{original_url}</a></small>
        </p>
    </article>

    <!-- Navigation -->
    <nav>
        <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="../publications.html">Publications</a></li>
            <li><a href="../blog.html" class="active">Blog</a></li>
        </ul>
    </nav>

    <!-- Footer -->
    <footer>
        <p>&copy; 2025 Cheonkam Jeong. Last updated: October 2025.</p>
    </footer>
</body>
</html>
"""
    return html

def parse_blogspot_xml(xml_file):
    """Parse Blogspot XML and extract blog posts"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    posts = []

    for entry in root.findall('atom:entry', ATOM_NS):
        # Check if this is a blog post using blogger:type
        post_type = entry.find('blogger:type', ATOM_NS)
        if post_type is None or post_type.text != 'POST':
            continue

        # Check status
        status = entry.find('blogger:status', ATOM_NS)
        if status is None or status.text != 'LIVE':
            continue

        # Get labels from categories
        labels = []
        categories = entry.findall('atom:category', ATOM_NS)
        for category in categories:
            term = category.get('term', '')
            if term:
                labels.append(term)

        # Check if post should be excluded
        if should_exclude_post(labels):
            continue

        # Extract post data
        title_elem = entry.find('atom:title', ATOM_NS)
        title = title_elem.text if title_elem is not None else 'Untitled'

        published_elem = entry.find('atom:published', ATOM_NS)
        if published_elem is not None:
            date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
        else:
            date = datetime.now()

        content_elem = entry.find('atom:content', ATOM_NS)
        content = content_elem.text if content_elem is not None else ''

        # Get original URL from blogger:filename
        filename_elem = entry.find('blogger:filename', ATOM_NS)
        if filename_elem is not None and filename_elem.text:
            original_url = f"https://cheonkamjeong.blogspot.com{filename_elem.text}"
        else:
            original_url = ''

        posts.append({
            'title': title,
            'date': date,
            'content': content,
            'labels': labels,
            'url': original_url
        })

    # Sort by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)

    return posts

def generate_blog_files(posts, output_dir='blog'):
    """Generate HTML files for all posts"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    category_posts = {}
    generated_files = []

    for post in posts:
        # Create filename
        filename = clean_filename(post['title']) + '.html'
        filepath = output_path / filename

        # Determine category
        category = extract_category_from_labels(post['labels'])
        if category not in category_posts:
            category_posts[category] = []

        category_posts[category].append({
            'title': post['title'],
            'date': post['date'],
            'filename': filename,
            'preview': post['content'][:200] if post['content'] else ''
        })

        # Generate HTML
        html_content = create_html_post(
            post['title'],
            post['date'],
            post['content'],
            post['labels'],
            post['url']
        )

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        generated_files.append(str(filepath))
        print(f"Generated: {filepath}")

    return generated_files, category_posts

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python blogspot_to_html.py <blogspot_xml_file>")
        print("\nExample:")
        print("  python blogspot_to_html.py blog-10-22-2025.xml")
        sys.exit(1)

    xml_file = sys.argv[1]

    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' not found")
        sys.exit(1)

    print(f"Parsing {xml_file}...")
    posts = parse_blogspot_xml(xml_file)
    print(f"Found {len(posts)} blog posts")

    print("\nGenerating HTML files...")
    generated_files, category_posts = generate_blog_files(posts)

    print(f"\n✓ Successfully generated {len(generated_files)} blog posts")
    print(f"\nCategories found:")
    for category, posts_list in category_posts.items():
        print(f"  - {category}: {len(posts_list)} posts")

    print("\nNext steps:")
    print("1. Review the generated files in the blog/ directory")
    print("2. Update blog.html to include all posts")
    print("3. Create/update category pages (book-summaries.html, paper-reviews.html, etc.)")

if __name__ == '__main__':
    main()
