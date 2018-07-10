#!/bin/sh

PWD=$(pwd)
cd $PWD

if [ -e build ];then
  rm -rf build/*
else
  mkdir build
fi

python -O -m py_compile diff_repo.py

cp compare_git_log.sh  build
mv diff_repo.pyo build
