#include <optional>

std::optional<double> safe_divide(double a, double b)
{
    if (b == 0.0)
    {
        return std::nullopt;
    }
    return a / b;
}

int main()
{
    std::optional<double> result = safe_divide(1.0, 0.0);
    return result.has_value() ? 0 : 1;
}
