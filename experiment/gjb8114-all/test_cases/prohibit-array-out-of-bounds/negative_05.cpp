int main() {
    int matrix[3][4] = {};
    matrix[3][0] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    return 0;
}
