import numpy as np
import pandas as pd
import pickle

import pygsheets
import os
import json

if os.environ.get('GDRIVE_API_CREDENTIALS') is not None:
    gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS') #web

