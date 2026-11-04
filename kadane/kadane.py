"""Kadane's algorithm: the maximum subarray problem."""


def max_subarray(nums):
    """Return the contiguous window with the largest sum.

    Result: {"start": int, "end": int, "best_sum": number} (inclusive indices).
    One pass, O(n). Raises ValueError for empty input.

    Tie rule: when two windows have the same sum, the EARLIER one is returned
    (we only replace the best window when the new sum is strictly larger).
    """
    if len(nums) == 0:
        raise ValueError("nums must not be empty")

    best_sum = nums[0]
    best_start = 0
    best_end = 0

    running_sum = nums[0]
    run_start = 0

    for i in range(1, len(nums)):
        # Extending the old run only helps if its sum is positive.
        if running_sum < 0:
            running_sum = nums[i]
            run_start = i
        else:
            running_sum += nums[i]

        if running_sum > best_sum:
            best_sum = running_sum
            best_start = run_start
            best_end = i

    return {"start": best_start, "end": best_end, "best_sum": best_sum}


def max_profit_window(daily_changes):
    """Finance framing of max_subarray.

    daily_changes is a list of daily price changes (e.g. +2, -3 ...).
    The best window is the best day to buy (start) and the day to sell (end):
    holding the stock over those days gives the biggest total gain.
    Returns the same dict as max_subarray; best_sum is the profit.
    """
    return max_subarray(daily_changes)


if __name__ == "__main__":
    changes = [-2, 1, -3, 7, -1, 2, 1, -5, 4]
    print("Daily changes:", changes)
    print(max_profit_window(changes))  # start 3, end 6, best_sum 9
