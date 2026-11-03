int main() {
    int result = 1;
    auto compute = []() {
        int result = 5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        return result;
    };
    result = compute();
    return result - 5;
}
