# Marking errors - updated by Claude Code after analysis
# Format: {page_index: [(question_num, x, y), ...]}
# Page index is 0-based (page 1 = index 0)

ERRORS = {
    # B161a (page 0) - Q5: 150-50=106 (should be 100)
    0: [(5, 180, 485)],

    # B167a (page 12) - Q6, Q8
    12: [(6, 460, 285), (8, 460, 485)],

    # B168a (page 14) - Q5: 257-38=119 (should be 219)
    14: [(5, 460, 185)],

    # B168b (page 15) - Q12: 354-26=338 (should be 328)
    15: [(12, 180, 385)],

    # B170a (page 18) - Q3: 253-36=227 (should be 217)
    18: [(3, 180, 385)],
}

# Student info
STUDENT_NAME = "Gemma"
WORKSHEET_DATE = "14 January 2026"
TOTAL_QUESTIONS = 173
CORRECT_ANSWERS = 167
