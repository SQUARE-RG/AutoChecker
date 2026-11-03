#include <utility>

int main() {
    std::pair<int, int> p{0, 1};
    auto [count1, label] = p;
    return count1 + label;
}
