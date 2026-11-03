int negative_06(int n) {
    if (n > 0) {
        return 1;
    } else {
        return -1;
    }
    return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
}
