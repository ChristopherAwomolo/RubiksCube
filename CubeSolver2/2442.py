class RubiksNavigator:
    def __init__(self, solution):
        # Split the solution and expand '2' moves
        self.sol = self.expand_moves(solution.split(" "))
        self.current_position = 0
        self.previous_number = 0  # Start from step 0 (initial state)

    def expand_moves(self, moves):
        expanded_moves = []
        for move in moves:
            if move.endswith("2"):
                expanded_moves.append(move[0])
                expanded_moves.append(move[0])
            else:
                expanded_moves.append(move)
        return expanded_moves

    def get_opposite_step(self, step):
        """Returns the opposite of a given Rubik's cube move."""
        if len(step) == 1:
            return step + "'"
        elif step.endswith("'"):
            return step[0]
        else:
            return step[0]

    def compute_reverse_steps(self, steps):
        """Returns the reverse of a list of steps."""
        reversed_steps = []
        for step in reversed(steps):
            reversed_steps.append(self.get_opposite_step(step))
        return reversed_steps

    def navigate_solution(self, step_number):
        if step_number == 0:
            print("\nCurrent step: 0 -> Initial state (no moves executed)")
            print("Solution so far: [Initial state]")
            return self.current_position

        current_position = step_number - 1

        if current_position < 0 or current_position >= len(self.sol):
            print(
                f"Step {step_number} is out of bounds. Please enter a valid step number between 0 and {len(self.sol)}.")
            return self.current_position

        self.current_position = current_position
        print(f"\nCurrent step: {self.current_position + 1} -> {self.sol[self.current_position]}")
        print(f"Solution so far: {' '.join(self.sol[:self.current_position + 1])}")
        return self.current_position

    def start_navigation(self, number):
        if number == self.previous_number:
            print(f"Already at step {number}.")
        elif number == self.previous_number + 1:  # Equivalent to 'next'
            if self.current_position < len(self.sol) - 1:
                self.current_position += 1
                self.previous_number = self.current_position + 1
                self.navigate_solution(self.current_position + 1)
            else:
                print("You are already at the last step.")
        elif number == self.previous_number - 1:  # Equivalent to 'prev'
            if self.current_position > 0:
                reverse_steps = self.compute_reverse_steps(self.sol[:self.current_position])
                if reverse_steps:
                    print(f"Reversing the last steps: {' '.join(reverse_steps)}")
                self.current_position -= 1
                self.previous_number = self.current_position + 1
                self.navigate_solution(self.current_position + 1)
            else:
                print("You are already at the first step.")
        elif 0 <= number <= len(self.sol):  # Jump to specific step, including step 0
            if number > self.previous_number:
                difference = self.sol[self.current_position + 1:number]
                print(f"Jumping forward to step {number}: {' '.join(difference)}")
            elif number < self.previous_number:
                reverse_steps = self.compute_reverse_steps(self.sol[number-1:self.current_position + 1])
                print(f"Reversing to step {number}: {' '.join(reverse_steps)}")
            self.previous_number = number
            self.navigate_solution(number)
        else:
            print(f"Please enter a valid step number between 0 and {len(self.sol)}.")


# Example usage
solution = "R' U B' D' F2 B' U2 F2 R F' R2 B2 U2 L2 U2 D L2 F2 R2"
navigator = RubiksNavigator(solution)

for i in range(31):
    navigator.start_navigation(i)  # Start from the initial state (step 0)

