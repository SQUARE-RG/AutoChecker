int main() {
    unsigned int x = 2U;
    unsigned int y = x << -1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-7]
    return static_cast<int>(y);
}
