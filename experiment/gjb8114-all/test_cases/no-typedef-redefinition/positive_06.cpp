namespace app {
typedef int count_type;

count_type initial_count()
{
    return 3;
}
} // namespace app

int main()
{
    auto compute = []()
    {
        typedef float weight_type;
        weight_type value = 0.5f;
        return value;
    };

    app::count_type count = app::initial_count();
    auto weight = compute();
    return (count == 3 && weight > 0.0f) ? 0 : 1;
}
