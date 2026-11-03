#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

template <typename T>
class Parser {
public:
    explicit Parser(T defaultValue) : fallback(defaultValue) {}

    T parse(bool ok, T const& candidate) const
    {
        try {
            if (!ok) {
                throw std::runtime_error("unparsable input");
            }
            return candidate;
        } catch (std::runtime_error const& e) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
            std::cout << "fallback after: " << e.what() << "\n";
            return fallback;
        }
    }

private:
    T fallback;
};

int main()
{
    Parser<int> ints(0);
    std::cout << ints.parse(false, 42) << "\n";
    std::cout << ints.parse(true, 7) << "\n";

    Parser<std::string> texts(std::string("unknown"));
    std::cout << texts.parse(false, std::string("ok")) << "\n";
    std::cout << texts.parse(true, std::string("value")) << "\n";
    return 0;
}
