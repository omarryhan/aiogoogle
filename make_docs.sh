#!/bin/bash

# sphinx-apidoc -d 2 -M -f -o docs aiogoogle/ && cd docs && make html && cd .. && chromium-browser docs/_build/html/index.html
cd docs && make html || (echo "make sure you are in a virtual env and have docs_requirements.txt installed" && cd .. && exit 1) && cd .. && sensible-browser docs/_build/html/index.html
