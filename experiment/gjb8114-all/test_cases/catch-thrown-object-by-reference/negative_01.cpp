#include <iostream>

class MyError {
public:
    explicit MyError(int code) : code_(code) {}
    int getCode() const { return code_; }
private:
    int code_;
};

int main() {
    try {
        throw new MyError(42);
    } catch (MyError *e) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
        std::cout << e->getCode() << std::endl;
        delete e;
    }
    return 0;
}
