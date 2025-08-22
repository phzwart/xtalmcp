#!/usr/bin/env bash
# Run from the xtalmcp project root
export PYTHONPATH="/storage/Projects/xtalmcp/src${PYTHONPATH:+:$PYTHONPATH}"
exec /home/pzwart/miniconda3/envs/xtalmcp/bin/python \
  -m xtalmcp serve-stdio --config examples/numpy_server/numpy_tools.yaml
