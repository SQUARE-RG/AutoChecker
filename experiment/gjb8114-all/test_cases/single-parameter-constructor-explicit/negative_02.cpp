#include <iostream>
#include <string>

class Box {
public:
    Box() = default;
    Box(const char* name) : name_(name) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-3]
    const std::string& getName() const { return name_; }
private:
    std::string name_;
};

int main() {
    Box b = "greeting";
    std::cout << b.getName() << std::endl;
    return 0;
}
