#include <iostream>

enum class Level { Low, Medium, High };

int main() {
    int outer = 2;
    switch (outer) {
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
            }
            break;
        }
        default:
            std::cout << "other\n";
            break;
    }
    return 0;
}
