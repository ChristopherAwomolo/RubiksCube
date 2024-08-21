def get_opposite_moves(sequence):
    # Split the sequence into individual moves
    moves = sequence.split()

    # Initialize the opposite sequence list
    opposite_sequence = []

    # Iterate over the reversed list of moves
    for move in reversed(moves):
        face = move[0]  # First character is the face (R, U, F, etc.)
        if len(move) == 1:
            # If the move is just a single face (e.g., "R")
            opposite_sequence.append(face + "'")
        elif move[1] == "'":
            # If the move is a prime move (e.g., "R'")
            opposite_sequence.append(face)
        elif move[1] == "2":
            # If the move is a double turn (e.g., "R2")
            opposite_sequence.append(face + "' " + face + "'")

    # Join the moves into a single string and return
    return ' '.join(opposite_sequence)

# Example usage:
sequence = "R' U B' D' F2 B' U2 F2 R F' R2 B2 U2 L2 U2 D L2 F2 R2"
opposite_sequence = get_opposite_moves(sequence)
print(opposite_sequence)