int main() {
    int i = 0;
    do {
        register int total = i + 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
        (void)total;
        ++i;
    } while (i < 3);
    return 0;
}
