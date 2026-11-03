int main() {
    int total = 100;
    int divisor = 7;
    int quotient = total / divisor; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    return quotient;
}
