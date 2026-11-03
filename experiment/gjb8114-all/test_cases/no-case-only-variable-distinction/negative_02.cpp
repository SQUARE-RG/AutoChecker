int compute(
    int Value,
    int value // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-8]
) {
    return Value + value;
}

int main() {
    return compute(1, 2);
}
