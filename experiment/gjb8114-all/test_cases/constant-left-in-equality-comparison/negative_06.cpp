bool has_value(const int* ptr) {
    return ptr != nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
}

int main() {
    int value = 0;
    return has_value(&value) ? 0 : 1;
}
