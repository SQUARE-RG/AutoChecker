int main() {
    int const arr[2] = {1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
    (void)arr;
    return 0;
}
