int main() {
    unsigned int value = 0b1010; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
    return static_cast<int>(value);
}
