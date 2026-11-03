#include <cmath>
#include <vector>

int main() {
    std::vector<int> values;
    double raw = 9.876;
    values.push_back(static_cast<int>(std::round(raw)));
    return values[0];
}
