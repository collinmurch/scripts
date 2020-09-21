#!/bin/bash

filename=$1

if [ $# -eq 0 ] 
then
    filename="problemset_solution"
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

% List collaborators
Collaborators: NONE

\begin{questions}

\question{
  QUESTION 1
}

\begin{solution}
    \begin{proof}

    % Write text outiside of align

    \begin{align*}
        SOLUTION 1
    \end{align*}
  \end{proof}
\end{solution}

\end{questions}

\end{document}" 

echo "$text" >> "$PWD"/"$filename".tex 

echo "New Latex note document created."
exit
