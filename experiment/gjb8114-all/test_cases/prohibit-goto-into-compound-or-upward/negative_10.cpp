int main() {
    int x = 0;
    if (x == 1) {
        x = 2;
    } else {
    L1:
        x = 3;
    }
    goto L1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    return 0;
}
