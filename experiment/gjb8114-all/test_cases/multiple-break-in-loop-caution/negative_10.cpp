int process(int limit) {
    int i = 0;
    while (i < limit) {
        try {
            if (i == 2) {
                break;
            }
            if (i == 4) {
                break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
            }
            if (i == 6) {
                throw 42;
            }
        } catch (int) {
            return -1;
        }
        ++i;
    }
    return i;
}
