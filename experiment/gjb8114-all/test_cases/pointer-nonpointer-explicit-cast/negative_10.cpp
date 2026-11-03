int main() {
    int* ptr = 0b0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    (void)ptr;
    return 0;
}
