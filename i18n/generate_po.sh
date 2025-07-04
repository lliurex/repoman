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

echo "#: polkit" >> repoman/repoman.pot
message="Insert your password"
description="Repoman wants to change system settings"
echo 'msgid "'${message}'"' >> repoman/repoman.pot
echo 'msgstr ""'>> repoman/repoman.pot
echo 'msgid "'${description}'"' >> repoman/repoman.pot
echo 'msgstr ""'>> repoman/repoman.pot
echo '' >> repoman/repoman.pot
echo "#: qtextrawidgets" >> repoman/repoman.pot
echo 'msgid "'Apply'"' >> repoman/repoman.pot
echo 'msgstr ""'>> repoman/repoman.pot
echo 'msgid "'Undo'"' >> repoman/repoman.pot
echo 'msgstr ""'>> repoman/repoman.pot
