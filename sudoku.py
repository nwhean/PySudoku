"""Solve Sudoku Puzzle using DLX."""
from pydlx import create_network, search
from pydlx.link import Link


class SolutionNotFound(Exception):
    """Raised if no Sudoku Solution is Found."""


def read_puzzle(filename: str) -> list[str]:
    """Read a sudoku puzzle and return as a list of strings."""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def write_matrix(filename: str, mat: list[list[int]]) -> None:
    """Write an exact cover matrix to a file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for row in mat:
            for i in range(0, 324, 81):
                file.write("".join(str(c) for c in row[i:i+81]))
                file.write("|")
            file.write("\n")

def puzzle_to_matrix(strs: list[str]) -> list[list[int]]:
    """Convert puzzle into an exact cover matrix."""
    retval = []
    for i, row in enumerate(strs):
        for j, char in enumerate(row):
            if char.isdigit():
                candidates = [int(char) - 1]
            else:
                candidates = [i for i in range(9)]
            for k in candidates:
                new_row = [0] * (81 * 4)
                new_row[i*9 + j] = 1    # each cell must be filled
                new_row[81 + i*9 + k] = 1   # unique value in each row, and
                new_row[81*2 + j*9 + k] = 1   # each col, and
                new_row[81*3 + (i//3 * 3 + j//3)*9 + k] = 1     # each block
                retval.append(new_row)
    return retval

def solution_to_matrix(solution: list[Link]) -> list[list[int]]:
    """Convert a dlx solution into Sudoku solution.
    >>> puzzle = ["...26.7.1",
    ...           "68..7..9.",
    ...           "19...45..",
    ...           "82.1...4.",
    ...           "..46.29..",
    ...           ".5...3.28",
    ...           "..93...74",
    ...           ".4..5..36",
    ...           "7.3.18..."]
    >>> matrix = puzzle_to_matrix(puzzle)
    >>> network = create_network(matrix)
    >>> for solution in search(network):
    ...     solution_mat = solution_to_matrix(solution)
    >>> target = [[4, 3, 5, 2, 6, 9, 7, 8, 1],
    ...           [6, 8, 2, 5, 7, 1, 4, 9, 3],
    ...           [1, 9, 7, 8, 3, 4, 5, 6, 2],
    ...           [8, 2, 6, 1, 9, 5, 3, 4, 7],
    ...           [3, 7, 4, 6, 8, 2, 9, 1, 5],
    ...           [9, 5, 1, 7, 4, 3, 6, 2, 8],
    ...           [5, 1, 9, 3, 2, 6, 8, 7, 4],
    ...           [2, 4, 8, 9, 5, 7, 1, 3, 6],
    ...           [7, 6, 3, 4, 1, 8, 2, 5, 9]]
    >>> all(i == j for i, j in zip(solution_mat, target))
    True
    """
    # initialise a 9 x 9 matrix
    mat = [[0] * 9 for _ in range(9)]

    for link in solution:
        # get puzzle index
        col = int(link.column.name)
        while col >= 81:
            link = link.right
            col = int(link.column.name)
        i, j = divmod(col, 9)

        # get solution
        link = link.right
        col = int(link.column.name)
        k = col - 81 - i*9 + 1
        mat[i][j] = k

    return mat


if __name__ == "__main__":
    import sys

    puzzle = read_puzzle(sys.argv[1])
    matrix = puzzle_to_matrix(puzzle)
    network = create_network(matrix)

    found = False
    for sol in search(network):
        sol_mat = solution_to_matrix(sol)
        for _ in sol_mat:
            print(_)
        print()
        found = True

    if not found:
        raise SolutionNotFound("Sudoku Puzzle has no solution.")
