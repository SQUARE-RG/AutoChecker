int process(int limit) {
    int i = 0;
    while (i < limit) {
        try {
            if (i == 3) {
                break;
            }
            if (i == 5) {
                throw 42;
            }
        } catch (int) {
            return -1;
        }
        ++i;
    }
    return i;
}
