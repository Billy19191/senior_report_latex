import re

file_path = "project_report.tex"

with open(file_path, "r") as f:
    content = f.read()

packages = r"""
\usepackage{ulem}
\usepackage{soul}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{calc}
\usepackage{array}
"""

content = content.replace(r'\usepackage{polyglossia}', packages + r'\usepackage{polyglossia}')

with open(file_path, "w") as f:
    f.write(content)

print("Added packages.")
