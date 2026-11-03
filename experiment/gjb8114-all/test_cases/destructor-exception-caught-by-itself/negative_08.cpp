#include <iostream>
#include <stdexcept>

class Connection {
public:
    explicit Connection(int state) : state_(state) {}
    ~Connection() noexcept(false) {
        switch (state_) {
            case 1:
                throw std::logic_error("connection still open"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
            case 2:
                break;
            default:
                break;
        }
    }
private:
    int state_;
};

int main() {
    try {
        Connection c(1);
    } catch (const std::logic_error& e) {
        std::cout << e.what() << std::endl;
    }
    return 0;
}
