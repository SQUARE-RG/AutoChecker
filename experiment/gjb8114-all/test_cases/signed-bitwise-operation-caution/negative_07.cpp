int main() {
    short value = 1024;
    value >>= 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    return value;
}
