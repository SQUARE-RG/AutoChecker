#include <iostream>
struct BaseError {
    virtual ~BaseError() = default;
    virtual int code() const { return 1; }
};
struct DerivedError : BaseError {
    int code() const override { return 2; }
};
int main() {
    try {
        DerivedError err;
        throw err;
    } catch (BaseError e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
        std::cout << e.code();
    }
    return 0;
}
