#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p repoman/

xgettext $PYTHON_FILES -o repoman/repoman.pot

echo '' >> repoman/repoman.pot
for i in ../sources.d/default/*json
do
	echo "#: json $i" >> repoman/repoman.pot
	a=$(grep \"desc\": $i | cut -d "\"" -f4)
	echo 'msgid "'${a}'"' >> repoman/repoman.pot
	echo 'msgstr ""'>> repoman/repoman.pot
	echo '' >> repoman/repoman.pot

done
for i in ../sources.d/*json
do
	echo "#: json $i" >> repoman/repoman.pot
	a=$(grep \"desc\": $i | cut -d "\"" -f4)
	echo 'msgid "'${a}'"' >> repoman/repoman.pot
	echo 'msgstr ""'>> repoman/repoman.pot
	echo '' >> repoman/repoman.pot

done
