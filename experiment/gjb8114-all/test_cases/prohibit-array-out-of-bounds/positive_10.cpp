int main() {
    constexpr int rows = 2;
    constexpr int cols = 3;
    int mat[rows][cols] = {{0}};
    for (int c = 0; c < cols - 1; ++c) {
        mat[0][c + 1] = 1;
    }
    return 0;
}
