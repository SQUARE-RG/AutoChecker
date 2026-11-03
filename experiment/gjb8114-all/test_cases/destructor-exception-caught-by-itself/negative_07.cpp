#include <iostream>

class Processor {
public:
    explicit Processor(bool fail) : fail_(fail) {}
    ~Processor() noexcept(false) {
        try {
            if (fail_) {
                throw 10;
            }
        } catch (int value) {
            std::cout << value << std::endl;
            throw 2.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
        }
    }
private:
    bool fail_;
};

int main() {
    try {
        Processor p(true);
    } catch (double error) {
        std::cout << error << std::endl;
    }
    return 0;
}
