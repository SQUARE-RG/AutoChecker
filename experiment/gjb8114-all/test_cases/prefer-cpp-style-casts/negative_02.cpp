int main() {
    int value = 42;
    void* erased = &value;
    int* restored = (int*)erased; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    return *restored;
}
