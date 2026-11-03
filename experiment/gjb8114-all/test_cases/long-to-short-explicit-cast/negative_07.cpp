int main() {
    long sourceValue = 123456L;
    short targetValue = 0;
    targetValue = sourceValue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return static_cast<int>(targetValue);
}
