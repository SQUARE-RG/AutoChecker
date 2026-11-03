int main() {
    int* p = new int[4]{1, 2, 3, 4}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    int sum = p[0] + p[1];
    (void)sum;
    return 0;
}
