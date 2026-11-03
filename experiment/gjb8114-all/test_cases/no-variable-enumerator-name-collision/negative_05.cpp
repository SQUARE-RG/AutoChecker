#include <utility>

enum Compass { east, west };

int main()
{
    std::pair<int, int> values{1, 2};
    auto [east, value] = values; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
    Compass dir = west;
    return east + value + static_cast<int>(dir);
}
