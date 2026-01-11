import snoop
import numpy as np
import pandas as pd


@snoop.snoop()
def main():
    arr = np.arange(10000).astype(str)
    arr = arr.reshape((100, 100))
    df = pd.DataFrame(arr)
    series = df[0]
    return series


if __name__ == '__main__':
    main()
