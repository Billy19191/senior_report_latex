import re

raw_file = "raw_content.tex"
template_file = "project_report.tex"

with open(raw_file, "r") as f:
    raw_content = f.read()

# 1. Remove \texorpdfstring{A}{B} and keep A
# A might contain \textbf{...} so we use a non-greedy match that assumes B does not contain '}' except at the end.
# Actually, B is usually plain text.
# Let's use a simpler approach: find \texorpdfstring{ and balance braces.
def strip_texorpdfstring(text):
    result = []
    i = 0
    while i < len(text):
        if text.startswith(r'\texorpdfstring{', i):
            i += len(r'\texorpdfstring{')
            # Extract first argument
            brace_count = 1
            arg1_start = i
            while i < len(text) and brace_count > 0:
                if text[i] == '{': brace_count += 1
                elif text[i] == '}': brace_count -= 1
                i += 1
            arg1 = text[arg1_start:i-1]
            
            # Now extract second argument
            if i < len(text) and text[i] == '{':
                brace_count = 1
                i += 1
                while i < len(text) and brace_count > 0:
                    if text[i] == '{': brace_count += 1
                    elif text[i] == '}': brace_count -= 1
                    i += 1
            
            result.append(arg1)
        else:
            result.append(text[i])
            i += 1
    return "".join(result)

raw_content = strip_texorpdfstring(raw_content)

# Extract body from "CHAPTER 1"
match = re.search(r'\\textbf\{CHAPTER 1\\\\.*?\}INTRODUCTION', raw_content, re.DOTALL)
if not match:
    match = re.search(r'\\textbf\{CHAPTER 1', raw_content)

if match:
    body_content = raw_content[match.start():]
else:
    body_content = raw_content

# Remove all labels added by pandoc
body_content = re.sub(r'\\label\{.*?\}', '', body_content)

# Remove \section{}, \subsection{}, \subsubsection{}, \paragraph{} wrappers from pandoc
# since pandoc wraps \textbf{...} in \section{} sometimes.
body_content = re.sub(r'\\(?:section|subsection|subsubsection|paragraph)\{(.*?)\}', r'\1', body_content, flags=re.DOTALL)

# Now we have lines with \textbf{CHAPTER X\\ TITLE} or \textbf{X.Y TITLE} or \textbf{X.Y.Z TITLE}
def format_headings(text):
    # Fix Chapter
    text = re.sub(r'\\textbf\{CHAPTER \d+\\\\\s*(.*?)\}', r'\\chapter{\1}', text)
    # Fix Section (X.Y)
    text = re.sub(r'\\textbf\{\d+\.\d+\s+(.*?)\}', r'\\section{\1}', text)
    # Fix Subsection (X.Y.Z)
    text = re.sub(r'\\textbf\{\d+\.\d+\.\d+\s+(.*?)\}', r'\\subsection{\1}', text)
    return text

body_content = format_headings(body_content)

# Fix image paths
# Ensure paths like report_media/media/image8.png are used properly
body_content = body_content.replace('report_media/media/', '../report_media/media/') 
# Wait, project_report.tex is inside Report Format Latex/, and report_media is also inside Report Format Latex/.
# So 'report_media/media/' should just be 'report_media/media/'. Let's restore it.
body_content = body_content.replace('../report_media/media/', 'report_media/media/')

with open(template_file, "r") as f:
    template_content = f.read()

start_marker = r'\\chapter\{Introduction\}'
end_marker = r'\%{60,}\s*\%+ Bibliography'

start_match = re.search(start_marker, template_content)
end_match = re.search(end_marker, template_content)

if start_match and end_match:
    new_template = template_content[:start_match.start()] + body_content + "\n\n" + template_content[end_match.start():]
    with open(template_file, "w") as f:
        f.write(new_template)
    print("Successfully merged content.")
else:
    print("Could not find markers.")
