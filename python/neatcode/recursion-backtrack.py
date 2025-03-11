def generateParenthesis(n: int):
    res = []

    def backtrack(current, open_count, close_count):
        if len(current) == 2 * n:  # Base Case: When we used all pairs
            res.append(current)
            return

        if open_count < n:  # Can we add '('?
            backtrack(current + "(", open_count + 1, close_count)

        if close_count < open_count:  # Can we add ')'?
            backtrack(current + ")", open_count, close_count + 1)

    backtrack("", 0, 0)
    return res

def parent(n):
    if n == 0:
        print("Base case reached!")
        return
    print(f"Calling child({n})")
    parent(n - 1)  # Recursive call
    print(f"Returning to parent({n})")  # This runs AFTER the recursive call

parent(3)
parent(10)
