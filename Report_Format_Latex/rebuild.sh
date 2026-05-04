#!/bin/bash
# Clean and Rebuild script to bypass the "invalid character" error
# caused by external file interference (e.g. iCloud syncing).

JOBNAME="report_build"
MAIN_FILE="project_report.tex"

echo "Cleaning auxiliary files..."
rm -f ${MAIN_FILE%.tex}.aux ${MAIN_FILE%.tex}.log ${MAIN_FILE%.tex}.toc ${MAIN_FILE%.tex}.out ${MAIN_FILE%.tex}.lof ${MAIN_FILE%.tex}.fls ${MAIN_FILE%.tex}.bbl ${MAIN_FILE%.tex}.blg ${MAIN_FILE%.tex}.fdb_latexmk ${MAIN_FILE%.tex}.synctex.gz
rm -f ${JOBNAME}.*

echo "Pass 1: xelatex (jobname: ${JOBNAME})..."
xelatex -interaction=nonstopmode -jobname=${JOBNAME} ${MAIN_FILE}

echo "Pass 2: bibtex..."
bibtex ${JOBNAME}

echo "Pass 3: xelatex..."
xelatex -interaction=nonstopmode -jobname=${JOBNAME} ${MAIN_FILE}

echo "Pass 4: xelatex..."
xelatex -interaction=nonstopmode -jobname=${JOBNAME} ${MAIN_FILE}

if [ -f ${JOBNAME}.pdf ]; then
    cp ${JOBNAME}.pdf project_report.pdf
    cp ${JOBNAME}.bbl project_report.bbl
    cp ${JOBNAME}.aux project_report.aux
    echo "Success! Final PDF generated as project_report.pdf"
    echo "Citations have been synced to project_report.bbl"
else
    echo "Build failed. Check ${JOBNAME}.log for details."
fi
