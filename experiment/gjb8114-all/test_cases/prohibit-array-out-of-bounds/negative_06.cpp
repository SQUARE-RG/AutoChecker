int main() {
    int a[5] = {};
    for (int i = 5; i >= 0; --i) {
        a[i] = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    }
    return 0;
}
