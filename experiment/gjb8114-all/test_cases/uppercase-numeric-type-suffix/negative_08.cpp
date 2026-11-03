int main() {
    long double hex_value = 0x1.8p2l; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return 0;
}
