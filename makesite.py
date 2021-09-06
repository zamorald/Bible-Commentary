#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2018 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Make static website/blog with Python."""


import os
import shutil
import re
import glob
import sys
import json
import datetime


def fread(filename):
    """Read file and close the file."""
    with open(filename, mode='r', encoding='utf-8') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, mode='w', encoding='utf-8') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def truncate(text, words=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words])


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime('%a, %d %b %Y %H:%M:%S +0000')


def read_content(filename):
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'slug': match.group(2),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        try:
            if _test == 'ImportError':
                raise ImportError('Error forced by test')
            import commonmark
            text = commonmark.commonmark(text)
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **page_params)
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')

    # Default parameters.
    params = {
        'base_path': '/',
        'subtitle': 'Commentary on the Bible',
        'author': 'Luis D. Zamora',
        'site_url': 'http://localhost:8000',
        'current_year': datetime.datetime.now().year,
        'last_updated': datetime.datetime.now().strftime('%A %d %B %Y %I:%M %p %z'),
        'current_version': '1.3.0'
    }
    # Books and chapters.
    bible_books = {
        'Genesis':50,
        'Exodus':40,
        'Leviticus':27,
        'Numbers':36,
        'Deuteronomy':34,
        'Joshua':24,
        'Judges':21,
        'Ruth':4,
        '1_Samuel':31,
        '2_Samuel':24,
        '1_Kings':22,
        '2_Kings':25,
        '1_Chronicles':29,
        '2_Chronicles':36,
        'Ezra':10,
        'Nehemiah':13,
        'Esther':10,
        'Job':42,
        'Psalm':150,
        'Proverbs':31,
        'Ecclesiastes':12,
        'Song_of_Solomon':8,
        'Isaiah':66,
        'Jeremiah':52,
        'Lamentations':5,
        'Ezekiel':48,
        'Daniel':12,
        'Hosea':14,
        'Joel':3,
        'Amos':9,
        'Obadiah':1,
        'Jonah':4,
        'Micah':7,
        'Nahum':3,
        'Habakkuk':3,
        'Zephaniah':3,
        'Haggai':2,
        'Zechariah':14,
        'Malachi':4,
        'Matthew':28,
        'Mark':16,
        'Luke':24,
        'John':21,
        'Acts':28,
        'Romans':16,
        '1_Corinthians':16,
        '2_Corinthians':13,
        'Galatians':6,
        'Ephesians':6,
        'Philippians':4,
        'Colossians':4,
        '1_Thessalonians':5,
        '2_Thessalonians':3,
        '1_Timothy':6,
        '2_Timothy':4,
        'Titus':3,
        'Philemon':1,
        'Hebrews':13,
        'James':5,
        '1_Peter':5,
        '2_Peter':3,
        '1_John':5,
        '2_John':1,
        '3_John':1,
        'Jude':1,
        'Revelation':22,
        'Appendix':0
    }

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    # Load layouts.
    page_layout = fread('layout/page.html')
    chapter_layout = fread('layout/chapter.html')
    toc_layout = fread('layout/toc.html')
    
    # Combine layouts to form final layouts.
    chapter_layout = render(page_layout, content=chapter_layout)
    toc_layout = render(page_layout, content=toc_layout)
    
    # Make Appendix pages.
    articles = glob.glob('content\\Appendix\\[!^index]**')
    for article in articles:
        make_pages(article, '_site\\Appendix\\{{ slug }}\\index.html', page_layout, **params)
    
    # Combine verses to form chapters.
    chapters = glob.glob('content\\**\\**\\')
    for chapter in chapters:
        # Create file "index.html" in the chapter directory by reading verse files into it.
        # Commented verses are HTML files prepended with an underscore.
        verses = glob.glob(chapter + '_*.html')

        # Don't forget to specify encoding to preserve Greek characters.
        with open(chapter + 'index.html', mode='w', encoding='utf-8') as c:
            for verse in sorted(verses):
                content = fread(str(verse))
                c.write(content)

        # Create chapter pages.
        make_pages(chapter + 'index.html', '_site\\' + chapter.removeprefix('content\\') + 'index.html', chapter_layout, **params)

    # key book url to book slug
    books = glob.glob('content\\**\\')
    book_sorter = {}
    for book in books:
        book_sorter[book.removeprefix('content\\').replace(' ','_').removesuffix('\\')] = book

    # Generate Table of Contents content.
    with open('content/index.html', mode='w', encoding='utf-8') as toc:
        toc.write('<!-- render : yes               -->\n')
        toc.write('<!-- book   : BibleCommentary   -->\n')
        toc.write('<!-- chapter: TableOfContents   -->\n')
        toc.write('<!-- title  : Table of Contents -->\n\n')

        # Outer "for" sorts in traditional Bible book order.
        for book in bible_books.keys():
            if book in book_sorter:
                toc.write('\n\t\t\t<li>' + book.replace('_',' ') + '\n\t\t\t\t<ul class="w3-ul">')

                chapters = glob.glob(book_sorter[book] + '\\**\\')
                chapter_sorter = {}
                for chapter in chapters:
                    chapter_sorter[chapter.removeprefix(book_sorter[book]).removesuffix('\\')] = chapter
                
                # for chapter sorts in numerical order, not string-representation-of-a-number order.
                # I.e., 11 > 2, not '11' < '2'.
                for chapter in range(bible_books[book]):
                    # Real chapters don't start at 0.
                    chapter += 1

                    if str(chapter) in chapter_sorter:
                        toc.write('\n\t\t\t\t\t<li>')
                        toc.write('<a class="w3-hover-shadow" href="{{ base_path }}' + chapter_sorter[str(chapter)].removeprefix('content\\') + '">')
                        toc.write(str(chapter) + '</a></li>')

                # Appendix has 0 chapters and won't enter the "for chapter" loop above.
                if book == 'Appendix':
                    articles = glob.glob('_site\\Appendix\\**\\')
                    for article in articles:
                        toc.write('\n\t\t\t\t\t<li>')
                        toc.write('<a class="w3-hover-shadow" href="{{ base_path }}' + article.removeprefix('_site\\') + '">')
                        toc.write(article.removeprefix('_site\\Appendix\\').replace('-', ' ').removesuffix('\\') + '</a></li>')

                toc.write('\n\t\t\t\t</ul>')
                toc.write('\n\t\t\t</li>\n')


    # Create Table of Contents and Change Log site pages.
    make_pages('content/index.html', '_site/index.html',
               toc_layout, **params)
    make_pages('content/change-log.html', '_site/change-log.html',
           page_layout, **params)

    # Create target site directory from scratch.
    log('Clearing \\Accuracy-Matters ......')
    if os.path.isdir('\\Accuracy-Matters'):
        with os.scandir(path='\\Accuracy-Matters') as contents:
            for entry in contents:
                if not entry.name.startswith('.'):
                    if entry.is_file():
                        print('Removing file:', entry.name)
                        os.remove(entry)
                    else:
                        print('Removing directory:', entry.name)
                        shutil.rmtree(entry)
    log('Copying _site => \\Accuracy-Matters')
    shutil.copytree('_site', '\\Accuracy-Matters', dirs_exist_ok=True)
    log('Now go commit that gh-pages branch.')

# Test parameter to be set temporarily by unit tests.
_test = None


if __name__ == '__main__':
    main()
