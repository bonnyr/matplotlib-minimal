#!/bin/bash
sample=$1
shift
pod=$1
shift

docker run -ti -v ${PWD}:/app -w /app czentye/matplotlib-minimal python3 chartplotter.py -m $sample $pod $*