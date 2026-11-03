#include <utility>

int combine(int x) {
    int y = x + 1;
    std::pair<int, int> values{y, y * 2};
    auto [a, b] = values;
    int result = a + b;
    return result;
}

int main() {
    return combine(3) == 12 ? 0 : 1;
}
