int main() {
    int i = 0;
    goto inside; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    for (i = 0; i < 10; ++i) {
    inside:
        i += 2;
    }
    return 0;
}
