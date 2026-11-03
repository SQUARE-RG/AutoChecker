int main() {
    int a = 0, b = 4.25; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    a = a + b;
    return a;
}
