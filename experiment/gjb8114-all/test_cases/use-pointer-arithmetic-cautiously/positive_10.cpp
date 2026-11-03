#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{10, 20, 30, 40};
    for (auto it = values.cbegin(); it != values.cend(); ++it) {
        std::cout << *it << '\n';
    }
    return 0;
}
