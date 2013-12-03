#!/bin/bash

REPO_ROOT=$HOME/Personal/github/home

export PYTHONPATH=${REPO_RROT}:${PYTHONPATH}

TESTS=$(find ${REPO_ROOT} -type f -name '*_test.py' | sort)

echo
echo "Found tests:"
echo "$TESTS" | while read test_program; do
  echo "$test_program"
done

echo "$TESTS" | while read test_program; do
  echo
  echo "==== $test_program ===="
  $test_program
done
