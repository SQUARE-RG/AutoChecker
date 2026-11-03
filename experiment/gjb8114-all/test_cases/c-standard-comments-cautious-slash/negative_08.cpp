int compute(int value) {
    return value + 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]
}

int main() {
    int result = compute(41);
    return result == 42 ? 0 : 1;
}
