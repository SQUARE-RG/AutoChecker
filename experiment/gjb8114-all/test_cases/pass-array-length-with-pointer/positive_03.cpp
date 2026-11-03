#include <cstddef>

void fillRows(int rows[][4], std::size_t rowCount)
{
    for (std::size_t i = 0; i < rowCount; ++i) {
        for (int j = 0; j < 4; ++j) {
            rows[i][j] = static_cast<int>(i) + j;
        }
    }
}

int main() {
    int grid[3][4] = {};
    fillRows(grid, sizeof(grid) / sizeof(grid[0]));
    return 0;
}
