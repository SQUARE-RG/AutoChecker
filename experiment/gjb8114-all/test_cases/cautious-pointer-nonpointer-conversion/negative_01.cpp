int main() {
    int value = 0;
    int* ptr = &value;
    bool has_value = ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-4]
    return has_value ? 0 : 1;
}
