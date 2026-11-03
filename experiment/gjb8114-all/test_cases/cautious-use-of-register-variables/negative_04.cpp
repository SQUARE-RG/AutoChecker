int compute(int value) {
    auto multiply = [](int x) {
        register int result = x * 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
        return result;
    };
    return multiply(value);
}

int main() {
    return compute(3);
}
