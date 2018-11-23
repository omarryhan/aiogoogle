#!/bin/bash

cd docs && make html && cd .. && chromium-browser docs/_build/html/index.html