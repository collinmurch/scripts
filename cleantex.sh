#!/bin/bash

rm "$PWD"/*.synctex.gz &> /dev/null
rm "$PWD"/*.fdb_latexmk &> /dev/null
rm "$PWD"/*.fls &> /dev/null
rm "$PWD"/*.aux &> /dev/null
rm "$PWD"/*.log &> /dev/null
rm "$PWD"/*.out &> /dev/null
echo "Directory cleaned!"
exit
