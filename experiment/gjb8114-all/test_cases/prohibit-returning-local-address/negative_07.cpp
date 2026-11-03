int* get_addr(int x) {
    return &x; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    return 0;
}
