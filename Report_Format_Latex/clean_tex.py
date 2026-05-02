import re

raw_file = "raw_content.tex"
template_file = "undergrad-sample-english.tex"

with open(raw_file, "r") as f:
    raw = f.read()

# Remove \texorpdfstring entirely
raw = re.sub(r'\\texorpdfstring\{(.*?)\}\{[^{}]*\}', r'\1', raw, flags=re.DOTALL)

# Remove pandoc wrappers
raw = re.sub(r'\\(?:section|subsection|subsubsection|paragraph)\{(.*?)\}', r'\1', raw, flags=re.DOTALL)
raw = re.sub(r'\\label\{.*?\}', '', raw)

# Format chapters
def replace_chapter1(m):
    title = m.group(1).strip().replace('\\\\', ' ').replace('\n', ' ')
    title = re.sub(r'\s+', ' ', title)
    return f"\\chapter{{{title}}}"

raw = re.sub(r'\\textbf\{CHAPTER\s+\d+\\\\\s*\}(.*?)(?=\n\n|\n\\)', replace_chapter1, raw, flags=re.DOTALL)

def replace_chapter2(m):
    title = m.group(1).strip().replace('\\\\', ' ').replace('\n', ' ')
    title = re.sub(r'\s+', ' ', title)
    return f"\\chapter{{{title}}}"

raw = re.sub(r'\\textbf\{CHAPTER\s+\d+\\\\\s*(.*?)\}', replace_chapter2, raw, flags=re.DOTALL)

# Format sections X.Y
def replace_section(m):
    title = m.group(1).strip().replace('\n', ' ')
    title = re.sub(r'\s+', ' ', title)
    return f"\\section{{{title}}}"

raw = re.sub(r'\\textbf\{\d+\.\d+\s+([^{}]*)\}', replace_section, raw)

# Format subsections X.Y.Z
def replace_subsection(m):
    title = m.group(1).strip().replace('\n', ' ')
    title = re.sub(r'\s+', ' ', title)
    return f"\\subsection{{{title}}}"

raw = re.sub(r'\\textbf\{\d+\.\d+\.\d+\s+([^{}]*)\}', replace_subsection, raw)

# ====================================================================
# FIX 1a: Remove \hl{...}, \ul{...}, and \mbox{...} wrappers entirely.
# These are DOCX formatting artifacts that break the soul package when
# they contain \url, \href, or other complex commands.
# We use a proper brace-matching function since these can span multiple
# lines with deeply nested braces.
# ====================================================================
def strip_command(text, cmd):
    """Remove all occurrences of \\cmd{...} keeping the inner content."""
    pattern = '\\' + cmd + '{'
    result = []
    i = 0
    while i < len(text):
        pos = text.find(pattern, i)
        if pos == -1:
            result.append(text[i:])
            break
        result.append(text[i:pos])
        # Find matching closing brace
        depth = 0
        j = pos + len(pattern) - 1  # position of the opening {
        while j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0:
                    # Extract inner content (between the { and })
                    inner = text[pos + len(pattern):j]
                    result.append(inner)
                    i = j + 1
                    break
            j += 1
        else:
            # No matching brace found, keep as-is
            result.append(text[i:])
            break
    return ''.join(result)

raw = strip_command(raw, 'hl')
raw = strip_command(raw, 'ul')
raw = strip_command(raw, 'mbox')

# ====================================================================
# FIX 2: "No counter 'none' defined"
# Caused by Pandoc wrapping longtables with {\def\LTcaptype{none} ... }
# Remove the wrapper entirely.
# ====================================================================
raw = raw.replace(r'{\def\LTcaptype{none} % do not increment counter', '')
# Remove the corresponding closing brace — it appears right after \end{longtable}
# We handle this by removing standalone } on its own line after \end{longtable}
raw = re.sub(r'(\\end\{longtable\})\n\}', r'\1', raw)

# ====================================================================
# FIX 3: Undefined \thaifont and \thaiabstract
# Since Thai font is not installed, define stub commands so the template
# Thai abstract section doesn't crash.
# ====================================================================
# (Handled below by injecting \providecommand stubs into preamble)

# Clean paths
raw = raw.replace('report_media/media/', 'report_media/media/')

# Extract body
# Find the start of chapter 1
match = re.search(r'\\chapter\{INTRODUCTION\}', raw, re.DOTALL)
if not match: 
    print("Could not find Chapter 1!")
    body_content = raw
else:
    body_content = raw[match.start():]

# Read template
with open(template_file, "r") as f:
    template = f.read()

# The dummy body starts at \chapter{Introduction} and ends before %%%% Bibliography
start_marker = r'\\chapter\{Introduction\}'
end_marker = r'\%{60,}\s*\%+ Bibliography'

start_match = re.search(start_marker, template)
end_match = re.search(end_marker, template)

if start_match and end_match:
    # We need to find the start marker AGAIN because lengths changed
    start_match = re.search(start_marker, template)
    end_match = re.search(end_marker, template)
    
    new_template = template[:start_match.start()] + body_content + "\n\n" + template[end_match.start():]
    
    # Apply preamble changes
    new_template = new_template.replace(r'\def\disstitleone{Project/Indep study title line 1}', r'\def\disstitleone{KKP Better Mobile Banking Application}')
    new_template = new_template.replace(r'\def\disstitletwo{Project/Indep title line 2 (optional)}', r'\def\disstitletwo{}')
    new_template = new_template.replace(r'\def\dissauthor{Mr./Ms. Firstname1 Lastname1}', r'\def\dissauthor{Mr. Sikares Nuntipatsakul}')
    new_template = new_template.replace(r'\def\dissauthortwo{Mr./Ms. Firstname2 Lastname2}', r'\def\dissauthortwo{Mr. Ratchanon Tarawan}')
    new_template = new_template.replace(r'\def\dissauthorthree{Mr./Ms. Firstname3 Lastname3}', r'\def\dissauthorthree{}')
    new_template = new_template.replace(r'\def\dissyear{202x}', r'\def\dissyear{2025}')
    new_template = new_template.replace(r'\def\thaidissyear{256x}', r'\def\thaidissyear{2568}')
    new_template = new_template.replace(r'\def\dissadvisor{Assoc.Prof. My main advisor name , Ph.D.}', r'\def\dissadvisor{Asst.Prof. Rajchawit Sarochawikasit}')
    new_template = new_template.replace(r'\def\disscoadvisor{Assoc.Prof. My Co-advisor name, Ph.D.}', r'\def\disscoadvisor{Attaporn Thanachanrojsakul}')
    new_template = new_template.replace(r'\def\disscoadvisortwo{}', r'\def\disscoadvisortwo{Kaset Soonthornpat}')
    
    # Packages + stub definitions for Thai font
    packages = r"""
\usepackage{ulem}
\usepackage{soul}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{calc}
\usepackage{array}
\usepackage{enumitem}
\setlist[itemize]{itemsep=0pt, parsep=0pt, leftmargin=2em}
\setlist[enumerate]{itemsep=0pt, parsep=0pt, leftmargin=2em}
% Stub commands so the Thai abstract section compiles even without TH Sarabun New
\providecommand{\thaifont}{}
\providecommand{\textthai}[1]{#1}
"""
    new_template = new_template.replace(r'\usepackage{polyglossia}', packages + r'\usepackage{polyglossia}')
    
    # Remove Thai font (but keep stubs above so \thaifont doesn't crash)
    new_template = new_template.replace(r'\setotherlanguage{thai}', r'%\setotherlanguage{thai}')
    new_template = new_template.replace(r'\newfontfamily\thaifont[Script=Thai,Scale=1.23]{TH Sarabun New}', r'%\newfontfamily\thaifont[Script=Thai,Scale=1.23]{TH Sarabun New}')
    
    with open("project_report.tex", "w") as f:
        f.write(new_template)
    print("Rewritten project_report.tex completely.")
else:
    print("Markers not found.")
