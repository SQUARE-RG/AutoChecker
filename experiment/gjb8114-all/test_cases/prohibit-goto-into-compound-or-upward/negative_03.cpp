int main() {
    int i = 0;
    goto L_in_loop;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    while (i < 3) {
L_in_loop:
        ++i;
        break;
    }
    return 0;
}
