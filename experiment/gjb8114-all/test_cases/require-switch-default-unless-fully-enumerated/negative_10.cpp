#include <iostream>

enum class Level { Low, Medium, High };

int main() {
    int outer = 2;
    switch (outer) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
        case 0:
            std::cout << "zero\n";
            break;
        case 1: {
            Level level = Level::Low;
            switch (level) {
                case Level::Low:
                    std::cout << "low\n";
                    break;
                case Level::Medium:
                    std::cout << "medium\n";
                    break;
                case Level::High:
                    std::cout << "high\n";
                    break;
                default:
                    std::cout << "unknown level\n";
                    break;
            }
            break;
        }
    }
    return 0;
}
