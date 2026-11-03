int main() {
    unsigned long long mask = 0xFF;
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
    (void)mask;
}
