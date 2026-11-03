int main() {
    constexpr int rows = 2;
    constexpr int cols = 3;
    int mat[rows][cols] = {{0}};
    for (int c = 0; c < cols; ++c) {
        mat[0][c + 1] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    }
    return 0;
}
