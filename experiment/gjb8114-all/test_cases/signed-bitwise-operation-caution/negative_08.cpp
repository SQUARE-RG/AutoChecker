int main() {
    int flags = 0x55;
    flags ^= 0x0F; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-1]
    return flags;
}
