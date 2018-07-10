#!/bin/bash

cd $1
git log --oneline > 1.log

cd $2
git log --oneline >2.log

output=$3
output=${output%\/*}

diff $1/1.log $2/2.log > $3
if [ $? == 0 ]; then
  echo "Git Repo: $4 are the same..."
else
  echo "Git Repo: $4 are different. Details are in file $output."
fi

rm $1/1.log $2/2.log

