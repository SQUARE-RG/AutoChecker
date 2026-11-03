int main() {
    int x = 4;
    int y = -1;
    auto combine = [](int a, int b) {
        return (a > 0) | (b < 0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
    };
    bool result = combine(x, y);
    return result ? 0 : 1;
}
