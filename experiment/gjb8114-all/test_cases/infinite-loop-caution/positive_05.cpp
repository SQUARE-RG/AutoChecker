#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    int sum = 0;
    for (auto it = values.begin(); it != values.end(); ++it) {
        sum += *it;
    }
    std::cout << sum << std::endl;
    return 0;
}
