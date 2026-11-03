int positive_05(int a, int b) {
    if (a > 0) {
        return (b > 0) ?
            (a > b) ?
                (b < 0) ?
                    (a < b) ?
                        (a + b > 0) ?
                            (a - b > 0) ?
                                1 : 2
                            : 3
                        : 4
                    : 5
                : 6
            : 7;
    }
    return 0;
}
