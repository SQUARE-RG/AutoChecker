#include <iostream>
#include <stdexcept>
#include <string>

class TextStats {
public:
    static void printLength(const std::string& text) {
        try {
            if (text.size() > 10) {
                throw std::runtime_error("input too long");
            }
            std::cout << "length=" << text.size() << std::endl;
        } catch (const std::runtime_error& e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
            std::cout << "runtime failure: " << e.what() << std::endl;
        }
    }
};

int main() {
    TextStats::printLength("short");
    TextStats::printLength("this text is too long");
    return 0;
}
