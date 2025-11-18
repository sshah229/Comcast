#!/usr/bin/env python3
"""
Median Calculator - Activity 2

Implements:
- sort(numbers): in-place insertion sort (ascending)
- sortAndFindMedian(numbers): sorts, then returns median following the pseudocode

Run examples:
- python median.py 3 1 4 1 5
- python median.py
  (then enter numbers separated by spaces or commas)
"""
from __future__ import annotations

import sys
from typing import Iterable, List


def insertion_sort(numbers: List[float]) -> None:
    for i in range(1, len(numbers)):
        key = numbers[i]
        j = i - 1
        while j >= 0 and numbers[j] > key:
            numbers[j + 1] = numbers[j]
            j -= 1
        numbers[j + 1] = key


def sort(numbers: List[float]) -> None:
    insertion_sort(numbers)


def sortAndFindMedian(numbers: List[float]) -> float:
    if not numbers:
        raise ValueError("Input list is empty")
    arr = list(numbers)
    sort(arr)
    n = len(arr)
    if n % 2 == 0:
        return (arr[n // 2 - 1] + arr[n // 2]) / 2
    else:
        return arr[n // 2]


def parse_numbers(args: Iterable[str]) -> List[float]:
    tokens: List[str] = []
    for token in args:
        tokens.extend(token.replace(",", " ").split())
    if not tokens:
        raise ValueError("No numbers provided")
    try:
        return [float(x) for x in tokens]
    except ValueError as e:
        raise ValueError("All inputs must be numeric") from e


def main() -> None:
    if len(sys.argv) > 1:
        nums = parse_numbers(sys.argv[1:])
    else:
        try:
            raw = input("Enter numbers separated by spaces or commas: ")
        except EOFError:
            print("No input provided.")
            sys.exit(1)
        nums = parse_numbers([raw])

    try:
        median = sortAndFindMedian(nums)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Print results
    arr_show = list(nums)
    sort(arr_show)
    print(f"Sorted: {arr_show}")
    print(f"Median: {median}")


if __name__ == "__main__":
    main()
