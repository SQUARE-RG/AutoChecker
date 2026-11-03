int main() {
    int value = 100;
    int divisor = 5;
    value /= divisor; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    return value;
}
