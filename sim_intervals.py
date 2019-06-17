import numpy


def sim_intervals(current, target, num_intervals, percent_change_std):
    if num_intervals == 1:
        return [target]
    target_change_for_this_interval = (target - current) / num_intervals
    target_percent_change_for_this_interval = target_change_for_this_interval / current
    actual_percent_change_for_this_interval = numpy.random.normal(target_percent_change_for_this_interval,
                                                                  percent_change_std)
    actual_end_price_for_this_interval = current * (1 + actual_percent_change_for_this_interval)
    return [actual_end_price_for_this_interval] + sim_intervals(actual_end_price_for_this_interval,
                                                                target, num_intervals - 1, percent_change_std)
