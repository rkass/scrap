import numpy


def sim_intervals(current, target, num_intervals):
    if num_intervals == 1:
        return [target]
    target_change_for_this_interval = (target - current) / num_intervals
    actual_change_for_this_interval = numpy.random.normal(target_change_for_this_interval)
    actual_end_price_for_this_interval = current + actual_change_for_this_interval
    return [actual_end_price_for_this_interval] + sim_intervals(actual_end_price_for_this_interval,
                                                                target, num_intervals - 1)