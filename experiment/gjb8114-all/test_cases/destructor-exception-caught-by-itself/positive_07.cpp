#include <iostream>

class Processor {
public:
    explicit Processor(bool fail) : fail_(fail) {}
    ~Processor() noexcept(false) {
        try {
            try {
                if (fail_) {
                    throw 10;
                }
            } catch (int value) {
                std::cout << value << std::endl;
                throw 2.5;
            }
        } catch (double error) {
            std::cout << error << std::endl;
        }
    }
private:
    bool fail_;
};

int main() {
    Processor p(true);
    return 0;
}
