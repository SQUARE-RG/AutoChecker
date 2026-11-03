int first_even_below(int limit) {
    int i = 0;
    int found = -1;
    while (i < limit) {
        if (i % 2 == 0) {
            found = i;
            break;
        }
        ++i;
    }
    return found;
}
