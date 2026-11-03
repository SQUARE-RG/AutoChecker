int main() {
    unsigned int flags = 0b1010u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return 0;
}
