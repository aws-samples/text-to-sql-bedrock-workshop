#!/bin/bash

pip install boto3 -t cloudformation/layers/python
cd cloudformation/layers
zip -r boto3.zip python