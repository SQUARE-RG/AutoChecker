int main() {
    auto value = 0x1.8p3f; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-5]
    return value == 0.0F ? 0 : 1;
}
