int main() {
    int* p = new int(42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    int value = *p;
    (void)value;
    return 0;
}
