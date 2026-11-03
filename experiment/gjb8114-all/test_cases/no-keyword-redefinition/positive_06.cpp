int main()
{
    auto increment = [](unsigned int input_value) {
        return input_value + 1U;
    };

    return static_cast<int>(increment(0U));
}
