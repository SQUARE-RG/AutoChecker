#include <iostream>

class AbstractBase {
public:
    AbstractBase() : kind(0) {}
    virtual ~AbstractBase() = default;
    virtual void f() = 0;
    AbstractBase& operator=(AbstractBase const&) = default; // CHECK-MESSAGES: :[[@LINE]]:5: warning: abstract class copy assignment operator must be protected or private [ucassaat-r-2-1-4]
private:
    int kind;
};

int main() {
    return 0;
}
