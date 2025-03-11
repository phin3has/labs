#!/usr/bin/env python3
def longest_substring(s: str) -> str:
    char_map = {}
    left = 0
    max_length = 0
    start = 0

    for right in range(len(s)):
        if s[right] in char_map:
            left = max(left, char_map[s[right]] + 1)
        
        char_map[s[right]] = right
        print(char_map)
        print(right)
        print(left)

        if right - left + 1 > max_length:
            max_length = right - left + 1
            start = left

    return s[start:start + max_length]

print(longest_substring("abc"))  # Output: "abc"
