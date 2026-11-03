int main() {
    int count = 0;
    for (int i = 0; i < 3; ++i) {
L_again:
        if (i > 0) {
            ++count;
            if (count > 1) {
                continue;
            }
            goto L_again;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
        }
    }
    return 0;
}
