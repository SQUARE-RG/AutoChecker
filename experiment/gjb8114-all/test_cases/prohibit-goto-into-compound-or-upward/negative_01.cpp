int main() {
    int x = 0;
    goto inside; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    if (x == 0) {
    inside:
        x = 1;
    }
    return 0;
}
