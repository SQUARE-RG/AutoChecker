#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{3, 5, 7, 9};
    auto found = std::find(values.begin(), values.end(), 7);
    if (found != values.end()) {
        std::cout << *found << std::endl;
    }
    return 0;
}
