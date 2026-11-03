int main() {
    int value = 16;
    const int shift = -2;
    int result = value >> shift; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return result;
}
