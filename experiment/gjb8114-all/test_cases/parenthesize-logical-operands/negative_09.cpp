int main() {
    unsigned int flags = 0x21;
    unsigned int threshold = 0x40;
    bool result = false;
    if (flags << 1 > threshold) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-5]
    {
        result = true;
    }
    return result ? 0 : 1;
}
