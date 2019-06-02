import snoop
import numpy as np
import pandas as pd


@snoop.snoop()
def main():
    _df = pd.DataFrame([[1, 2], [3, 4]])
    _arr = np.array([[1, 2], [3, 4]])


expected_output = """
12:34:56.78 >>> Call to main in File "/path/to_file.py", line 7
12:34:56.78    7 | def main():
12:34:56.78    8 |     _df = pd.DataFrame([[1, 2], [3, 4]])
12:34:56.78 .......... _df =    0  1
12:34:56.78                  0  1  2
12:34:56.78                  1  3  4
12:34:56.78 .......... len(_df) = 2
12:34:56.78 .......... _df.shape = (2, 2)
12:34:56.78    9 |     _arr = np.array([[1, 2], [3, 4]])
12:34:56.78 .......... _arr = array([[1, 2],
12:34:56.78                          [3, 4]])
12:34:56.78 .......... len(_arr) = 2
12:34:56.78 .......... _arr.shape = (2, 2)
12:34:56.78 <<< Return value from main: None
"""
