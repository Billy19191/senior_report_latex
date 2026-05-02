import re

file_path = "project_report.tex"

with open(file_path, "r") as f:
    content = f.read()

# Fix \section{\texorpdfstring{\chapter{...}...}...}
# To simplify, we will just completely remove \texorpdfstring and \section wrappers around \chapter.
# First, remove \section{\texorpdfstring{ ... }{ ... }} around \chapter

def clean_chapter(match):
    # Match contains something like \section{\texorpdfstring{\chapter{BACKGROUND, RELATED PRODUCTS,\\}
    # AND DEVELOPMENT TOOLS}{...}}\label{...}
    # We want to just extract the chapter content and format it nicely.
    # Actually, let's just do a string replacement on the file.
    return match.group(0)

# A more robust regex replacement
# Remove \texorpdfstring{A}{B} entirely
# Because it's hard to parse matching braces in regex, let's write a simple brace parser
def remove_texorpdfstring(text):
    out = ""
    i = 0
    while i < len(text):
        if text.startswith(r'\texorpdfstring{', i):
            i += 15
            # extract first arg
            brace_count = 1
            start = i
            while i < len(text) and brace_count > 0:
                if text[i] == '{': brace_count += 1
                elif text[i] == '}': brace_count -= 1
                i += 1
            arg1 = text[start:i-1]
            out += arg1
            
            # extract second arg and drop it
            if i < len(text) and text[i] == '{':
                brace_count = 1
                i += 1
                while i < len(text) and brace_count > 0:
                    if text[i] == '{': brace_count += 1
                    elif text[i] == '}': brace_count -= 1
                    i += 1
        else:
            out += text[i]
            i += 1
    return out

content = remove_texorpdfstring(content)

# Now it looks like \section{\chapter{TITLE}}
content = re.sub(r'\\section\{\\chapter\{(.*?)\}\}', r'\\chapter{\1}', content, flags=re.DOTALL)
content = re.sub(r'\\subsection\{\\chapter\{(.*?)\}\}', r'\\chapter{\1}', content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)
print("Fixed tex")
