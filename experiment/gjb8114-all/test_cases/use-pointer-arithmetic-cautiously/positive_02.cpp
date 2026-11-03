#include <iostream>
#include <vector>

int main() {
    std::vector<int> values = {2, 4, 6};
    int sum = values.at(0) + values.at(1);
    std::cout << sum << '\n';
    return 0;
}
