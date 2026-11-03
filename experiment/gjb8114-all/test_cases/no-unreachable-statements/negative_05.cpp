int negative_05(int n) {
    int result = 0;
    while (true) {
        result += n;
        if (result > 100) {
            return result;
        }
    }
    return result; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
}
