import heapq

def manhattan_distance(state, goal):
    distance = 0
    size = int(len(state) ** 0.5)
    for i, value in enumerate(state):
        if value != 0:
            goal_index = goal.index(value)
            distance += abs(i // size - goal_index // size) + abs(i % size - goal_index % size)
    return distance

def get_neighbors(state):
    size = int(len(state) ** 0.5)
    zero_index = state.index(0)
    moves = []
    x, y = zero_index % size, zero_index // size

    directions = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    for move, (dx, dy) in directions.items():
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < size and 0 <= new_y < size:
            new_index = new_y * size + new_x
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            moves.append((move, tuple(new_state)))
    return moves

def a_star(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start, []))
    explored = set()

    while frontier:
        _, current_state, path = heapq.heappop(frontier)
        if current_state == goal:
            return path
        explored.add(current_state)
        for move, neighbor in get_neighbors(current_state):
            if neighbor not in explored:
                cost = len(path) + 1 + manhattan_distance(neighbor, goal)
                heapq.heappush(frontier, (cost, neighbor, path + [move]))
    return None

def is_solvable(state, size):
    inversion_count = 0
    state_wo_zero = [x for x in state if x != 0]
    for i in range(len(state_wo_zero)):
        for j in range(i+1, len(state_wo_zero)):
            if state_wo_zero[i] > state_wo_zero[j]:
                inversion_count += 1
    if size % 2 != 0:  # size impar
        return inversion_count % 2 == 0
    else:
        zero_row_from_bottom = size - (state.index(0) // size)
        return (inversion_count + zero_row_from_bottom) % 2 == 0
