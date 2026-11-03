static int unused_helper() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
    return 42;
}

int main() {
    return 0;
}
