#include <vector>
#include <iostream>

int count_even(const std::vector<int>& values) {
    int count = 0;
    for (auto it = values.begin(); it != values.end(); ++it) {
        if (*it == 0) {
            continue;
        }
        if (*it % 2 == 0) {
            ++count;
        } else {
            // odd numbers are handled normally here
        }
    }
    return count;
}

int main() {
    std::vector<int> values{1, 2, 0, 4};
    std::cout << count_even(values) << std::endl;
    return 0;
}
