int main() {
    int x = 0;
again:
    x = x + 1;
    if (x < 3) {
        goto again; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    }
    return 0;
}
