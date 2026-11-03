#include <iostream>
#include <string>
#include <variant>

using Value = std::variant<int, double, std::string>;

void printValue(const Value& v) {
    std::visit([](const auto& x) { std::cout << x << std::endl; }, v);
}

int main() {
    Value a = 7;
    Value b = 3.14;
    Value c = std::string("hello");
    printValue(a);
    printValue(b);
    printValue(c);
    return 0;
}
