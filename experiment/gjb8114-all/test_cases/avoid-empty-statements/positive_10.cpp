#include <vector>

int main() {
    std::vector<int> values{1, 2, 3};
    int sum = 0;
    for (int value : values) {
        sum += value;
    }
    return sum;
}
