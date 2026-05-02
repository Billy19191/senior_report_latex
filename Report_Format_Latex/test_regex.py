import re

text = r"""
\textbf{CHAPTER 1\\
}INTRODUCTION

some text

\textbf{CHAPTER 2\\
BACKGROUND, RELATED PRODUCTS,\\
AND DEVELOPMENT
TOOLS}

more text

\textbf{CHAPTER 3\\
METHODOLOGY AND
DESIGN}

end text
"""

def replace_chapter1(m):
    title = m.group(1).strip().replace('\\\\', ' ').replace('\n', ' ')
    return f"\\chapter{{{title}}}"

text = re.sub(r'\\textbf\{CHAPTER\s+\d+\\\\\s*\}(.*?)(?=\n\n|\n\\)', replace_chapter1, text, flags=re.DOTALL)

def replace_chapter2(m):
    title = m.group(1).strip().replace('\\\\', ' ').replace('\n', ' ')
    # Clean up multiple spaces
    title = re.sub(r'\s+', ' ', title)
    return f"\\chapter{{{title}}}"

text = re.sub(r'\\textbf\{CHAPTER\s+\d+\\\\\s*(.*?)\}', replace_chapter2, text, flags=re.DOTALL)

print(text)
