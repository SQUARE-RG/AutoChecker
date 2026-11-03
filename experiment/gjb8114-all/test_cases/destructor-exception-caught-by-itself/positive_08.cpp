#include <iostream>
#include <stdexcept>

class Connection {
public:
    explicit Connection(int state) : state_(state) {}
    ~Connection() noexcept(false) {
        try {
            switch (state_) {
                case 1:
                    throw std::logic_error("connection still open");
                case 2:
                    break;
                default:
                    break;
            }
        } catch (const std::logic_error& e) {
            std::cout << e.what() << std::endl;
        }
    }
private:
    int state_;
};

int main() {
    Connection c(1);
    return 0;
}
