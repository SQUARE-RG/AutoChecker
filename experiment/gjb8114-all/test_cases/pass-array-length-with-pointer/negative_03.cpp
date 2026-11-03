#include <cstddef>

void fillRows(int rows[][4]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 4; ++j) {
            rows[i][j] = i + j;
        }
    }
}

int main() {
    int grid[3][4] = {};
    fillRows(grid);
    return 0;
}
