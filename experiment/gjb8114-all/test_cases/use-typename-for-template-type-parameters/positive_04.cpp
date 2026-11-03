template <typename T>
constexpr T default_value = T{};

int main() {
    return static_cast<int>(default_value<int>);
}
