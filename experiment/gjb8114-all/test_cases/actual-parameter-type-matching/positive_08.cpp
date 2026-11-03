int main()
{
    auto scale = [](double factor) { return factor; };
    double input = 1.0;
    double result = scale(input);
    (void)result;
    return 0;
}
