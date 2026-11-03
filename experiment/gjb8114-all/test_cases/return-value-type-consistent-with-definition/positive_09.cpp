long double convert_value()
{
    long double value = 2.5L;
    return value;
}

int main()
{
    long double result = convert_value();
    return (result > 0.0L) ? 0 : 1;
}
