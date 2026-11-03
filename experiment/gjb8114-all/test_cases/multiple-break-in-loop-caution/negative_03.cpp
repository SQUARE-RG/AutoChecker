int clamp_or_match(int value, int limit) {
    int i = 0;
    while (i < limit) {
        if (i == value) {
            break;
        }
        if (i > value) {
            break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
        }
        ++i;
    }
    return i;
}
