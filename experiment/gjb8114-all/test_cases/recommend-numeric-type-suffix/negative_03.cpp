int main() {
    long double ldValue = 1.0e-5;
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
    (void)ldValue;
}
