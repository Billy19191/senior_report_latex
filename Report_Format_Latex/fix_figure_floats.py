import re

with open('project_report.tex', 'r') as f:
    text = f.read()

# Pattern to find two consecutive center environments where the first contains \includegraphics
# and the second contains \caption. Or maybe they are separated by empty lines.
# We want to combine them into one figure environment.
# First, let's find any \begin{center}...\end{center} that just has \caption inside,
# and see what precedes it.
# Actually, the most robust way is to find \caption{...} inside \begin{center}...\end{center}
# and pull the preceding \begin{center}...\end{center} containing \includegraphics into it.

def merge_centers(text):
    # Regex:
    # \begin{center} (any \includegraphics) \end{center}
    # \s*
    # \begin{center} (\caption{...} and maybe Source: ...) \end{center}
    pattern = re.compile(
        r'\\begin\{center\}\s*(\\includegraphics[^}]*\})\s*\\end\{center\}\s*'
        r'\\begin\{center\}\s*(\\caption\{.*?\}\\label\{.*?\}(?:\s*Source:.*?(?=\\end\{center\}))?)\s*\\end\{center\}',
        re.DOTALL
    )
    
    # Replacement puts them together in a figure[H]
    def replacer(match):
        img = match.group(1).strip()
        cap = match.group(2).strip()
        return f'\\begin{{figure}}[H]\n\\centering\n{img}\n{cap}\n\\end{{figure}}'

    return pattern.sub(replacer, text)

# Also handle cases where they were already in the same \begin{center} but we just need to change it to \begin{figure}[H]
def fix_single_center(text):
    # If a center environment has both \includegraphics and \caption
    pattern = re.compile(r'\\begin\{center\}\s*(\\includegraphics[^}]*\}[\s\S]*?\\caption\{.*?\}\\label\{.*?\}(?:\s*Source:.*?(?=\\end\{center\}))?)\s*\\end\{center\}')
    
    def replacer(match):
        content = match.group(1).strip()
        return f'\\begin{{figure}}[H]\n\\centering\n{content}\n\\end{{figure}}'
        
    return pattern.sub(replacer, text)

new_text = merge_centers(text)
new_text = fix_single_center(new_text)

# there may also be cases where \caption is NOT inside \begin{center} at all, but follows \begin{center} \includegraphics \end{center}
def merge_uncentered_caption(text):
    pattern = re.compile(
        r'\\begin\{center\}\s*(\\includegraphics[^}]*\})\s*\\end\{center\}\s*'
        r'(\\caption\{.*?\}\\label\{.*?\}(?:\s*Source:.*?(?=\n\n|\Z))?)',
        re.DOTALL
    )
    def replacer(match):
        img = match.group(1).strip()
        cap = match.group(2).strip()
        return f'\\begin{{figure}}[H]\n\\centering\n{img}\n{cap}\n\\end{{figure}}'
    
    return pattern.sub(replacer, text)
    
new_text = merge_uncentered_caption(new_text)

# Finally, if there is ANY bare \caption left over that is still causing issues, we can check.
# But let's save and see.
with open('project_report.tex', 'w') as f:
    f.write(new_text)

print("Merged center environments and fixed figures.")
