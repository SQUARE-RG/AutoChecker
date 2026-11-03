int main()
{
    auto compute = []() -> unsigned int
    {
        unsigned int x = 0U;
#define LAMBDA_DEF 3U
        x = x + LAMBDA_DEF;
#undef LAMBDA_DEF
        return x;
    };

    return static_cast<int>(compute());
}
