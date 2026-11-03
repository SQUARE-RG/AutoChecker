#include <cstddef>
#include <iostream>
#include <vector>

bool find_value(const std::vector<std::vector<int>>& matrix, int target) {
    bool found = false;
    for (std::size_t row = 0; row < matrix.size(); ++row) {
        for (std::size_t col = 0; col < matrix[row].size(); ++col) {
            if (matrix[row][col] == target) {
                found = true;
                break;
            }
        }
        if (found) {
            break;
        }
    }
    return found;
}

int main() {
    std::vector<std::vector<int>> matrix = {{1, 2}, {3, 4}};
    std::cout << std::boolalpha << find_value(matrix, 3) << '\n';
    return 0;
}
