int negative_05(int a, int b) {
    if (a > 0) {
        return (b > 0) ?
            (a > b) ?
                (b < 0) ?
                    (a < b) ?
                        (a + b > 0) ?
                            (a - b > 0) ?
                                (a == b) ? // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                    1 : 2
                                : 3
                            : 4
                        : 5
                    : 6
                : 7
            : 8;
    }
    return 0;
}
