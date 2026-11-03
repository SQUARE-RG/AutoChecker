int main() {
    int i = 0;
    while (i < 3) {
    L0:
        ++i;
        goto L0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    }
    return 0;
}
