// Negative: dynamically allocated single object is never released.

int main() {
    int* value = new int(42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    int result = *value;
    return result;
}
