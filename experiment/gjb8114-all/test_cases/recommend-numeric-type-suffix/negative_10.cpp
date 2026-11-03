int main() {
    float ratio = 0x1.8p1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-4]
    return static_cast<int>(ratio);
}
