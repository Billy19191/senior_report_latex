import re

with open('project_report.tex', 'r') as f:
    text = f.read()

# We need to map old figure numbers to labels
fig_map = {}

def make_label(title):
    # remove special chars and lowercase
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    words = clean.strip().lower().split()
    return 'fig:' + '-'.join(words[:6]) # limit to 6 words

# Find all occurrences of \textbf{Figure X.Y} Title
# Sometimes it has \\ at the end, sometimes it doesn't.
# Example: \textbf{Figure 2.1} Common Git Workflow\\
# Example: \textbf{Figure 3.2} Example User Interface of Elastic Logging
def fix_caption(match):
    num = match.group(1)
    title = match.group(2).strip()
    
    # remove trailing \\ if exists
    if title.endswith(r'\\'):
        title = title[:-2].strip()
        
    label = make_label(title)
    
    # Store mapping for later
    fig_map[num] = label
    
    return f'\\caption{{{title}}}\\label{{{label}}}'

# Replace the captions
text = re.sub(r'\\textbf\{Figure\s+(\d+\.\d+|3\.x|3\.X)\}\s*([^\n]+)', fix_caption, text)

# Now replace \begin{center} ... \end{center} that contain \includegraphics and \caption with \begin{figure}[H] ... \end{figure}
# We can use a regex that looks for \begin{center} ... \includegraphics ... \caption ... \end{center}
# Actually, a simpler way is to find \begin{center} followed by \includegraphics and \caption, and change center to figure[H]\n\centering
def fix_env(match):
    inner = match.group(1)
    if '\\includegraphics' in inner and '\\caption' in inner:
        return f'\\begin{{figure}}[H]\n\\centering\n{inner.strip()}\n\\end{{figure}}'
    return match.group(0)

# Repeatedly apply the replacement in case of nested things (unlikely, but safe)
# using DOTALL
text = re.sub(r'\\begin\{center\}(.*?)\\end\{center\}', fix_env, text, flags=re.DOTALL)


# Now replace references in text.
# E.g. "figure 2.1" or "Figure 2.1"
for num, label in fig_map.items():
    if num.lower() in ('3.x', '3.x'):
        continue # Skip generic 3.x since it might cause false positives
    # Use negative lookbehind to avoid replacing inside \caption{...} or \label{...} if somehow matched
    # But those don't have "figure 2.1" anymore, they just have \caption{...}
    # Pattern: match "Figure <num>" or "figure <num>"
    pattern = re.compile(r'\b([Ff]igure)\s+' + re.escape(num) + r'\b')
    # Use \1~\ref{label} which preserves the case of "Figure" or "figure"
    # Actually standard LaTeX is Figure~\ref{...} with capital F. Let's force "Figure"
    text = pattern.sub(r'Figure~\\ref{' + label + '}', text)
    
    # also handle plural "Figures 2.1" if any
    pattern_plural = re.compile(r'\b([Ff]igures)\s+' + re.escape(num) + r'\b')
    text = pattern_plural.sub(r'Figures~\\ref{' + label + '}', text)

with open('project_report.tex', 'w') as f:
    f.write(text)

print("Replaced", len(fig_map), "figures.")
