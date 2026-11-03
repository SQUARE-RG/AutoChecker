struct Flags {
    bool enabled;
};

int main() {
    int value = 42;
    int* ptr = &value;
    Flags flags{false};
    flags.enabled = ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    return 0;
}
