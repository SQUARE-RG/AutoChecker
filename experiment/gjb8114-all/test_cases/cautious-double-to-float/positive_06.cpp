#include <iostream>
#include <vector>

int main() {
    std::vector<double> values{1.25, 2.5};
    for (double value : values) {
        std::cout << value << std::endl;
    }
    return 0;
}
