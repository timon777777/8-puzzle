import csv
import heapq
import random
import statistics
import time


PUZZLE_COUNT = 100


# Function: Creates the standard goal state (0 to 8).
# Inputs: None
# Outputs: Tuple of numbers 0-8
def generate_goal_state():
    return tuple(range(9))


# Function: Checks if the puzzle can actually be solved by counting inversions.
# Inputs: State (tuple)
# Outputs: Boolean (True if solvable, False otherwise)
def is_solvable(state):
    inversions = 0

    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                inversions += 1

   # Puzzle is solvable only if inversions are even 
    return inversions % 2 == 0


# Function: Generates a list of unique, solvable random puzzles.
# Inputs: count (int), goal (tuple)
# Outputs: List of puzzle tuples
def generate_puzzles(count, goal):
    puzzles = []
    numbers = list(range(9))

    while len(puzzles) < count:
        random.shuffle(numbers)
        puzzle = tuple(numbers)

        # Ensure it's not the goal, not a duplicate, and is solvable
        if puzzle != goal and puzzle not in puzzles and is_solvable(puzzle):
            puzzles.append(puzzle)

    return puzzles


# Function: Hamming Heuristic. Counts how many tiles are in the wrong spot.
# Inputs: state (tuple)
# Outputs: Integer (number of misplaced tiles)
def hamming(state):
    misplaced = 0

    for i in range(9):
        if state[i] != 0 and state[i] != i:
            misplaced += 1

    return misplaced


# Function: Manhattan Heuristic. Calculates exact distance of tiles from their home.
# Inputs: state (tuple)
# Outputs: Integer (total distance)
def manhattan(state):
    distance = 0

    for i in range(9):
        number = state[i]
        if number != 0:
            target = number
            # Uses 1D array math (// for row, % for column) to find distance
            distance += abs(i // 3 - target // 3)          
            distance += abs(i % 3 - target % 3)

    return distance


# Function: The A* Search Algorithm to find the shortest path.
# Inputs: start (tuple), goal (tuple), heuristic (function)
# Outputs: steps (int), expanded nodes (int), runtime (float)
def a_star(start, goal, heuristic):
    start_time = time.perf_counter()
    queue = [(heuristic(start), 0, start)]
    best_steps = {start: 0}
    expanded = 0

    while queue:
        _, negative_steps, state = heapq.heappop(queue)
        steps = -negative_steps

        # Skip if we already found a faster way to this state
        if steps != best_steps[state]:
            continue

        # If we reached the goal, stop and return results
        if state == goal:
            runtime = time.perf_counter() - start_time
            return steps, expanded, runtime

        expanded += 1
        
        # Find the empty space (0)
        empty = state.index(0)
        row, column = divmod(empty, 3)
        positions = []

        # Check valid moves (up, down, left, right)
        if row > 0:
            positions.append(empty - 3)
        if row < 2:
            positions.append(empty + 3)
        if column > 0:
            positions.append(empty - 1)
        if column < 2:
            positions.append(empty + 1)

        # Create new states for each valid move
        for position in positions:
            new_state = list(state)
            new_state[empty], new_state[position] = new_state[position], new_state[empty]
            new_state = tuple(new_state)
            new_steps = steps + 1

            # If this is the best path to this new state, save it
            if new_steps < best_steps.get(new_state, float('inf')):
                best_steps[new_state] = new_steps
                priority = new_steps + heuristic(new_state)
                heapq.heappush(queue, (priority, -new_steps, new_state))

    raise RuntimeError('No solution found')


# Function: Prints the puzzle in a 3x3 grid format.
# Inputs: state (tuple)
# Outputs: Prints to console
def print_board(state):
    for i in range(0, 9, 3):
        print(' '.join('_' if tile == 0 else str(tile) for tile in state[i:i + 3]))


# Function: Runs the 100 puzzles, saves data to CSV, and prints statistics.
# Inputs: None
# Outputs: Creates CSV file and prints results to console
def main():
    goal = generate_goal_state()
    puzzles = generate_puzzles(PUZZLE_COUNT, goal)

    hamming_times = []
    manhattan_times = []
    hamming_nodes = []
    manhattan_nodes = []

    # Open CSV file to save individual results
    with open('8_puzzle_results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'puzzle', 'start_state', 'heuristic', 'solution_length', 'expanded_nodes',
            'runtime_seconds'
        ])

        # Solve all 100 puzzles with both heuristics
        for number, puzzle in enumerate(puzzles, start=1):
            h_steps, h_nodes, h_time = a_star(puzzle, goal, hamming)
            m_steps, m_nodes, m_time = a_star(puzzle, goal, manhattan)

            # Safety check: both heuristics should find the exact same shortest path
            if h_steps != m_steps:
                raise RuntimeError('Heuristics returned different solution lengths')

            # Store data for statistics
            hamming_times.append(h_time)
            manhattan_times.append(m_time)
            hamming_nodes.append(h_nodes)
            manhattan_nodes.append(m_nodes)

            # Write to CSV
            start_state = ' '.join(map(str, puzzle))
            writer.writerow([number, start_state, 'Hamming', h_steps, h_nodes, h_time])
            writer.writerow([number, start_state, 'Manhattan', m_steps, m_nodes, m_time])

    # Print sample output and final statistics table
    print('Goal state:')
    print_board(goal)
    print('\nExample start state:')
    print_board(puzzles[0])
    print('Solvable:', is_solvable(puzzles[0]))
    print('\nResults for 100 puzzles:')
    print(f"{'Heuristic':<12} {'Mean time (s)':>14} {'Std time (s)':>14} "
          f"{'Mean nodes':>12} {'Std nodes':>12}")

    for name, times, nodes in [
        ('Hamming', hamming_times, hamming_nodes),
        ('Manhattan', manhattan_times, manhattan_nodes),
    ]:
        print(f'{name:<12} {statistics.mean(times):>14.6f} {statistics.stdev(times):>14.6f} '
              f'{statistics.mean(nodes):>12.2f} {statistics.stdev(nodes):>12.2f}')

    print('\nIndividual results saved in 8_puzzle_results.csv')


if __name__ == '__main__':
    main()
