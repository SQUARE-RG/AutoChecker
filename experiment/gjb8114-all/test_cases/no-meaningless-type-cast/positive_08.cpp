double half(int value)
{
    return static_cast<double>(value) / 2;
}

int main()
{
    double result = half(5);
    return result > 0.0 ? 0 : 1;
}
