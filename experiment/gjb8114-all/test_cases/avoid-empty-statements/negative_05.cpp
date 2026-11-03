int main() {
    int total = 0;
    for (int i = 0; i < 4; ++i) ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    return total;
}
