int main() {
    constexpr int n = 4;
    int a[n] = {0};
    for (int i = 0; i < n; ++i) {
        a[i + 1] = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    }
    return 0;
}
