#include <cstddef>
#include <iostream>

struct S {
    int i;
};

int main() {
    std::nullptr_t n = nullptr;
    std::nullptr_t* p = &n;
    S* s = reinterpret_cast<S*>(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)s;
    std::cout << "done" << std::endl;
    return 0;
}
