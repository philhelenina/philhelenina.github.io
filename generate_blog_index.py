#!/usr/bin/env python3
"""
Generate blog index and category pages from converted blog posts
"""

import os
from pathlib import Path
from datetime import datetime
import re

def extract_metadata_from_html(filepath):
    """Extract title and date from HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    title = title_match.group(1) if title_match else 'Untitled'

    # Extract date
    date_match = re.search(r'<p class="post-date">(.*?)</p>', content)
    date_str = date_match.group(1) if date_match else ''

    # Extract categories from metadata
    categories_match = re.search(r'<strong>Categories:</strong>\s*(.*?)</p>', content, re.DOTALL)
    categories = []
    if categories_match:
        cat_text = categories_match.group(1)
        categories = [c.strip() for c in cat_text.split(',')]

    # Also extract categories from title (e.g., [Paper Review - NLP])
    if title:
        # Match patterns like [Paper Review - X] or [Book Summary - X]
        title_cats = re.findall(r'\[(Paper Review|Book Summary|Book Review|Algorithm|Speech Technology|NLP|Psycholinguistics)[^\]]*\]', title, re.IGNORECASE)
        for cat in title_cats:
            # Extract the main category
            main_cat = cat.split('-')[0].strip() if '-' in cat else cat
            if main_cat not in categories:
                categories.append(main_cat)

    # Extract first 200 chars of content for preview
    content_match = re.search(r'<h1>.*?</p>\s*(.*?)\s*<p class="post-meta">', content, re.DOTALL)
    preview = ''
    if content_match:
        preview_html = content_match.group(1)
        # Remove HTML tags for preview
        preview = re.sub(r'<[^>]+>', '', preview_html)
        preview = preview[:200].strip() + '...' if len(preview) > 200 else preview

    return {
        'title': title,
        'date': date_str,
        'categories': categories,
        'preview': preview
    }

def categorize_posts(blog_dir='blog'):
    """Scan blog directory and categorize posts"""
    blog_path = Path(blog_dir)
    posts_by_category = {}
    all_posts = []

    for html_file in blog_path.glob('*.html'):
        if html_file.name in ['book-summaries.html', 'paper-reviews.html', 'speech-technology.html']:
            continue

        metadata = extract_metadata_from_html(html_file)

        post_info = {
            'filename': html_file.name,
            'title': metadata['title'],
            'date': metadata['date'],
            'preview': metadata['preview']
        }

        all_posts.append(post_info)

        # Categorize
        for category in metadata['categories']:
            cat_key = category.lower().replace(' ', '-')
            if cat_key not in posts_by_category:
                posts_by_category[cat_key] = []
            posts_by_category[cat_key].append(post_info)

    # Sort all posts by date (newest first)
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%B %d, %Y")
        except:
            return datetime.min

    all_posts.sort(key=lambda x: parse_date(x['date']), reverse=True)

    for cat in posts_by_category:
        posts_by_category[cat].sort(key=lambda x: parse_date(x['date']), reverse=True)

    return all_posts, posts_by_category

def generate_blog_index(all_posts):
    """Generate main blog index page"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Blog posts by Cheonkam Jeong">
    <title>Blog - Cheonkam Jeong</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Blog</h1>

    <!-- Categories -->
    <p style="margin-bottom: 2rem;">
        <strong>Categories:</strong>
        <a href="blog/book-summaries.html">Book Summaries</a> |
        <a href="blog/paper-reviews.html">Paper Reviews</a> |
        <a href="blog/speech-technology.html">Speech Technology</a> |
        <a href="blog/algorithm.html">Algorithm</a> |
        <a href="blog/aesthetics.html">Aesthetics</a> |
        <a href="blog/nlp.html">NLP</a>
    </p>

    <!-- Blog posts listed in reverse chronological order -->
"""

    for post in all_posts:
        html += f"""
    <div class="blog-post">
        <h2><a href="blog/{post['filename']}">{post['title']}</a></h2>
        <p class="post-date">{post['date']}</p>
        <p>
            {post['preview']}
        </p>
    </div>
"""

    html += """
    <!-- Navigation -->
    <nav>
        <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="publications.html">Publications</a></li>
            <li><a href="blog.html" class="active">Blog</a></li>
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

def generate_category_page(category_name, posts):
    """Generate a category page"""
    category_title = category_name.replace('-', ' ').title()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category_title} - Cheonkam Jeong</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <h1>{category_title}</h1>

    <p><a href="../blog.html">← Back to all posts</a></p>
"""

    for post in posts:
        html += f"""
    <div class="blog-post">
        <h2><a href="{post['filename']}">{post['title']}</a></h2>
        <p class="post-date">{post['date']}</p>
        <p>
            {post['preview']}
        </p>
    </div>
"""

    html += """
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

def main():
    print("Scanning blog posts...")
    all_posts, posts_by_category = categorize_posts()

    print(f"Found {len(all_posts)} posts in {len(posts_by_category)} categories")

    # Generate main blog index
    print("\nGenerating blog.html...")
    blog_html = generate_blog_index(all_posts)
    with open('blog.html', 'w', encoding='utf-8') as f:
        f.write(blog_html)
    print("✓ Created blog.html")

    # Generate category pages
    print("\nGenerating category pages...")
    for category, posts in posts_by_category.items():
        category_file = f'blog/{category}.html'
        category_html = generate_category_page(category, posts)
        with open(category_file, 'w', encoding='utf-8') as f:
            f.write(category_html)
        print(f"✓ Created {category_file} ({len(posts)} posts)")

    print("\n✓ All done!")
    print("\nCategory breakdown:")
    for category, posts in sorted(posts_by_category.items()):
        print(f"  - {category}: {len(posts)} posts")

if __name__ == '__main__':
    main()
