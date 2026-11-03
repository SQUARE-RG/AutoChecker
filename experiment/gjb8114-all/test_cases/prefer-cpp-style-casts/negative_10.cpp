int produce() {
    return 42;
}

int main() {
    (void)produce(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    return 0;
}
