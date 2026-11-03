#include <iostream>
#include <stdexcept>
#include <string>

class ServiceConfig {
public:
    explicit ServiceConfig(const std::string& endpoint) : endpoint_(endpoint) {
        if (endpoint_.empty()) {
            throw std::invalid_argument("endpoint must not be empty");
        }
    }

    const std::string& endpoint() const { return endpoint_; }

private:
    std::string endpoint_;
};

int main() {
    try {
        ServiceConfig config("");
        std::cout << config.endpoint() << '\n';
    } catch (const std::invalid_argument& error) {
        std::cerr << "configuration error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
