#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{10, 20, 30, 40, 50};
    for (auto it = values.rbegin(); it != values.rend(); ++it) {
        std::cout << *it << std::endl;
    }
    return 0;
}
