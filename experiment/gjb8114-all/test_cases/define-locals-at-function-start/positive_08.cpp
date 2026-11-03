#include <vector>

int totalEven(const std::vector<int>& data) {
    int total = 0;
    int offset = 0;
    for (int value : data) {
        if (value % 2 == 0) {
            total += value;
        }
    }
    offset = total / 2;
    return total + offset;
}

int main() {
    std::vector<int> data = {2, 4, 5, 6};
    return totalEven(data);
}
