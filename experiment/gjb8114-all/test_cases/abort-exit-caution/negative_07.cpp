#include <cstdlib>
#include <iostream>
#include <string>

class ServiceConfig {
public:
    explicit ServiceConfig(const std::string& endpoint) : endpoint_(endpoint) {
        if (endpoint_.empty()) {
            std::exit(EXIT_FAILURE);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
        }
    }

    const std::string& endpoint() const { return endpoint_; }

private:
    std::string endpoint_;
};

int main() {
    ServiceConfig config("");
    std::cout << config.endpoint() << '\n';
    return 0;
}
