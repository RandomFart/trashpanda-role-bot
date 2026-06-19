from rank_logic import Rank, get_qualified_rank

TEST_RANKS = [
    Rank("Staff Sergeant", 1, 7),
    Rank("2nd Lieutenant", 2, 18),
    Rank("Captain", 3, 32),
    Rank("Colonel", 4, 53),
    Rank("General", 5, 81),
    Rank("Marshal", 6, 121),
    Rank("Grand Lord", 7, 177),
    Rank("Hero of the Sector", 8, 255),
    Rank("Admiral of Super Earth", 9, 365),
]


def test_rank(days, expected_name):
    rank = get_qualified_rank(days, TEST_RANKS)

    actual_name = rank.name if rank else None

    if actual_name == expected_name:
        print(f"PASS: {days} days -> {actual_name}")
    else:
        print(f"FAIL: {days} days -> {actual_name}, expected {expected_name}")


test_rank(0, None)
test_rank(6, None)
test_rank(7, "Staff Sergeant")
test_rank(17, "Staff Sergeant")
test_rank(18, "2nd Lieutenant")
test_rank(31, "2nd Lieutenant")
test_rank(32, "Captain")
test_rank(53, "Colonel")
test_rank(999, "Colonel")