#include <iostream>
#include <stdexcept>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 3, 4, 5};
    int total = 0;
    for (std::size_t i = 0; i < values.size(); ++i) {
        try {
            if (values[i] == 0) {
                continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
            }
            if (values[i] < 0) {
                throw std::runtime_error("negative value");
            }
            total += values[i];
        } catch (const std::runtime_error& e) {
            std::cerr << e.what() << '\n';
            continue;
        }
    }
    std::cout << total << '\n';
    return 0;
}
