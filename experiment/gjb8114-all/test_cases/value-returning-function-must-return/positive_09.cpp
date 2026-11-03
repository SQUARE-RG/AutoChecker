#include <type_traits>

template <typename T>
int normalize(T value)
{
    if constexpr (std::is_integral<T>::value)
    {
        return static_cast<int>(value);
    }
    else
    {
        return static_cast<int>(value * 2);
    }
}

int main()
{
    return normalize(3);
}
