#include <cstdlib>
#include <exception>
#include <iostream>
#include <stdexcept>

int parse_port(int port) {
    if (port <= 0) {
        throw std::out_of_range("port must be positive");
    }
    return port;
}

int main() {
    try {
        int port = parse_port(0);
        std::cout << port << '\n';
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        std::abort();  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
    }
    return 0;
}
