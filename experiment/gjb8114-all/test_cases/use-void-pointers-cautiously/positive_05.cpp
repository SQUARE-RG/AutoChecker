#include <any>
#include <iostream>
#include <string>

int main() {
    std::any payload = 42;
    int value = std::any_cast<int>(payload);

    std::any message = std::string("typed");
    std::string text = std::any_cast<std::string>(message);

    std::cout << value << ' ' << text << '\n';
    return 0;
}
