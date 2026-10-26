import csv
import heapq
import random
import statistics
import time


PUZZLE_COUNT = 100


def generate_goal_state():
    return tuple(range(9))


def is_solvable(state):
    inversions = 0

    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                inversions += 1

    return inversions % 2 == 0


def generate_puzzles(count, goal):
    puzzles = []
    numbers = list(range(9))

    while len(puzzles) < count:
        random.shuffle(numbers)
        puzzle = tuple(numbers)

        if puzzle != goal and puzzle not in puzzles and is_solvable(puzzle):
            puzzles.append(puzzle)

    return puzzles


def hamming(state):
    misplaced = 0

    for i in range(9):
        if state[i] != 0 and state[i] != i:
            misplaced += 1

    return misplaced


def manhattan(state):
    distance = 0

    for i in range(9):
        number = state[i]
        if number != 0:
            target = number
            distance += abs(i // 3 - target // 3)
            distance += abs(i % 3 - target % 3)

    return distance


def a_star(start, goal, heuristic):
    start_time = time.perf_counter()
    queue = [(heuristic(start), 0, start)]
    best_steps = {start: 0}
    expanded = 0

    while queue:
        _, negative_steps, state = heapq.heappop(queue)
        steps = -negative_steps

        if steps != best_steps[state]:
            continue

        if state == goal:
            runtime = time.perf_counter() - start_time
            return steps, expanded, runtime

        expanded += 1
        empty = state.index(0)
        row, column = divmod(empty, 3)
        positions = []

        if row > 0:
            positions.append(empty - 3)
        if row < 2:
            positions.append(empty + 3)
        if column > 0:
            positions.append(empty - 1)
        if column < 2:
            positions.append(empty + 1)

        for position in positions:
            new_state = list(state)
            new_state[empty], new_state[position] = new_state[position], new_state[empty]
            new_state = tuple(new_state)
            new_steps = steps + 1

            if new_steps < best_steps.get(new_state, float('inf')):
                best_steps[new_state] = new_steps
                priority = new_steps + heuristic(new_state)
                heapq.heappush(queue, (priority, -new_steps, new_state))

    raise RuntimeError('No solution found')


def print_board(state):
    for i in range(0, 9, 3):
        print(' '.join('_' if tile == 0 else str(tile) for tile in state[i:i + 3]))


def main():
    goal = generate_goal_state()
    puzzles = generate_puzzles(PUZZLE_COUNT, goal)

    hamming_times = []
    manhattan_times = []
    hamming_nodes = []
    manhattan_nodes = []

    with open('8_puzzle_results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'puzzle', 'start_state', 'heuristic', 'solution_length', 'expanded_nodes',
            'runtime_seconds'
        ])

        for number, puzzle in enumerate(puzzles, start=1):
            h_steps, h_nodes, h_time = a_star(puzzle, goal, hamming)
            m_steps, m_nodes, m_time = a_star(puzzle, goal, manhattan)

            if h_steps != m_steps:
                raise RuntimeError('Heuristics returned different solution lengths')

            hamming_times.append(h_time)
            manhattan_times.append(m_time)
            hamming_nodes.append(h_nodes)
            manhattan_nodes.append(m_nodes)

            start_state = ' '.join(map(str, puzzle))
            writer.writerow([number, start_state, 'Hamming', h_steps, h_nodes, h_time])
            writer.writerow([number, start_state, 'Manhattan', m_steps, m_nodes, m_time])

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
