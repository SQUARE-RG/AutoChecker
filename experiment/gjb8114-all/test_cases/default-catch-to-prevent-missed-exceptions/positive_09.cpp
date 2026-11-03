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
        } catch (const std::runtime_error& e) {
            std::cout << "runtime failure: " << e.what() << std::endl;
        } catch (...) {
            std::cout << "unknown failure" << std::endl;
        }
    }
};

int main() {
    TextStats::printLength("short");
    TextStats::printLength("this text is too long");
    return 0;
}
