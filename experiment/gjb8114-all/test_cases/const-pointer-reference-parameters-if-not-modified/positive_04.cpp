#include <vector>

int first_element(const std::vector<int>& values) {
    if (values.empty()) {
        return 0;
    }
    return values.front();
}
