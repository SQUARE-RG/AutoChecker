#include <variant>
#include <string>

struct DivError {
    std::string message;
};

using DivResult = std::variant<double, DivError>;

class Divider {
public:
    DivResult divide(double a, double b) const {
        if (b == 0.0) {
            return DivError{"division by zero"};
        }
        return a / b;
    }
};

int main() {
    Divider d;
    DivResult r = d.divide(1.0, 0.0);
    return std::holds_alternative<DivError>(r) ? 1 : 0;
}
