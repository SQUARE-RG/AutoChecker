int first_divisible_by_three(const int (&values)[5]) {
    int found = -1;
    for (int value : values) {
        if (value % 3 == 0) {
            found = value;
            break;
        }
    }
    return found;
}
