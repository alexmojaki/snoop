import snoop
import numpy as np
import pandas as pd


@snoop.snoop()
def main():
    arr = np.arange(10000)
    arr = arr.reshape((100, 100))
    df = pd.DataFrame(arr)
    series = df[0]
    return series
