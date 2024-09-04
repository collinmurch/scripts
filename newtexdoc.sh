#!/bin/bash

filename=$1

if [ $# -eq 0 ] 
then
    filename="problemset"
fi

text=" \documentclass[answers]{exam}

\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{mathrsfs}
\usepackage{graphicx}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue
}

% Title, name, netID, and due date
\title{TITLE}
\author{Collin Murch -- cdm5184}
\date{DUE DATE}

\begin{document}

\maketitle


\end{document}" 

echo "$text" >> "$PWD"/"$filename".tex 

echo "New Latex note document created."
exit
