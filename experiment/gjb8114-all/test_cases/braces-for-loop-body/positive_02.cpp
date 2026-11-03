#include <iostream>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3};
    for (int value : values)
    {
        std::cout << value << ' ';
    }
    std::cout << '\n';
    return 0;
}
