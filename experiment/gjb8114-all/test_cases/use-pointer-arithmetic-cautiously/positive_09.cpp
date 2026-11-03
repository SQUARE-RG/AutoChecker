#include <algorithm>
#include <iostream>
#include <iterator>
#include <vector>

int main() {
    std::vector<int> values{10, 20, 30, 40};
    std::copy(values.begin(), values.end(),
              std::ostream_iterator<int>(std::cout, "\n"));
    return 0;
}
