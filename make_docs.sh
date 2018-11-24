#!/bin/bash

sphinx-apidoc -d 2 -M -f -o docs aiogoogle/ && cd docs && make html && cd .. && chromium-browser docs/_build/html/index.html