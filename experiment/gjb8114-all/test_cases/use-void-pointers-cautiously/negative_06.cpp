#include <iostream>

int main() {
    char text[] = "hello";
    void* erased = reinterpret_cast<void*>(text); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    char* mutable_text = static_cast<char*>(erased);
    mutable_text[0] = 'H';
    std::cout << text << '\n';
    return 0;
}
