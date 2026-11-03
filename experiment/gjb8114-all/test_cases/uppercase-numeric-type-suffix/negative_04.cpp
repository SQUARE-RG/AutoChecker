int main() {
    unsigned long long value = 0xFFull; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return 0;
}
