int main() {
    int i = 0;
    while (i++ < 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    return 0;
}
