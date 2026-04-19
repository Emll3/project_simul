"""
File created by Maxim Frankish. Adapted by Samuel Bakker.
Contains distributions used in simulation.py.

Note: ofcourse you can also use the scipy.stats package to instantiate a distribution on which you then call .rvs().
But why would you, if this is more fun? ;)
"""

import math

def Exponential_distribution(lambda_value, rng) -> float:
    """Exponential distribution

    Args:
        lambda_value (float): shape parameter
        rng: random number generator (instance of random.Random)

    Returns:
        float: random sample
    """
    j1 = rng.randint(1, 1000) / 1000   # nooit 0
    j2 = -math.log(j1) / lambda_value
    return j2


def Normal_distribution(mean, stdev, rng) -> float:
    """Normal distribution.

    Args:
        mean (float): mean
        stdev (float): stddev
        rng: random number generator (instance of random.Random)

    Returns:
        float: value in minutes
    """
    do_loop = True
    while do_loop:
        v1 = rng.random() * 2 - 1
        v2 = rng.random() * 2 - 1
        t = v1 * v1 + v2 * v2
        if (t >= 1) or (t == 0):
            do_loop = True
        else:
            do_loop = False
    multiplier = math.sqrt(-2 * math.log(t) / t)
    x = v1 * multiplier * stdev + mean
    return x


def Bernouilli_distribution(prob, rng) -> bool:
    """Bernouilli distribution

    Args:
        prob (float): probability of returning True
        rng: random number generator (instance of random.Random)

    Returns:
        bool: true if random number is smaller than prob, false otherwise
    """
    j1 = rng.random()
    return j1 < prob