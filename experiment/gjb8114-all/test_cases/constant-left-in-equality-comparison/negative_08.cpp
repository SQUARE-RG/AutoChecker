int main() {
    unsigned int flags = 0x10u;
    const unsigned int mask = 0x10u;
    if ((flags & mask) == 0x10u) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        return 1;
    }
    return 0;
}
