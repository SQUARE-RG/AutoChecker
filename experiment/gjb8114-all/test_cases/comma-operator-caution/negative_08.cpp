int main() {
    int x = 0;
    int y = 0;
    (x = 1, y = 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    return x + y;
}
