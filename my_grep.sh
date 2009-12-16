#!/bin/bash

grep -r $1 $2 | grep -v 'pyc' | grep -v 'py~' | grep -v 'py#' | grep -v 'Binary' 