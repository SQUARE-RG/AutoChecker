struct Holder {
    int*** ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
};

int main() {
    Holder h{};
    (void)h;
    return 0;
}
