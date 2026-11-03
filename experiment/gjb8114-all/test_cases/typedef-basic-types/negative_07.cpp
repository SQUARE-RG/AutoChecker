long GetValue() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    return 100L;
}

int main() {
    (void)GetValue();
    return 0;
}
