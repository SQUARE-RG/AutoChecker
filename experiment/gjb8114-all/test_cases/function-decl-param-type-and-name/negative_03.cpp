int compute(int value, long); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

int main() {
    int result = compute(10, 20L);
    return result;
}

int compute(int value, long factor) {
    return value + static_cast<int>(factor);
}
