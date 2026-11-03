#include <memory>
#include <iostream>

int main() {
    std::unique_ptr<int> owner(new int(42));
    int* raw = owner.release(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    std::cout << *raw << '\n';
    // 忘记 delete raw，造成泄漏
    return 0;
}
