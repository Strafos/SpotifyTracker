import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

from spotify_interface import get_data

def graph_frequency(data):
    ids = []
    frequencies = []
    for k, v in data.items():
        ids.append(k)
        frequencies.append(v)

    bar = plt.bar(ids, frequencies)
    ax = plt.subplot(111)
    plt.show(block=True)

def kstest(data, num_tracks):
    observations = []
    for k, v in data.items():
        for i in range(v):
            observations.append(k)

    print(len(observations))

    d, p_val = stats.kstest(rvs=observations, cdf=stats.randint.cdf, args=(0, num_tracks))
    print(d)
    print(p_val)
    d, p_val = stats.kstest(rvs=np.random.randint(num_tracks, size=500), cdf=stats.randint.cdf, args=(0, num_tracks))
    print(d)
    print(p_val)

data, num_tracks = get_data()
# graph_frequency(data)
kstest(data, num_tracks)